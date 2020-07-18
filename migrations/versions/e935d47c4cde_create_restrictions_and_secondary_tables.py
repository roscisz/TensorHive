"""create restrictions and secondary tables

Revision ID: e935d47c4cde
Revises: 81c2455baab1
Create Date: 2020-07-18 09:42:52.140402

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e935d47c4cde'
down_revision = '81c2455baab1'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('restrictions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('starts_at', sa.DateTime(), nullable=False),
        sa.Column('ends_at', sa.DateTime(), nullable=True),
        sa.Column('is_global', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sqlite_autoincrement=True
    )
    op.create_table('restriction2assignee',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('restriction_id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['restriction_id'], ['restrictions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sqlite_autoincrement=True
    )
    op.create_table('restriction2resource',
        sa.Column('restriction_id', sa.Integer(), nullable=False),
        sa.Column('resource_id', sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(['resource_id'], ['resources.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['restriction_id'], ['restrictions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('restriction_id', 'resource_id')
    )


def downgrade():
    op.drop_table('restriction2resource')
    op.drop_table('restriction2assignee')
    op.drop_table('restrictions')
