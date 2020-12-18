"""create command_segments and cmd_segment2task tables

Revision ID: 4d010fddad6f
Revises: a44e0949e0a0
Create Date: 2020-11-30 08:55:48.870233

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4d010fddad6f'
down_revision = 'a44e0949e0a0'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('command_segments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=40), nullable=False),
        sa.Column('segment_type',
                  sa.Enum('env_variable', 'parameter', 'actual_command', name='segmenttype'),
                  nullable=False),        
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sqlite_autoincrement=True
    )

    op.create_table('cmd_segment2task',
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('cmd_segment_id', sa.Integer(), nullable=False),
        sa.Column('_value', sa.String(length=100), nullable=True),
        sa.Column('_index', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['cmd_segment_id'], ['command_segments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('task_id', 'cmd_segment_id')
    )

def downgrade():
    op.drop_table('command_segments')
    op.drop_table('cmd_segment2task')
