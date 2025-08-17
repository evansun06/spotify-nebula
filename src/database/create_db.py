from sqlalchemy import create_engine
from .models import Base
from sqlalchemy.orm import sessionmaker

'''Creates SQL database'''

URL = 'sqlite:///./mydatabase.db'

engine = create_engine(URL)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



