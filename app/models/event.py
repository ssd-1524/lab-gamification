from sqlalchemy import Column, String, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.database import Base

class Event(Base):
    __tablename__ = "events"

    event_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.session_id"))
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.plan_id"))
    feature = Column(String)
    action = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    event_metadata = Column("metadata", JSON)
