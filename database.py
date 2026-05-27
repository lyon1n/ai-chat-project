from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://root:123456@localhost/ai_chat"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)