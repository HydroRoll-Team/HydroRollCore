import functools  # noqa: F401
from typing import Generic, Any, Type

from abc import ABC

from . import BaseRule  # noqa: F401
from ..typing import RuleT  # noqa: F401

import inspect
from abc import abstractmethod
from enum import Enum
from typing import (
    TYPE_CHECKING,
    ClassVar,
    NoReturn,
    Optional,
    Tuple,
    cast,
    final,
)
from typing_extensions import Annotated, get_args, get_origin

from ..config import ConfigModel

from ..dependencies import Depends
from ..event import Event
from ..exceptions import SkipException, StopException
from ..typing import ConfigT, EventT, StateT
from ..utils import is_config_class

if TYPE_CHECKING:
    from ..core import Core


class RuleLoadType(Enum):
    """Rules loaded types."""

    DIR = "dir"
    NAME = "name"
    FILE = "file"
    CLASS = "class"


class Rule(ABC, Generic[EventT, StateT, ConfigT]):
    priority: ClassVar[int] = 0
    block: ClassVar[bool] = False

    # Cannot use ClassVar because PEP 526 does not allow it
    Config: Type[ConfigT]

    __rule_load_type__: ClassVar[RuleLoadType]
    __rule_file_path__: ClassVar[Optional[str]]

    if TYPE_CHECKING:
        event: EventT
    else:
        event = Depends(Event)  # noqa: F821

    def __init_state__(self) -> Optional[StateT]:
        """Initialize rule state."""

    def __init_subclass__(
        cls,
        config: Optional[Type[ConfigT]] = None,
        init_state: Optional[StateT] = None,
        **_kwargs: Any,
    ) -> None:
        super().__init_subclass__()

        orig_bases: Tuple[type, ...] = getattr(cls, "__orig_bases__", ())
        for orig_base in orig_bases:
            origin_class = get_origin(orig_base)
            if inspect.isclass(origin_class) and issubclass(origin_class, Rule):
                try:
                    _event_t, state_t, config_t = cast(
                        Tuple[EventT, StateT, ConfigT], get_args(orig_base)
                    )
                except ValueError:  # pragma: no cover
                    continue
                if (
                    config is None
                    and inspect.isclass(config_t)
                    and issubclass(config_t, ConfigModel)
                ):
                    config = config_t  # pyright: ignore
                if (
                    init_state is None
                    and get_origin(state_t) is Annotated
                    and hasattr(state_t, "__metadata__")
                ):
                    init_state = state_t.__metadata__[0]  # pyright: ignore

        if not hasattr(cls, "Config") and config is not None:
            cls.Config = config
        if cls.__init_state__ is Rule.__init_state__ and init_state is not None:
            cls.__init_state__ = lambda _: init_state  # type: ignore

    @final
    @property
    def name(self) -> str:
        """rule class name."""
        return self.__class__.__name__

    @final
    @property
    def core(self) -> "Core":
        """core object."""
        return self.event.core  # pylint: disable=no-member

    @final
    @property
    def config(self) -> ConfigT:
        """rule configuration."""
        default: Any = None
        config_class = getattr(self, "Config", None)
        if is_config_class(config_class):
            return getattr(
                self.core.config.rule,
                config_class.__config_name__,
                default,
            )
        return default

    @final
    def stop(self) -> NoReturn:
        """Stop propagation of current events."""
        raise StopException

    @final
    def skip(self) -> NoReturn:
        """Skips itself and continues propagation of the current event."""
        raise SkipException

    @property
    def state(self) -> StateT:
        """rule status."""
        return self.core.rule_state[self.name]

    @state.setter
    @final
    def state(self, value: StateT) -> None:
        self.core.rule_state[self.name] = value

    @abstractmethod
    async def handle(self) -> None:
        """Method to handle events. iamai will call this method when the ``rule()`` method returns ``True``. Each plugin must implement this method."""
        raise NotImplementedError
  
    @abstractmethod
    async def rule(self) -> bool:
        """Method to match the event. When the event is processed, this method will be called in sequence according to the priority of the plugin. When this method returns ``True``, the event will be handed over to this plugin for processing. Each plugin must implement this method.

        .. note::
            It is not recommended to implement event processing directly in this method. Please leave the specific processing of events to the ``handle()`` method.
        """
        raise NotImplementedError

    @staticmethod
    def aliases(names, ignore_case=False):
        def decorator(func):
            func._aliases = names
            func._ignore_case = ignore_case
            return func

        return decorator
