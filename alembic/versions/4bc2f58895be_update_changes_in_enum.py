"""Update changes in enum

Revision ID: 4bc2f58895be
Revises: 8c42aef0c8b1
Create Date: 2026-01-02 11:16:42.016289

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4bc2f58895be'
down_revision: Union[str, None] = '8c42aef0c8b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
