from typing import TypeVar, Generic, Any, TYPE_CHECKING, Awaitable, Callable, Optional

if TYPE_CHECKING:
    from .rules import Rules
    
    
RulesT = TypeVar("RulesT", bound="Rules[Any]")