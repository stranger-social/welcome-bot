from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, Boolean, UniqueConstraint
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship

from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    is_active = Column(Boolean, nullable=False, default=True)
    is_admin = Column(Boolean, nullable=False, default=False)
    send_alerts = Column(Boolean, nullable=False, default=True)
    mastodon_acct = Column(String, nullable=False)

class MastodonAccts(Base):
    __tablename__ = "mastodon_accts"

    id = Column(Integer, primary_key=True, nullable=False)
    acct = Column(String, nullable=False, unique=True, index=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    welcomed = Column(Boolean, nullable=False, default=False)
    welcomed_at = Column(TIMESTAMP(timezone=True), nullable=True)
    
class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default="True", nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("User")

# Model to track which posts have been sent to which Mastodon accounts
class PostSent(Base):
    __tablename__ = "posts_sent"
    id = Column(Integer, primary_key=True, nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    post = relationship("Post")
    mastodon_acct_id = Column(Integer, ForeignKey("mastodon_accts.id", ondelete="CASCADE"), nullable=False)
    mastodon_acct = relationship("MastodonAccts")
    sent_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    __table_args__ = (
        UniqueConstraint('post_id', 'mastodon_acct_id', name='_post_acct_uc'),
    )
