"""Add hostname column to the resources table

Revision ID: 58a12e45663e
Revises: 06ce06e9bb85
Create Date: 2020-10-20 18:24:40.267394

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '58a12e45663e'
down_revision = '06ce06e9bb85'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('resources') as batch_op:
        batch_op.add_column(sa.Column('hostname', sa.String(length=64), nullable=True))


def downgrade():
    with op.batch_alter_table('resources') as batch_op:
        batch_op.drop_column('hostname')
