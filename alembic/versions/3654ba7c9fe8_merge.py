"""merge

Revision ID: 3654ba7c9fe8
Revises: d22df80a4a60
Create Date: 2026-03-28 20:51:21.758333

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '3654ba7c9fe8'
down_revision: Union[str, None] = 'd22df80a4a60'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass