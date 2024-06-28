import dataclasses
from dataclasses import dataclass
from typing import Literal, Optional, Union


@dataclass
class Custom(object):
    """Docstring for Custom."""
    property: type


class Attribute(Custom):
    ...


class Skill(Custom):
    ...


class Information(Custom):
    ...

