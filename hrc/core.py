import asyncio
import json
import pkgutil
import signal
import sys
import threading
import time
from collections import defaultdict
from contextlib import AsyncExitStack
from itertools import chain
from pathlib import Path
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
    overload,
)

from pydantic import ValidationError, create_model

from .config import ConfigModel, MainConfig, RuleConfig
from .dependencies import solve_dependencies
from .log import logger
from .rule import Rule, RuleLoadType
from .event import Event
from .typing import CoreHook, EventHook, EventT
from .utils import (
    ModulePathFinder,
    get_classes_from_module_name,
    is_config_class,
    samefile,
    wrap_get_func,
)
from .exceptions import (
    StopException,
    SkipException,
    GetEventTimeout,
    LoadModuleError
)


if sys.version_info >= (3, 11):  # pragma: no cover
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib

HANDLED_SIGNALS = (
    signal.SIGINT,  # Unix signal 2. Sent by Ctrl+C.
    signal.SIGTERM,  # Unix signal 15. Sent by `kill <pid>`.
)


class Core:

    should_exit: asyncio.Event
    rules_priority_dict: Dict[int, List[Type[Rule[Any, Any, Any]]]]

    _condition: (asyncio.Condition)
    _current_event: Optional[Event[Any]]
    _restart_flag: bool
    _module_path_finder: ModulePathFinder
    _raw_config_dict: Dict[str, Any]
    _handle_event_tasks: Set[
        "asyncio.Task[None]"
    ]  # Event handling task, used to keep a reference to the adapter task
    # The following properties are not cleared on reboot
    _config_file: Optional[str]  # Configuration file
    _config_dict: Optional[Dict[str, Any]]  # Configuration dictionary
    _hot_reload: bool  # Hot-Reload
    _extend_rules: List[
        Union[Type[Rule[Any, Any, Any]], str, Path]
    ]  # A list of rules loaded programmatically using the ``load_rules()`` method
    _extend_rule_dirs: List[
        Path
    ]  # List of rule paths loaded programmatically using the ``load_rules_from_dirs()`` method
    _core_run_hooks: List[CoreHook]
    _core_exit_hooks: List[CoreHook]
    _event_pre_processor_hooks: List[EventHook]
    _event_post_processor_hooks: List[EventHook]

    def __init__(
        self,
        *,
        config_file: Optional[str] = "config.toml",
        config_dict: Optional[Dict[str, Any]] = None,
        hot_reload: bool = False,
    ) -> None:
        self.config = MainConfig()
        self.rules_priority_dict = defaultdict(list)
        self._current_event = None
        self._restart_flag = False
        self._module_path_finder = ModulePathFinder()
        self._raw_config_dict = {}
        self._handle_event_tasks = set()

        self._config_file = config_file
        self._config_dict = config_dict
        self._hot_reload = hot_reload

        self._extend_rules = []
        self._extend_rule_dirs = []
        self._core_run_hooks = []
        self._core_exit_hooks = []
        self._event_pre_processor_hooks = []
        self._event_post_processor_hooks = []

        sys.meta_path.insert(0, self._module_path_finder)

    @property
    def rules(self) -> List[Type[Rule[Any, Any, Any]]]:
        """List of currently loaded rules."""
        return list(chain(*self.rules_priority_dict.values()))

    def run(self) -> None:
        self._restart_flag = True
        while self._restart_flag:
            self._restart_flag = False
            asyncio.run(self._run())
            if self._restart_flag:
                self._load_plugins_from_dirs(*self._extend_rule_dirs)
                self._load_plugins(*self._extend_rules)

    def restart(self) -> None:
        logger.info("Restarting...")
        self._restart_flag = True
        self.should_exit.set()

    async def _run(self) -> None:
        self.should_exit = asyncio.Event()
        self._condition = asyncio.Condition()

        # Monitor and intercept system exit signals to complete some aftermath work before closing the program
        if threading.current_thread() is threading.main_thread():  # pragma: no cover
            # Signals can only be processed in the main thread
            try:
                loop = asyncio.get_running_loop()
                for sig in HANDLED_SIGNALS:
                    loop.add_signal_handler(sig, self._handle_exit)
            except NotImplementedError:
                # add_signal_handler is only available under Unix, below for Windows
                for sig in HANDLED_SIGNALS:
                    signal.signal(sig, self._handle_exit)

        # Load configuration file
        self._reload_config_dict()

        self._load_rules_from_dirs(*self.config.bot.rule_dirs)
        self._load_rules(*self.config.bot.rules)
        self._update_config()

        logger.info("Running...")

        hot_reload_task = None
        if self._hot_reload:  # pragma: no cover
            hot_reload_task = asyncio.create_task(self._run_hot_reload())

        for core_run_hook_func in self._core_run_hooks:
            await core_run_hook_func(self)

        self.rules_priority_dict.clear()
        self._module_path_finder.path.clear()

    def _remove_rule_by_path(
        self, file: Path
    ) -> List[Type[Rule[Any, Any, Any]]]:  # pragma: no cover
        removed_rules: List[Type[Rule[Any, Any, Any]]] = []
        for rules in self.plugins_priority_dict.values():
            _removed_rules = list(
                filter(
                    lambda x: x.__rule_load_type__ != RuleLoadType.CLASS
                    and x.__rule_file_path__ is not None
                    and samefile(x.__rule_file_path__, file),
                    rules,
                )
            )
            removed_rules.extend(_removed_rules)
            for rule_ in _removed_rules:
                rules.remove(rule_)
                logger.info(
                    "Succeeded to remove rule "
                    f'"{rule_.__name__}" from file "{file}"'
                )
        return removed_rules

    async def _run_hot_reload(self) -> None:  # pragma: no cover
        """Hot reload."""
        try:
            from watchfiles import Change, awatch
        except ImportError:
            logger.warning(
                'Hot reload needs to install "watchfiles", try "pip install watchfiles"'
            )
            return

        logger.info("Hot reload is working!")
        async for changes in awatch(
            *(
                x.resolve()
                for x in set(self._extend_rule_dirs)
                .union(self.config.core.rule_dirs)
                .union(
                    {Path(self._config_file)}
                    if self._config_dict is None and self._config_file is not None
                    else set()
                )
            ),
            stop_event=self.should_exit,
        ):
            # Processed in the order of Change.deleted, Change.modified, Change.added
            # To ensure that when renaming occurs, deletions are processed first and then additions are processed
            for change_type, file_ in sorted(changes, key=lambda x: x[0], reverse=True):
                file = Path(file_)
                # Change configuration file
                if (
                    self._config_file is not None
                    and samefile(self._config_file, file)
                    and change_type == change_type.modified
                ):
                    logger.info(f'Reload config file "{self._config_file}"')
                    old_config = self.config
                    self._reload_config_dict()
                    if (
                        self.config.bot != old_config.bot
                        or self.config.adapter != old_config.adapter
                    ):
                        self.restart()
                    continue

                # Change rule folder
                if change_type == Change.deleted:
                    # Special handling for deletion operations
                    if file.suffix != ".py":
                        file = file / "__init__.py"
                else:
                    if file.is_dir() and (file / "__init__.py").is_file():
                        # When a new directory is added and this directory contains the ``__init__.py`` file
                        # It means that what happens at this time is that a Python package is added, and the ``__init__.py`` file of this package is deemed to be added
                        file = file / "__init__.py"
                    if not (file.is_file() and file.suffix == ".py"):
                        continue

                if change_type == Change.added:
                    logger.info(f"Hot reload: Added file: {file}")
                    self._load_plugins(
                        Path(file), rule_load_type=RuleLoadType.DIR, reload=True
                    )
                    self._update_config()
                    continue
                if change_type == Change.deleted:
                    logger.info(f"Hot reload: Deleted file: {file}")
                    self._remove_rule_by_path(file)
                    self._update_config()
                elif change_type == Change.modified:
                    logger.info(f"Hot reload: Modified file: {file}")
                    self._remove_rule_by_path(file)
                    self._load_plugins(
                        Path(file), rule_load_type=RuleLoadType.DIR, reload=True
                    )
                    self._update_config()

    def _update_config(self) -> None:
        def update_config(
            source: List[Type[Rule[Any, Any, Any]]],
            name: str,
            base: Type[ConfigModel],
        ) -> Tuple[Type[ConfigModel], ConfigModel]:
            config_update_dict: Dict[str, Any] = {}
            for i in source:
                config_class = getattr(i, "Config", None)
                if is_config_class(config_class):
                    default_value: Any
                    try:
                        default_value = config_class()
                    except ValidationError:
                        default_value = ...
                    config_update_dict[config_class.__config_name__] = (
                        config_class,
                        default_value,
                    )
            config_model = create_model(
                name, **config_update_dict, __base__=base)
            return config_model, config_model()

        self.config = create_model(
            "Config",
            rule=update_config(self.rules, "RuleConfig", RuleConfig),
            __base__=MainConfig,
        )(**self._raw_config_dict)
        # Update the level of logging
        logger.remove()
        logger.add(sys.stderr, level=self.config.bot.log.level)

    def _reload_config_dict(self) -> None:
        """Reload the configuration file."""
        self._raw_config_dict = {}

        if self._config_dict is not None:
            self._raw_config_dict = self._config_dict
        elif self._config_file is not None:
            try:
                with Path(self._config_file).open("rb") as f:
                    if self._config_file.endswith(".json"):
                        self._raw_config_dict = json.load(f)
                    elif self._config_file.endswith(".toml"):
                        self._raw_config_dict = tomllib.load(f)
                    else:
                        self.error_or_exception(
                            "Read config file failed:",
                            OSError("Unable to determine config file type"),
                        )
            except OSError as e:
                self.error_or_exception("Can not open config file:", e)
            except (ValueError, json.JSONDecodeError, tomllib.TOMLDecodeError) as e:
                self.error_or_exception("Read config file failed:", e)

        try:
            self.config = MainConfig(**self._raw_config_dict)
        except ValidationError as e:
            self.config = MainConfig()
            self.error_or_exception("Config dict parse error:", e)
        self._update_config()

    def reload_rules(self) -> None:
        self.rules_priority_dict.clear()
        self._load_rules(*self.config.core.rules)
        self._load_rules_from_dirs(*self.config.core.rule_dirs)
        self._load_rules(*self._extend_rules)
        self._load_rules_from_dirs(*self._extend_rule_dirs)
        self._update_config()

    def _handle_exit(self, *_args: Any) -> None:  # pragma: no cover
        """When the robot receives the exit signal, it will handle it according to the situation."""
        logger.info("Stopping...")
        if self.should_exit.is_set():
            logger.warning("Force Exit...")
            sys.exit()
        else:
            self.should_exit.set()

    async def handle_event(
        self,
        current_event: Event[Any],
        *,
        handle_get: bool = True,
        show_log: bool = True,
    ) -> None:
        if show_log:
            logger.info(
                f"Rule {current_event.rule.name} received: {current_event!r}"
            )

        if handle_get:
            _handle_event_task = asyncio.create_task(self._handle_event())
            self._handle_event_tasks.add(_handle_event_task)
            _handle_event_task.add_done_callback(
                self._handle_event_tasks.discard)
            await asyncio.sleep(0)
            async with self._condition:
                self._current_event = current_event
                self._condition.notify_all()
        else:
            _handle_event_task = asyncio.create_task(
                self._handle_event(current_event))
            self._handle_event_tasks.add(_handle_event_task)
            _handle_event_task.add_done_callback(
                self._handle_event_tasks.discard)

    async def _handle_event(self, current_event: Optional[Event[Any]] = None) -> None:
        if current_event is None:
            async with self._condition:
                await self._condition.wait()
                assert self._current_event is not None
                current_event = self._current_event
            if current_event.__handled__:
                return

        for _hook_func in self._event_pre_processor_hooks:
            await _hook_func(current_event)

        for rule_priority in sorted(self.rules_priority_dict.keys()):
            logger.debug(
                f"Checking for matching rules with priority {rule_priority!r}"
            )
            stop = False
            for rule in self.rules_priority_dict[rule_priority]:
                try:
                    async with AsyncExitStack() as stack:
                        _rule = await solve_dependencies(
                            rule,
                            use_cache=True,
                            stack=stack,
                            dependency_cache={
                                Core: self,
                                Event: current_event,
                            },
                        )
                        if await _rule.rule():
                            logger.info(f"Event will be handled by {_rule!r}")
                            try:
                                await _rule.handle()
                            finally:
                                if _rule.block:
                                    stop = True
                except SkipException:
                    # The plug-in requires that it skips itself and continues the current event propagation
                    continue
                except StopException:
                    # Plugin requires stopping current event propagation
                    stop = True
                except Exception as e:
                    self.error_or_exception(f'Exception in rule "{rule}":', e)
            if stop:
                break

        for _hook_func in self._event_post_processor_hooks:
            await _hook_func(current_event)

        logger.info("Event Finished")

    @overload
    async def get(
        self,
        func: Optional[Callable[[Event[Any]],
                                Union[bool, Awaitable[bool]]]] = None,
        *,
        event_type: None = None,
        max_try_times: Optional[int] = None,
        timeout: Optional[Union[int, float]] = None,
    ) -> Event[Any]: ...

    @overload
    async def get(
        self,
        func: Optional[Callable[[EventT],
                                Union[bool, Awaitable[bool]]]] = None,
        *,
        event_type: None = None,
        max_try_times: Optional[int] = None,
        timeout: Optional[Union[int, float]] = None,
    ) -> EventT: ...

    @overload
    async def get(
        self,
        func: Optional[Callable[[EventT],
                                Union[bool, Awaitable[bool]]]] = None,
        *,
        event_type: Type[EventT],
        max_try_times: Optional[int] = None,
        timeout: Optional[Union[int, float]] = None,
    ) -> EventT: ...

    async def get(
        self,
        func: Optional[Callable[[Any], Union[bool, Awaitable[bool]]]] = None,
        *,
        event_type: Optional[Type[Event[Any]]] = None,
        max_try_times: Optional[int] = None,
        timeout: Optional[Union[int, float]] = None,
    ) -> Event[Any]:
        """Get events that meet the specified conditions. The coroutine will wait until the adapter receives events that meet the conditions, exceeds the maximum number of events, or times out.

        Args:
            func: Coroutine or function, the function will be automatically packaged as a coroutine for execution.
                Requires an event to be accepted as a parameter and returns a Boolean value. Returns the current event when the coroutine returns ``True``.
                When ``None`` is equivalent to the input coroutine returning true for any event, that is, returning the next event received by the adapter.
            event_type: When specified, only events of the specified type are accepted, taking effect before the func condition. Defaults to ``None``.
            adapter_type: When specified, only events generated by the specified adapter will be accepted, taking effect before the func condition. Defaults to ``None``.
            max_try_times: Maximum number of events.
            timeout: timeout period.

        Returns:
            Returns events that satisfy the condition of ``func``.

        Raises:
            GetEventTimeout: Maximum number of events exceeded or timeout.
        """
        _func = wrap_get_func(func)

        try_times = 0
        start_time = time.time()
        while not self.should_exit.is_set():
            if max_try_times is not None and try_times > max_try_times:
                break
            if timeout is not None and time.time() - start_time > timeout:
                break

            async with self._condition:
                if timeout is None:
                    await self._condition.wait()
                else:
                    try:
                        await asyncio.wait_for(
                            self._condition.wait(),
                            timeout=start_time + timeout - time.time(),
                        )
                    except asyncio.TimeoutError:
                        break

                if (
                    self._current_event is not None
                    and not self._current_event.__handled__
                    and (
                        event_type is None
                        or isinstance(self._current_event, event_type)
                    )
                    and await _func(self._current_event)
                ):
                    self._current_event.__handled__ = True
                    return self._current_event

                try_times += 1

        raise GetEventTimeout

    def _load_rule_class(
        self,
        rule_class: Type[Rule[Any, Any, Any]],
        rule_load_type: RuleLoadType,
        rule_file_path: Optional[str],
    ) -> None:
        """Load a rule class"""
        priority = getattr(rule_class, "priority", None)
        if isinstance(priority, int) and priority >= 0:
            for _rule in self.rules:
                if _rule.__name__ == rule_class.__name__:
                    logger.warning(
                        f'Already have a same name rule pack "{
                            _rule.__name__}"'
                    )
            rule_class.__rule_load_type__ = rule_load_type
            rule_class.__rule_file_path__ = rule_file_path
            self.rules_priority_dict[priority].append(rule_class)
            logger.info(
                f'Succeeded to load rule "{rule_class.__name__}" '
                f'from class "{rule_class!r}"'
            )
        else:
            self.error_or_exception(
                f'Load rule from class "{rule_class!r}" failed:',
                LoadModuleError(
                    f'Rule priority incorrect in the class "{
                        rule_class!r}"'
                ),
            )

    def _load_rules_from_module_name(
        self,
        module_name: str,
        *,
        rule_load_type: RuleLoadType,
        reload: bool = False,
    ) -> None:
        """Load rules from the given module."""
        try:
            rule_classes = get_classes_from_module_name(
                module_name, Rule, reload=reload
            )
        except ImportError as e:
            self.error_or_exception(
                f'Import module "{module_name}" failed:', e)
        else:
            for rule_class, module in rule_classes:
                self._load_rule_class(
                    rule_class,  # type: ignore
                    rule_load_type,
                    module.__file__,
                )

    def _load_rules(
        self,
        *rules: Union[Type[Rule[Any, Any, Any]], str, Path],
        rule_load_type: Optional[RuleLoadType] = None,
        reload: bool = False,
    ) -> None:
        for rule_ in rules:
            try:
                if isinstance(rule_, type) and issubclass(rule_, Rule):
                    self._load_plugin_class(
                        rule_, rule_load_type or RuleLoadType.CLASS, None
                    )
                elif isinstance(rule_, str):
                    logger.info(f'Loading rules from module "{rule_}"')
                    self._load_rules_from_module_name(
                        rule_,
                        rule_load_type=rule_load_type or RuleLoadType.NAME,
                        reload=reload,
                    )
                elif isinstance(rule_, Path):
                    logger.info(f'Loading rules from path "{rule_}"')
                    if not rule_.is_file():
                        raise LoadModuleError(  # noqa: TRY301
                            f'The rule path "{rule_}" must be a file'
                        )

                    if rule_.suffix != ".py":
                        raise LoadModuleError(  # noqa: TRY301
                            f'The path "{rule_}" must endswith ".py"'
                        )

                    rule_module_name = None
                    for path in self._module_path_finder.path:
                        try:
                            if rule_.stem == "__init__":
                                if rule_.resolve().parent.parent.samefile(Path(path)):
                                    rule_module_name = rule_.resolve().parent.name
                                    break
                            elif rule_.resolve().parent.samefile(Path(path)):
                                rule_module_name = rule_.stem
                                break
                        except OSError:
                            continue
                    if rule_module_name is None:
                        rel_path = rule_.resolve().relative_to(Path().resolve())
                        if rel_path.stem == "__init__":
                            rule_module_name = ".".join(rel_path.parts[:-1])
                        else:
                            rule_module_name = ".".join(
                                rel_path.parts[:-1] + (rel_path.stem,)
                            )

                    self._load_rules_from_module_name(
                        rule_module_name,
                        rule_load_type=rule_load_type or RuleLoadType.FILE,
                        reload=reload,
                    )
                else:
                    raise TypeError(  # noqa: TRY301
                        f"{rule_} can not be loaded as rule"
                    )
            except Exception as e:
                self.error_or_exception(f'Load rule "{rule_}" failed:', e)

    def load_rules(
        self, *rules: Union[Type[Rule[Any, Any, Any]], str, Path]
    ) -> None:
        self._extend_plugins.extend(rules)

        return self._load_plugins(*rules)

    def _load_rules_from_dirs(self, *dirs: Path) -> None:
        dir_list = [str(x.resolve()) for x in dirs]
        logger.info(f'Loading rules from dirs "{
                    ", ".join(map(str, dir_list))}"')
        self._module_path_finder.path.extend(dir_list)
        for module_info in pkgutil.iter_modules(dir_list):
            if not module_info.name.startswith("_"):
                self._load_rules_from_module_name(
                    module_info.name, rule_load_type=RuleLoadType.DIR
                )

    def load_rules_from_dirs(self, *dirs: Path) -> None:
        self._extend_rule_dirs.extend(dirs)
        self._load_rules_from_dirs(*dirs)

    def get_plugin(self, name: str) -> Type[Rule[Any, Any, Any]]:
        for _rule in self.rules:
            if _rule.__name__ == name:
                return _rule
        raise LookupError(f'Can not find rule named "{name}"')

    def error_or_exception(
        self, message: str, exception: Exception
    ) -> None:  # pragma: no cover
        """Output error or exception logs based on the current Bot configuration.

        Args:
            message: message.
            exception: Exception.
        """
        if self.config.bot.log.verbose_exception:
            logger.exception(message)
        else:
            logger.error(f"{message} {exception!r}")

    def core_run_hook(self, func: CoreHook) -> CoreHook:
        self._core_run_hooks.append(func)
        return func

    def core_exit_hook(self, func: CoreHook) -> CoreHook:
        self._core_exit_hooks.append(func)
        return func

    def event_pre_processor_hook(self, func: EventHook) -> EventHook:
        self._event_preprocessor_hooks.append(func)
        return func

    def event_post_processor_hook(self, func: EventHook) -> EventHook:
        self._event_post_processor_hooks.append(func)
        return func
