from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    tg_id = Column(Integer, primary_key=True)
    path = Column(String(1000), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    actions = relationship("ActionHistory", back_populates="user",
                           cascade="all, delete-orphan")


class ActionType(Base):
    __tablename__ = 'action_types'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)



class ActionHistory(Base):
    __tablename__ = 'actions_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_tg_id = Column(Integer, ForeignKey('users.tg_id'), nullable=False)
    action_type_id = Column(Integer, ForeignKey('action_types.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    description = Column(Text, nullable=True)

    user = relationship("User", back_populates="actions")
    action_type = relationship("ActionType")
