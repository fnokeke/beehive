"""empty message

Revision ID: 699cd169160d
Revises: None
Create Date: 2017-02-08 11:17:51.808802

"""

# revision identifiers, used by Alembic.
revision = '699cd169160d'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('mturk_mobile',
    sa.Column('worker_id', sa.String(length=120), nullable=False),
    sa.Column('device_id', sa.String(length=120), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('worker_id', 'device_id'),
    sa.UniqueConstraint('device_id'),
    sa.UniqueConstraint('worker_id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('mturk_mobile')
    ### end Alembic commands ###
