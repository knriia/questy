"""test alembic

Revision ID: a6adea677993
Revises:
Create Date: 2026-06-19 19:01:16.396689

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "a6adea677993"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
