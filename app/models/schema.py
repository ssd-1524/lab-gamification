from sqlalchemy import Column, String, Enum, ForeignKey, DateTime, Text, CheckConstraint, Integer, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func, text
import uuid
from app.database import Base

class Users(Base):
    __tablename__ = "users"

    user_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )

    loc_id = Column(
        UUID(as_uuid=True),
        ForeignKey("location.loc_id"),
        nullable=False,
        index=True
    )

    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey("role.role_id"),
        nullable=False,
        index=True
    )

    name = Column(String, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

class Sessions(Base):
    __tablename__ = "sessions"

    session_id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        nullable=False
    )
    
    user_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.user_id"),
        nullable=False,
        index=True
    )
    
    login_time = Column(
        DateTime,
        server_default=func.now(), 
        nullable=False
    )
    
    logout_time = Column(DateTime)
    device = Column(String)

class Role(Base):
    __tablename__ = "role"

    role_id = Column(
        UUID(as_uuid=True),              
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )

    role_name = Column(
        Enum("Viewer", "Operator", "Executive", "Manager", name="role_names",create_type=False ), 
        unique=True, 
        nullable=False
    )

class Question(Base):
    __tablename__ = "questions"

    question_id = Column(
        UUID(as_uuid=True), 
        primary_key=True,
        # server_default=text("generate_uuid()")
        default=uuid.uuid4,
        nullable=False
    )

    plan_id = Column(
        UUID(as_uuid=True),
        ForeignKey("plans.plan_id"),
        nullable=True,
        index=True
    )

    role_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("role.role_id"), 
        nullable=True, 
        index=True,
    )

    question_text = Column(Text, nullable=False)

    question_type = Column(
        Enum("Sugarcane", "Role", "Plan", name="question_types",create_type=False ), 
        nullable=False
    )

    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)

    correct_option = Column(Text, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "correct_option IN ('A', 'B', 'C')",
            name="check_correct_option_valid",
        ),
    ) 

class PointWallet(Base):
    __tablename__ = "pointwallet"

    user_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.user_id"), 
        primary_key=True, 
        default=uuid.uuid4,
        index=True,
        nullable=False  
    )

    total_points = Column(Integer, nullable=True)
    rank = Column(
        Enum("Bronze", "Silver", "Gold", "Platinum", name="rank_types",create_type=False), 
        nullable=True
    )

    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=True
    )

class PointHistory(Base):
    __tablename__ = "pointhistory"

    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        nullable=False
    )

    user_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.user_id"), 
        default=uuid.uuid4,
        index=True,
        nullable=False
    )

    points = Column(Integer, nullable=True)
    
    source = Column(
        Enum("Quiz", "Streak", "Manual", "Badges", name="point_sources",create_type=False ),
        nullable=True
    )

    timestamp = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=True
    )

class Plan(Base):
    __tablename__ = "plans"

    plan_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False
    )

    plan_type = Column(
        Enum("Basic", "Prime", "Nexus", name="plan_types",create_type=False ),
        nullable=False
    )

class Location(Base):
    __tablename__ = "location"

    loc_id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        nullable=False
    )

    plan_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("plans.plan_id"), 
        nullable=False,
        index=True,
    )

    loc_name = Column(
        Enum("Gautemala", "Nicaragua", "Mexico Panuco", "Mexico El Mante", name="location_names",create_type=False ),
        nullable=False
    )

class Event(Base):
    __tablename__ = "events"

    event_id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        nullable=False
    )

    user_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.user_id"),
        index=True,
        nullable=False
    )

    session_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("sessions.session_id"),
        index=True,
        nullable=False
    )

    plan_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("plans.plan_id"),
        index=True,
        nullable=False
    )

    feature = Column(String)
    action = Column(String)

    timestamp = Column(
        DateTime, 
        server_default=func.now()
    )

    event_metadata = Column("metadata", JSON)

class Badge(Base):
    __tablename__ = "badges"

    badge_id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        nullable=False
    )

    plan_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("plans.plan_id"), 
        nullable=False,
        index=True,
    )

    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    min_points = Column(Integer, nullable=True)

class UserBadge(Base):
    __tablename__ = "user_badges"

    user_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.user_id"), 
        primary_key=True,
        index=True,
        nullable=False
    )

    badge_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("badges.badge_id"), 
        primary_key=True,
        index=True,
        nullable=True
    )

    earned_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=True
    )