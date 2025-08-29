from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    tg_id = Column(Integer, primary_key=True)
    path = Column(String(1000), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<User(id={self.tg_id}, title='{self.path}')>"
