"""empty message

Revision ID: a7b9830c016c
Revises: 9be5d50fec0f
Create Date: 2017-02-08 16:40:54.541629

"""

# revision identifiers, used by Alembic.
revision = 'a7b9830c016c'
down_revision = '9be5d50fec0f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('mturk_fb_stats', sa.Column('total_seconds', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('mturk_fb_stats', 'total_seconds')
    ### end Alembic commands ###
