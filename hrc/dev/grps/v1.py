from datetime import datetime
from pydantic import BaseModel


__version__ = "1.0.0-alpha.1"

class GRPS(BaseModel):
    id: str
    name: str
    description: str
    created_at: datetime
    updated_at: datetime