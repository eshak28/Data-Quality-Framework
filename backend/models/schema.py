from pydantic import BaseModel
from typing import Optional

class Metadata(BaseModel):
    title: Optional[str]
    description: Optional[str]
    license: Optional[str]
    publisher: Optional[str] = None
    update_frequency: Optional[str] = None