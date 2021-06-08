"""create jobs table

Revision ID: a44e0949e0a0
Revises: e792ab930685
Create Date: 2020-11-30 08:26:07.204496

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a44e0949e0a0'
down_revision = 'e792ab930685'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('jobs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=40), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('status',
                  sa.Enum('not_running', 'running', 'terminated', 'unsynchronized', name='jobstatus'),
                  nullable=False),        
        sa.Column('_start_at', sa.DateTime(), nullable=True),
        sa.Column('_stop_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sqlite_autoincrement=True
    )


def downgrade():
    op.drop_table('jobs')
