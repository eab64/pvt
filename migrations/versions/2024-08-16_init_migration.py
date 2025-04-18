"""init migration

Revision ID: a2334a59d08a
Revises: 
Create Date: 2024-08-16 11:24:42.384161

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a2334a59d08a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    ...
    # REMOVE ME
    op.create_table('users',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('balance', sa.Numeric(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('transactions',
    sa.Column('uid', sa.String(length=36), nullable=False),
    sa.Column('type', sa.Enum('WITHDRAW', 'DEPOSIT', name='transactiontype'), nullable=False),
    sa.Column('amount', sa.Numeric(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('uid')
    )
    # END REMOVE ME


def downgrade():
    ...
    # REMOVE ME
    op.drop_table('transactions')
    op.drop_table('users')
    # END REMOVE ME
