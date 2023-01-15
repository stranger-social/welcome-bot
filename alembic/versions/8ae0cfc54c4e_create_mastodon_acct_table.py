"""create mastodon acct table

Revision ID: 8ae0cfc54c4e
Revises: 398aa8b3ee4d
Create Date: 2023-01-14 18:48:53.838101

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '8ae0cfc54c4e'
down_revision = '398aa8b3ee4d'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('mastodon_accts',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('acct', sa.VARCHAR(), autoincrement=False, nullable=False, unique=True, index=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.Column('welcomed', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False),
    sa.Column('welcomed_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='mastodon_accts_pkey')
    )
    pass

def downgrade():
    op.drop_table('mastodon_accts')
    pass
    