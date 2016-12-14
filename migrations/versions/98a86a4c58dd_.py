"""empty message

Revision ID: 98a86a4c58dd
Revises: b4796edef8f8
Create Date: 2016-12-12 20:07:08.685801

"""

# revision identifiers, used by Alembic.
revision = '98a86a4c58dd'
down_revision = 'b4796edef8f8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('imageintv', sa.Column('image_name', sa.String(length=30), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('imageintv', 'image_name')
    ### end Alembic commands ###
