import dataclasses
from dataclasses import dataclass
from typing import Literal, Optional, Union

from . import JudgeRule
from . import CharacterCard

@dataclass
class CustomRule(object):
    """Docstring for CustomRule."""
    property: type


@dataclass
class ExpansionRule(object):
    """Docstring for ExpansionRule."""
    property: type


@dataclass
class Wiki(object):
    """Docstring for Wiki."""
    property: type


@dataclass
class Query(object):
    """Docstring for Query."""
    property: type


@dataclass
class Duration(object):
    """Docstring for Duration."""
    property: type
