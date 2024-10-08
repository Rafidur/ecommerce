"""removed phone from customers table

Revision ID: bbd728f3a554
Revises: 19b3fa78dc72
Create Date: 2024-09-10 17:29:13.881428

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bbd728f3a554'
down_revision: Union[str, None] = '19b3fa78dc72'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('addresses', sa.Column('address', sa.String(), nullable=False))
    op.drop_column('addresses', 'Address')
    op.drop_column('customers', 'phone_number')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('customers', sa.Column('phone_number', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('addresses', sa.Column('Address', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_column('addresses', 'address')
    # ### end Alembic commands ###
