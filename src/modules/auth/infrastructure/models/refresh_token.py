import uuid
from datetime import datetime

from sqlalchemy import UUID, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from shared.db import Base


class AuthRefreshTokenModel(Base):
    __tablename__ = "auth_refresh_tokens"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("auth_sessions.id", ondelete="CASCADE"),
        index=True,
    )
    replaced_by_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("auth_refresh_tokens.id"), nullable=True)
    secret_hash: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
