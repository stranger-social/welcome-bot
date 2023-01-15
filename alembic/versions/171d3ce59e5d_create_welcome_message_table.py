"""create welcome posts table

Revision ID: 171d3ce59e5d
Revises: 8ae0cfc54c4e
Create Date: 2023-01-14 19:02:14.231680

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '171d3ce59e5d'
down_revision = '8ae0cfc54c4e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('posts',
    sa.Column('id', sa.Integer(), nullable = False, primary_key=True),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('content', sa.String(), nullable=False),
    sa.Column('published', sa.Boolean(), server_default="True", nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('owner_id', sa.Integer(), nullable=False)
    )
    op.create_foreign_key('posts_owner_id_fkey', source_table='posts', referent_table="users", local_cols=[
                          'owner_id'], remote_cols=['id'], ondelete="CASCADE")
    pass

def downgrade():
    op.drop_table('posts')
    pass