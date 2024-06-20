import dataclasses
from dataclasses import dataclass
from typing import Literal, Optional, Union
from typing_extensions import override


@dataclass
class CharacterCard(object):
    """Docstring for CharacterCard."""
    property: type

    class Information(object):
        age:  Optional[Union[int, str]]
        race: Optional[str]
        gender: Optional[str]
        group: Optional[str]


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
