"""add send_alerts and mastodon_acct colomn to bot user

Revision ID: e56af5111d3e
Revises: ab04a9016e38
Create Date: 2023-01-16 19:37:18.773031

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e56af5111d3e'
down_revision = 'ab04a9016e38'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('send_alerts', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('users', sa.Column('mastodon_acct', sa.String(), nullable=True))


def downgrade():
    op.drop_column('users', 'mastodon_acct')
    op.drop_column('users', 'send_alerts')