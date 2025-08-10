from fastapi import FastAPI
from routers import auth

from app.database.create_db import engine, Base

server = FastAPI()
Base.metadata.create_all(bind=engine)
server.include_router(auth.router)