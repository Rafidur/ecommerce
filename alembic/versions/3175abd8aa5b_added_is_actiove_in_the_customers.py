"""added is_actiove in the customers

Revision ID: 3175abd8aa5b
Revises: 364f517b7c8a
Create Date: 2024-09-22 12:29:32.637406

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3175abd8aa5b'
down_revision: Union[str, None] = '364f517b7c8a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('customers', sa.Column('is_active', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('customers', 'is_active')
    # ### end Alembic commands ###
