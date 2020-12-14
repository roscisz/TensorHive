"""rename columns to match API

Revision ID: e792ab930685
Revises: 7110c972b137
Create Date: 2020-11-06 15:45:29.383856

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e792ab930685'
down_revision = '7110c972b137'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('reservations') as bop:
        bop.alter_column('protected_resource_id', new_column_name='resource_id')
        bop.alter_column('_starts_at', new_column_name='_start')
        bop.alter_column('_ends_at', new_column_name='_end')

    with op.batch_alter_table('tasks') as bop:
        bop.alter_column('host', new_column_name='hostname')


def downgrade():
    with op.batch_alter_table('reservations') as bop:
        bop.alter_column('resource_id', new_column_name='protected_resource_id')
        bop.alter_column('_start', new_column_name='_starts_at')
        bop.alter_column('_end', new_column_name='_ends_at')

    with bop.alter_column('tasks') as bop:
        bop.alter_column('hostname', new_column_name='host')
