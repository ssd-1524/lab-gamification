from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database import Base

class Plan(Base):
    __tablename__ = "plans"

    plan_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_type = Column(String, unique=True, nullable=False)
