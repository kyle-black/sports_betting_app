"""empty message

Revision ID: 0bf5e3bba6b4
Revises: 
Create Date: 2023-06-02 12:52:22.071001

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0bf5e3bba6b4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('test_user', schema=None) as batch_op:
        batch_op.drop_index('ix_test_user_email')

    op.drop_table('test_user')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('test_user',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('email', sa.VARCHAR(length=64), nullable=True),
    sa.Column('password_hash', sa.VARCHAR(length=128), nullable=True),
    sa.Column('subscription_status', sa.VARCHAR(length=64), nullable=True),
    sa.Column('stripe_id', sa.VARCHAR(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('test_user', schema=None) as batch_op:
        batch_op.create_index('ix_test_user_email', ['email'], unique=False)

    # ### end Alembic commands ###
