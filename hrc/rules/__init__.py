from typing import Generic, Any, Type

from abc import ABC

from . import BaseRule
from ..typing import RulesT


class Rules(ABC, Generic[RulesT]):
    ...
    