import functools
from typing import Generic, Any, Type

from abc import ABC

from . import BaseRule
from ..typing import RulesT


class Rules(ABC, Generic[RulesT]):
    ...


def aliases(names, ignore_case=False):
    def decorator(func):
        func._aliases = names
        func._ignore_case = ignore_case
        return func
    return decorator
