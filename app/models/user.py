from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True
    )
    loc_id = Column(UUID(as_uuid=True), ForeignKey("location.loc_id"), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("role.role_id"), nullable=False)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)