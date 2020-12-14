"""Remove unique constraint from is_default group column

Revision ID: 7110c972b137
Revises: 72fb5b78625f
Create Date: 2020-10-26 19:54:49.344197

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7110c972b137'
down_revision = '72fb5b78625f'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('groups') as batch_op:
        batch_op.drop_constraint('one_default_group_only', type_='unique')


def downgrade():
    with op.batch_alter_table('groups') as batch_op:
        batch_op.create_unique_constraint('one_default_group_only', ['is_default'])
