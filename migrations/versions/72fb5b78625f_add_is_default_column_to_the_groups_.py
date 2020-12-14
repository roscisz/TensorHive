"""add is_default column to the groups table

Revision ID: 72fb5b78625f
Revises: 58a12e45663e
Create Date: 2020-10-23 14:54:03.758690

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '72fb5b78625f'
down_revision = '58a12e45663e'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('groups') as batch_op:
        batch_op.add_column(sa.Column('is_default', sa.Boolean(), nullable=True))
        batch_op.create_unique_constraint('one_default_group_only', ['is_default'])


def downgrade():
    with op.batch_alter_table('groups') as batch_op:
        batch_op.drop_constraint('one_default_group_only', type_='unique')
        batch_op.drop_column('is_default')
