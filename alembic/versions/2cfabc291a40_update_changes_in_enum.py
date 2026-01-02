"""Update changes in enum

Revision ID: 2cfabc291a40
Revises: 4bc2f58895be
Create Date: 2026-01-02 11:18:33.930423

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2cfabc291a40'
down_revision: Union[str, None] = '4bc2f58895be'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
