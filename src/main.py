from fastapi import FastAPI
from src.routers import spotify
from src.database import crud, create_db

from src.database.create_db import engine, Base

app = FastAPI()
Base.metadata.create_all(bind=engine)
app.include_router(spotify.router)



