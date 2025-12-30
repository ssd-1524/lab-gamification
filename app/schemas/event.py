from pydantic import BaseModel
from uuid import UUID
from typing import Optional, Dict

class EventCreate(BaseModel):
    session_id: UUID
    plan_id: UUID
    feature: str
    action: str
    metadata: Optional[Dict]
