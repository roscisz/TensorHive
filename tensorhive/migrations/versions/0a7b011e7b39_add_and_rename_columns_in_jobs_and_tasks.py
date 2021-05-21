"""add and rename columns in jobs and tasks

Revision ID: 0a7b011e7b39
Revises: a16bb624004f
Create Date: 2021-05-20 16:20:53.179078

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0a7b011e7b39'
down_revision = 'a16bb624004f'
branch_labels = None
depends_on = None


def upgrade():

    with op.batch_alter_table('jobs') as bop:
        bop.add_column(sa.Column('is_queued', sa.Boolean(), nullable=True))
        bop.alter_column('status', new_column_name='_status')

    with op.batch_alter_table('tasks') as bop:
        bop.alter_column('status', new_column_name='_status')
        bop.add_column(sa.Column('gpu_id', sa.Integer(), nullable=True))


def downgrade():

    with op.batch_alter_table('jobs') as bop:
        bop.drop_column('is_queued')
        bop.alter_column('_status', new_column_name='status')

    with op.batch_alter_table('tasks') as bop:
        bop.alter_column('_status', new_column_name='status')
        bop.drop_column('gpu_id')

