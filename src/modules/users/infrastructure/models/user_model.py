import uuid
from datetime import datetime

from sqlalchemy import UUID, Boolean, DateTime, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from shared.db.base import Base


class UserModel(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    username: Mapped[str] = mapped_column(String(200), nullable=False)
    timezone: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(String(200), nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("uq_users_email_not_deleted", func.lower(email), unique=True, postgresql_where=deleted_at.is_(None)),
        Index(
            "uq_users_username_not_deleted", func.lower(username), unique=True, postgresql_where=deleted_at.is_(None)
        ),
    )
