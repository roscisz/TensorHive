"""create resources table

Revision ID: 81c2455baab1
Revises: ecd059f567b5
Create Date: 2020-07-17 10:50:16.607131

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '81c2455baab1'
down_revision = 'ecd059f567b5'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('resources',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=40), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('resources')
