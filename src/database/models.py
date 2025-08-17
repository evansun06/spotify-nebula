from sqlalchemy import Column, Integer, Text, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class NebulaUser(Base):
    '''ORM model for Nebula user'''
    
    __tablename__ = "nebula_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    spotify_user_id = Column(Text, unique=True, nullable=False)
    display_name = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())
    tokens = relationship("SpotifyToken", back_populates="user", cascade="all, delete-orphan")


class SpotifyToken(Base):
    '''ORM model for spotify tokens, linked to nebula users by id'''
    
    __tablename__ = "spotify_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("nebula_users.id", ondelete="CASCADE"))
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )
    user = relationship("NebulaUser", back_populates="tokens")
