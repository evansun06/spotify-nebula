from fastapi import FastAPI
from .routers import auth
from .database import crud, create_db

from src.database.create_db import engine, Base

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.include_router(auth.router)




