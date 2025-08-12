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
def getAccToken(db_session: Session, neb_user_id: int):
    token = db_session.query(SpotifyToken).filter(SpotifyToken.user_id == neb_user_id).first()
    if token is None:
        raise TokenNotFoundError(f"No access token found for user_id {neb_user_id}")
    else: 
        return token

## Create a NebulaUser
def create_nebula_user(db_session: Session, spotify_user_id: str, display_name: str):
    existing_user = db_session.query(NebulaUser).filter(NebulaUser.spotify_user_id == spotify_user_id).first()
    if existing_user: 
        raise HTTPException(status_code=409, detail="User already exists")
    
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
def update_tokens(db_session: Session, nebula_user_id: int, access_token:str, refresh_token:str,):
    existing_record = db_session.query(SpotifyToken).filter(SpotifyToken.user_id == nebula_user_id).first()
    if existing_record:
        record = db_session.query(SpotifyToken).filter_by(user_id=nebula_user_id).first()
        record.access_token = access_token
        record.expires_at=expires_at=datetime.now(timezone.utc) + timedelta(seconds=3600),
        record.updated_at=datetime.now(timezone.utc)
        return record
    else:
        new_token_record = SpotifyToken(user_id=nebula_user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=3600),
            updated_at=datetime.now(timezone.utc)
        )

        try: 
            db_session.add(new_token_record)
            db_session.commit()  # Commit the transaction to save to DB
            db_session.refresh(new_token_record)
        except SQLAlchemyError as e:
            db_session.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
        print("Sucess")
        return new_token_record
        

## Checks if a user has an expired token.
def has_expired_token(db_session:Session,  nebula_user_id: int) -> bool:
    existing_record = db_session.query(SpotifyToken).filter(SpotifyToken.user_id == nebula_user_id).first()
    if existing_record:
        return existing_record.expires_at > datetime.now(timezone.utc)
    else:
        return True


    









