from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.database import Base

class Badge(Base):
    __tablename__ = "badges"

    badge_id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)
    min_points = Column(Integer)
    plan_required = Column(String)

class UserBadge(Base):
    __tablename__ = "user_badges"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), primary_key=True)
    badge_id = Column(UUID(as_uuid=True), ForeignKey("badges.badge_id"), primary_key=True)
    earned_at = Column(DateTime, default=datetime.utcnow)
