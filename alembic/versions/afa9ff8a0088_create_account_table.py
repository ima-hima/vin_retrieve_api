"""create account table

Revision ID: afa9ff8a0088
Revises: 
Create Date: 2023-06-14 09:19:32.156949

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'afa9ff8a0088'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'vehicles',
        sa.Column('vin', sa.String, primary_key=True),
        sa.Column('make', sa.String(50), nullable=False),
        sa.Column('model', sa.String(50), nullable=False),
        sa.Column('model_year', sa.Integer, nullable=False),
        sa.Column('body_class', sa.String(50), nullable=False),
    )
