from os import getenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

DATABASE_URL = getenv('DATABASE_URL')

def get_db():
    engine = create_engine(DATABASE_URL)
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = None
    try:
        db = session()
        yield db
    finally:
        db.close()


