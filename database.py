from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import enum

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class StatusEnum(enum.Enum):
    alive = "alive"
    dead = "dead"
    finished = "finished"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(Enum(StatusEnum), default=StatusEnum.alive)
    status_updated_at = Column(DateTime, default=datetime.datetime.utcnow)
    msg_1_sent_at = Column(DateTime, nullable=True)
    msg_2_sent_at = Column(DateTime, nullable=True)
    msg_3_sent_at = Column(DateTime, nullable=True)

Base.metadata.create_all(bind=engine)
