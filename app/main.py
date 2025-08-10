from fastapi import FastAPI
from app.database.create_db import engine, Base

server = FastAPI()
Base.metadata.create_all(bind=engine)







    


