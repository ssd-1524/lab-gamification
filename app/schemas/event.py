from __future__ import annotations

from typing import Dict, Any, Optional

from pydantic import BaseModel


class EventCreate(BaseModel):
    feature: str
    action: str
    metadata: Optional[Dict[str, Any]] = {}
