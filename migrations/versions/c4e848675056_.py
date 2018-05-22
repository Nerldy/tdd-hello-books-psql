"""empty message

Revision ID: c4e848675056
Revises: acb926283872
Create Date: 2018-05-22 15:46:08.040551

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c4e848675056'
down_revision = 'acb926283872'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('black_list_tokens',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(), nullable=False),
    sa.Column('blacklisted_on', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('token')
    )
    op.drop_table('blacklist_token')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('blacklist_token',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('token', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('blacklisted_on', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='blacklist_token_pkey'),
    sa.UniqueConstraint('token', name='blacklist_token_token_key')
    )
    op.drop_table('black_list_tokens')
    # ### end Alembic commands ###
