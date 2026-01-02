"""Update changes in enum

Revision ID: 8c42aef0c8b1
Revises: 86b1f7895f78
Create Date: 2026-01-02 11:11:45.910648

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8c42aef0c8b1'
down_revision: Union[str, None] = '86b1f7895f78'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
