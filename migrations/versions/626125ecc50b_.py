"""empty message

Revision ID: 626125ecc50b
Revises: 87bf63126332
Create Date: 2017-02-20 04:47:59.232850

"""

# revision identifiers, used by Alembic.
revision = '626125ecc50b'
down_revision = '87bf63126332'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('daily_reminder_config',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=10), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('reminder_time', sa.String(length=10), nullable=True),
    sa.ForeignKeyConstraint(['code'], ['experiment.code'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table(u'daily_reminder')
    op.drop_column('screen_unlock_config', u'app_id')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('screen_unlock_config', sa.Column(u'app_id', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    op.create_table(u'daily_reminder',
    sa.Column(u'id', sa.INTEGER(), nullable=False),
    sa.Column(u'code', sa.VARCHAR(length=10), autoincrement=False, nullable=True),
    sa.Column(u'created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column(u'reminder_time', sa.VARCHAR(length=10), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint([u'code'], [u'experiment.code'], name=u'daily_reminder_code_fkey'),
    sa.PrimaryKeyConstraint(u'id', name=u'daily_reminder_pkey')
    )
    op.drop_table('daily_reminder_config')
    ### end Alembic commands ###
