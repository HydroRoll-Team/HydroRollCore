# MyRule
import math
import dataclasses

from dataclasses import dataclass
from typing import Literal, Optional, Union
from pydantic import Field, BaseModel
from hrc.rule import aliases, BaseRule
from hrc.rule.BaseRule import CharacterCard