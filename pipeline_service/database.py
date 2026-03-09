from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()
database_url: str = str(os.getenv("DATABASE_URL"))

engine = create_engine(database_url, echo=False)
Session = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
