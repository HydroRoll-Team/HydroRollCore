# ruff: noqa: TCH001
from typing import TYPE_CHECKING, Awaitable, Callable, Optional, TypeVar

if TYPE_CHECKING:
    from typing import Any

    from hrc.service import Service
    from hrc.core import Core
    from hrc.config import ConfigModel
    from hrc.event import Event
    from hrc.rule import Rule


StateT = TypeVar("StateT")
EventT = TypeVar("EventT", bound="Event[Any]")
RuleT = TypeVar("RuleT", bound="Rule[Any, Any, Any]")
ConfigT = TypeVar("ConfigT", bound=Optional["ConfigModel"])
ServiceT = TypeVar("ServiceT", bound="Service[Any, Any]")

CoreHook = Callable[["Core"], Awaitable[None]]
RuleHook = Callable[["Rule"], Awaitable[None]]
ServiceHook = Callable[["Service[Any, Any]"], Awaitable[None]]
EventHook = Callable[["Event[Any]"], Awaitable[None]]
