from sqlalchemy.orm import sessionmaker, Session
from .models import Base, SpotifyToken, NebulaUser
from fastapi import HTTPException

## Errors
class TokenNotFoundError(Exception):
    pass


def getAccToken(db_session: Session, user_id: int):
    token = db_session.query(SpotifyToken).filter(SpotifyToken.user_id == user_id).first()
    if token is None:
        raise TokenNotFoundError(f"No access token found for user_id {user_id}")
    else: 
        return token

def create_nebula_user(db_session: Session, spotify_user_id: str, display_name: str):
    ###Check for users
    if NebulaUser.spotify_user_id.contains(spotify_user_id):
        raise HTTPException(status_code=409, detail="User already exists")
    
    new_user = NebulaUser(spotify_user_id = spotify_user_id, display_name = display_name)

    db_session.add(new_user)
    db_session.commit()  # Commit the transaction to save to DB
    db_session.refresh(new_user)



