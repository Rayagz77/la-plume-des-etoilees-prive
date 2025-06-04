"""Add is_active column

Revision ID: 4355632516a9
Revises: 3b361a002e1a
Create Date: 2025-04-15 19:57:33.837066

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4355632516a9'
down_revision = '3b361a002e1a'
branch_labels = None
depends_on = None


def upgrade():
    # Solution pour éviter l'erreur NOT NULL sur table existante
    with op.batch_alter_table('User') as batch_op:
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))

def downgrade():
    with op.batch_alter_table('User') as batch_op:
        batch_op.drop_column('is_active')