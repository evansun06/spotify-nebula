from fastapi import FastAPI
from src.routers import spotify
from src.database.create_db import engine, Base
from fastapi.middleware.cors import CORSMiddleware

'''Main'''

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
app.include_router(spotify.router)



