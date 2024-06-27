# MyRule
import math
import dataclasses

from dataclasses import dataclass
from typing import Literal, Optional, Union
from pydantic import Field, BaseModel
from hrc.rules import aliases, BaseRule
from hrc.rules.BaseRule import CharacterCard

class Query(Wiki):
    