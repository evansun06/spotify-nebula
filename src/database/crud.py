from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from .models import Base, SpotifyToken, NebulaUser
from typing import Annotated
from fastapi import HTTPException, Depends
from . import create_db
from datetime import datetime, timezone, timedelta



## Errors
class TokenNotFoundError(Exception):
    pass

## Retrieve an API Access Token using a Nebula User ID
def get_token(db_session: Session, neb_user_id: int):
    token = db_session.query(SpotifyToken).filter(SpotifyToken.user_id == neb_user_id).first()
    if token is None:
        raise TokenNotFoundError(f"No access token found for user_id {neb_user_id}")
    else: 
        return token

## Create a NebulaUser
def create_nebula_user(db_session: Session, spotify_user_id: str, display_name: str):
    existing_user = db_session.query(NebulaUser).filter(NebulaUser.spotify_user_id == spotify_user_id).first()
    if existing_user: 
        return existing_user
    
    new_user = NebulaUser(spotify_user_id = spotify_user_id, display_name = display_name)
    try: 
        db_session.add(new_user)
        db_session.commit()  # Commit the transaction to save to DB
        db_session.refresh(new_user)
    except SQLAlchemyError as e:
        db_session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
     # Verify user was added
    verified_user = db_session.query(NebulaUser).filter_by(spotify_user_id=spotify_user_id).first()
    if not verified_user:
        raise HTTPException(status_code=500, detail="User creation failed")
    
    return verified_user


## Update Tokens For a Given User
def update_tokens(db_session: Session, nebula_user_id: int, access_token:str, refresh_token:str):
    token_model = db_session.query(SpotifyToken).filter(SpotifyToken.user_id == nebula_user_id).first()
    
    if token_model:
        token_model.access_token = access_token
        token_model.expires_at=datetime.now(timezone.utc) + timedelta(seconds=3600)
        token_model.updated_at=datetime.now(timezone.utc)
        
        db_session.add(token_model)
        db_session.commit()
        return token_model
    
    else:
        new_token_model = SpotifyToken(user_id=nebula_user_id,
                                        access_token=access_token,
                                        refresh_token=refresh_token,
                                        expires_at=datetime.now(timezone.utc) + timedelta(seconds=3600),
                                        updated_at=datetime.now(timezone.utc))

        try: 
            db_session.add(new_token_model)
            db_session.commit()
            
        except SQLAlchemyError as e:
            db_session.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
        return new_token_model
        

## Checks if a user has an expired token.
def has_expired_token(db_session:Session,  nebula_user_id: int) -> bool:
    existing_record = db_session.query(SpotifyToken).filter(SpotifyToken.user_id == nebula_user_id).first()
    expires_at = existing_record.expires_at.replace(tzinfo=timezone.utc)
    return expires_at <= datetime.now(timezone.utc)









