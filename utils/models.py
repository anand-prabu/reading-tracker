from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from .db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    display_name = Column(String, nullable=False)
    role = Column(String, default="reader", nullable=False)
    class_name = Column(String, default="Class A")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Book(Base):
    __tablename__ = "books_master"
    id = Column(Integer, primary_key=True)
    isbn = Column(String, nullable=True, unique=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    total_pages = Column(Integer, nullable=False)
    genre = Column(String, default="General")
    level_hint = Column(String, default="Starter")
    cover_emoji = Column(String, default="📘")
    is_public = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    normalized_key = Column(String, nullable=False, unique=True)

class UserBook(Base):
    __tablename__ = "user_books"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books_master.id"), nullable=False)
    assigned_by = Column(String, default="system")
    assigned_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    user = relationship("User")
    book = relationship("Book")
    __table_args__ = (UniqueConstraint("user_id", "book_id", name="uq_user_book"),)

class ReadingLog(Base):
    __tablename__ = "reading_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books_master.id"), nullable=False)
    log_date = Column(Date, nullable=False)
    pages_read = Column(Integer, nullable=False)
    minutes_spent = Column(Integer, nullable=False)
    notes = Column(String, default="")
    created_by = Column(String, nullable=False)
    updated_by = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User")
    book = relationship("Book")

Index("ix_logs_user_date", ReadingLog.user_id, ReadingLog.log_date)

class BadgeDefinition(Base):
    __tablename__ = "badge_definitions"
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    icon = Column(String, default="🏅")
    metric_type = Column(String, nullable=False)  # "pages", "books", "streak"
    threshold = Column(Integer, nullable=False)

class UserBadge(Base):
    __tablename__ = "user_badges"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    badge_id = Column(Integer, ForeignKey("badge_definitions.id"), nullable=False)
    earned_at = Column(DateTime, default=datetime.utcnow)

class LevelDefinition(Base):
    __tablename__ = "level_definitions"
    id = Column(Integer, primary_key=True)
    level_no = Column(Integer, unique=True, nullable=False)
    level_name = Column(String, nullable=False)
    min_pages = Column(Integer, nullable=False)