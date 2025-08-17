from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .models import SpotifyToken, NebulaUser
from fastapi import HTTPException
from datetime import datetime, timezone, timedelta

'''CRUD for SQL database'''

class TokenNotFoundError(Exception):
    '''Token not found exception'''

def get_token(db_session: Session, neb_user_id: int):
    '''Returns token for given nebula user'''
    
    token = db_session.query(SpotifyToken).filter(SpotifyToken.user_id == neb_user_id).first()
    if token is None:
        raise TokenNotFoundError(f"No access token found for user_id {neb_user_id}")
    else: 
        return token

def create_nebula_user(db_session: Session, spotify_user_id: str, display_name: str):
    '''Creates nebula user and returns user, if user already exists return existing user'''
    
    existing_user = db_session.query(NebulaUser).filter(NebulaUser.spotify_user_id == spotify_user_id).first()
    if existing_user: 
        return existing_user
    
    new_user = NebulaUser(spotify_user_id = spotify_user_id, display_name = display_name)
    
    try: 
        db_session.add(new_user)
        db_session.commit()
        db_session.refresh(new_user)
        
    except SQLAlchemyError as e:
        db_session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    verified_user = db_session.query(NebulaUser).filter_by(spotify_user_id=spotify_user_id).first()
    
    if not verified_user:
        raise HTTPException(status_code=500, detail="User creation failed")
    
    return verified_user


def update_tokens(db_session: Session, nebula_user_id: int, access_token:str, refresh_token:str):
    '''Updates and returns tokens for given user'''
    
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


def has_expired_token(db_session:Session,  nebula_user_id: int) -> bool:
    '''Returns true if tokens are expired, otherwise false'''
    
    existing_record = db_session.query(SpotifyToken).filter(SpotifyToken.user_id == nebula_user_id).first()
    expires_at = existing_record.expires_at.replace(tzinfo=timezone.utc)
    return expires_at <= datetime.now(timezone.utc)