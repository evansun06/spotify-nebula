from fastapi import FastAPI
from src.routers import spotify
from src.database.create_db import engine, Base

'''Main'''

app = FastAPI()
Base.metadata.create_all(bind=engine)
app.include_router(spotify.router)



