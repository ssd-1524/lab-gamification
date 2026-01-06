from pydantic import BaseModel
from typing import Dict, Any


class BonusRequest(BaseModel):
    feature: str
    points: int
    metadata: Dict[str, Any] = {}
