"""rename_table_schedules

Revision ID: cebed67d7dc2
Revises: 04a7edffef9b
Create Date: 2026-06-23 22:15:48.444242

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'cebed67d7dc2'
down_revision: Union[str, Sequence[str], None] = '04a7edffef9b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Переименовываем саму таблицу
    op.rename_table('schedules', 'activity_schedules')

    # Переименовываем первичный ключ (Constraint)
    op.execute('ALTER TABLE activity_schedules RENAME CONSTRAINT schedules_pkey TO activity_schedules_pkey')

    # Переименовываем внешний ключ (Foreign Key)
    op.execute(
        'ALTER TABLE activity_schedules RENAME CONSTRAINT schedules_activity_id_fkey TO activity_schedules_activity_id_fkey'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Возвращаем старое имя таблице
    op.rename_table('activity_schedules', 'schedules')

    # Возвращаем старое имя внешнему ключу
    op.execute(
        'ALTER TABLE schedules RENAME CONSTRAINT activity_schedules_activity_id_fkey TO schedules_activity_id_fkey'
    )

    # Возвращаем старое имя первичному ключу
    op.execute('ALTER TABLE schedules RENAME CONSTRAINT activity_schedules_pkey TO schedules_pkey')
