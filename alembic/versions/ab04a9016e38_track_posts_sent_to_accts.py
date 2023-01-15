"""Track posts sent to accts

Revision ID: ab04a9016e38
Revises: 171d3ce59e5d
Create Date: 2023-01-15 18:14:43.455168

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ab04a9016e38'
down_revision = '171d3ce59e5d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'posts_sent',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('mastodon_acct_id', sa.Integer(), nullable=False),
        sa.Column('sent_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['mastodon_acct_id'], ['mastodon_accts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint("post_id", "mastodon_acct_id")
    )
    op.create_index(op.f('ix_posts_sent_mastodon_acct_id'), 'posts_sent', ['mastodon_acct_id'], unique=False)
    op.create_index(op.f('ix_posts_sent_post_id'), 'posts_sent', ['post_id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_posts_sent_post_id'), table_name='posts_sent')
    op.drop_index(op.f('ix_posts_sent_mastodon_acct_id'), table_name='posts_sent')
    op.drop_table('posts_sent')
