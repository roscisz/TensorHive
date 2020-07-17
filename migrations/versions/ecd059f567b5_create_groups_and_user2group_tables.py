"""create groups and user2group tables

Revision ID: ecd059f567b5
Revises: 131eb148fd57
Create Date: 2020-07-17 08:18:58.457152

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ecd059f567b5'
down_revision = '131eb148fd57'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('groups',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=40), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sqlite_autoincrement=True
    )
    op.create_table('user2group',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'group_id')
    )


def downgrade():
    op.drop_table('user2group')
    op.drop_table('groups')
