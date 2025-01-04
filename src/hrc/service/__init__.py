import os
from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Generic,
    Optional,
    Type,
    TypeVar,
    Union,
    final,
    overload,
)

from hrc.event import Event
from hrc.typing import ConfigT, EventT
from hrc.utils import is_config_class

if TYPE_CHECKING:
    from ..core import Core

__all__ = ["Server"]

if os.getenv("IAMAI_DEV") == "1":  # pragma: no cover
    # 当处于开发环境时，使用 pkg_resources 风格的命名空间包
    __import__("pkg_resources").declare_namespace(__name__)


_EventT = TypeVar("_EventT", bound="Event[Any]")


class Service(Generic[EventT, ConfigT], ABC): 
    name: str
    core: "Core"
    Config: Type[ConfigT]

    def __init__(self, core: "Core") -> None:
        if not hasattr(self, "name"):
            self.name = self.__class__.__name__
        self.core: Core = core
        self.handle_event = self.core.handle_event

    @property
    def config(self) -> ConfigT:
        default: Any = None
        config_class = getattr(self, "Config", None)
        if is_config_class(config_class):
            return getattr(
                self.core.config.service,
                config_class.__config_name__,
                default,
            )
        return default

    @final
    async def safe_run(self) -> None:
        try:
            await self.run()
        except Exception as e:
            self.core.error_or_exception(
                f"Run service {self.__class__.__name__} failed:", e
            )

    @abstractmethod
    async def run(self) -> None:
        raise NotImplementedError

    async def startup(self) -> None:
        ...
        
    async def shutdown(self) -> None:
        ...

    @overload
    async def get(
        self,
        func: Optional[Callable[[EventT], Union[bool, Awaitable[bool]]]] = None,
        *,
        event_type: None = None,
        max_try_times: Optional[int] = None,
        timeout: Optional[Union[int, float]] = None,
    ) -> EventT: ...

    @overload
    async def get(
        self,
        func: Optional[Callable[[_EventT], Union[bool, Awaitable[bool]]]] = None,
        *,
        event_type: Type[_EventT],
        max_try_times: Optional[int] = None,
        timeout: Optional[Union[int, float]] = None,
    ) -> _EventT: ...

    @final
    async def get(
        self,
        func: Optional[Callable[[Any], Union[bool, Awaitable[bool]]]] = None,
        *,
        event_type: Any = None,
        max_try_times: Optional[int] = None,
        timeout: Optional[Union[int, float]] = None,
    ) -> Event[Any]:
        return await self.core.get(
            func,
            event_type=event_type,
            server_type=type(self),
            max_try_times=max_try_times,
            timeout=timeout,
        )