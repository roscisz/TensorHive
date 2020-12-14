"""create restriction_schedules and restriction2schedule tables

Revision ID: 9d12594fe87b
Revises: e935d47c4cde
Create Date: 2020-07-18 12:09:43.342617

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9d12594fe87b'
down_revision = 'e935d47c4cde'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('restriction_schedules',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('schedule_days', sa.String(length=7), nullable=False),
        sa.Column('hour_start', sa.Time(), nullable=False),
        sa.Column('hour_end', sa.Time(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sqlite_autoincrement=True
    )
    op.create_table('restriction2schedule',
        sa.Column('restriction_id', sa.Integer(), nullable=False),
        sa.Column('schedule_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['restriction_id'], ['restrictions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['schedule_id'], ['restriction_schedules.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('restriction_id', 'schedule_id')
    )


def downgrade():
    op.drop_table('restriction2schedule')
    op.drop_table('restriction_schedules')
