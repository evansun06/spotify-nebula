from sqlalchemy import Table, Column, Integer, String, Text, ForeignKey, TIMESTAMP, MetaData, func
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class NebulaUser(Base):
    __tablename__ = "nebula_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    spotify_user_id = Column(Text, unique=True, nullable=False)
    display_name = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())

    # relationship to tokens (one-to-many)
    tokens = relationship("SpotifyToken", back_populates="user", cascade="all, delete-orphan")


class SpotifyToken(Base):
    __tablename__ = "spotify_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("nebula_users.id", ondelete="CASCADE"))
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())

    # relationship back to user
    user = relationship("SpotifyUser", back_populates="tokens")
