"""add is_cancelled column to the reservation table

Revision ID: 06ce06e9bb85
Revises: 9d12594fe87b
Create Date: 2020-09-16 19:08:28.365494

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '06ce06e9bb85'
down_revision = '9d12594fe87b'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('reservations') as batch_op:
        batch_op.add_column(sa.Column('is_cancelled', sa.Boolean(), nullable=True))


def downgrade():
    with op.batch_alter_table('reservations') as batch_op:
        batch_op.drop_column('is_cancelled')
