"""added customer_date column in the customer table

Revision ID: 29adcb18097c
Revises: 13c07910df93
Create Date: 2024-09-15 19:07:24.230241

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '29adcb18097c'
down_revision: Union[str, None] = '13c07910df93'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('customers', sa.Column('customer_date', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('customers', 'customer_date')
    # ### end Alembic commands ###
