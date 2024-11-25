from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class Timestamp:
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=lambda: datetime.now().replace(tzinfo=None), nullable=False)


class User(Base, Timestamp):
    __tablename__ = "users"
    telegram_id = Column(Integer, unique=True, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    username = Column(String, nullable=True)
    language_code = Column(String, nullable=True)

    requests = relationship("Request", back_populates="user", cascade="all, delete-orphan")
    counters = relationship("Counter", back_populates="user", cascade="all, delete-orphan")


class Request(Base, Timestamp):
    __tablename__ = "requests"
    user_id = Column(Integer, ForeignKey("users.id"))
    query = Column(Text, nullable=False)
    topic = Column(String, nullable=False)
    intent = Column(String, nullable=True)
    response = Column(Text, nullable=True)

    prompt_injection = Column(Boolean, default=False)
    filtered = Column(Boolean, default=False)
    filtered_reason = Column(String, nullable=True)
    filtered_commentary = Column(Text, nullable=True)

    user = relationship("User", back_populates="requests")


class Counter(Base, Timestamp):
    __tablename__ = "counters"
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    value = Column(String, nullable=False)

    user = relationship("User", back_populates="counters")
