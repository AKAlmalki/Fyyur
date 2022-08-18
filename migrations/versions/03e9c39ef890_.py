"""empty message

Revision ID: 03e9c39ef890
Revises: 6eeb606d4c9d
Create Date: 2022-08-14 21:02:54.067063

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '03e9c39ef890'
down_revision = '6eeb606d4c9d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('genres', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'genres')
    # ### end Alembic commands ###
