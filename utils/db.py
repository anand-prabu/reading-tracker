import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.engine import URL
from datetime import datetime

# --- Engine Setup ---
def get_engine():
    db = st.secrets["database"]
    url = URL.create(
        drivername="postgresql+psycopg2",
        username=db["username"],
        password=db["password"],
        host=db["host"],
        port=int(db["port"]),
        database=db["database"],
        query={"sslmode": "require"},
    )
    return create_engine(url, pool_pre_ping=True, pool_recycle=300)

engine = get_engine()
SessionLocal = sessionmaker(bind=engine)

# --- ORM Base ---
class Base(DeclarativeBase):
    pass

# --- Models ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String)
    role = Column(String, default="reader")  # "reader" or "admin"
    created_at = Column(DateTime, default=datetime.utcnow)
    logs = relationship("ReadingLog", back_populates="user")
    bookshelf = relationship("Bookshelf", back_populates="user")

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String)
    genre = Column(String)
    total_pages = Column(Integer, default=0)
    cover_url = Column(String)
    added_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    logs = relationship("ReadingLog", back_populates="book")
    shelves = relationship("Bookshelf", back_populates="book")

class ReadingLog(Base):
    __tablename__ = "reading_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    date_read = Column(Date, nullable=False)
    pages_read = Column(Integer, default=0)
    minutes_read = Column(Integer, default=0)
    notes = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="logs")
    book = relationship("Book", back_populates="logs")

class Bookshelf(Base):
    __tablename__ = "bookshelves"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    status = Column(String, default="want_to_read")  # want_to_read, reading, completed
    added_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="bookshelf")
    book = relationship("Book", back_populates="shelves")

class Badge(Base):
    __tablename__ = "badges"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    badge_name = Column(String, nullable=False)
    awarded_at = Column(DateTime, default=datetime.utcnow)

# --- Create Tables ---
def init_db():
    Base.metadata.create_all(bind=engine)

# --- Helper Functions ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_or_create_user(email: str, name: str, db_session) -> User:
    user = db_session.query(User).filter_by(email=email).first()
    if not user:
        # First user gets admin if in admin_emails list
        admin_emails = list(st.secrets.get("app", {}).get("admin_emails", []))
        role = "admin" if email in admin_emails else "reader"
        user = User(email=email, name=name, role=role)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user

def get_user_stats(user_id: int, db_session) -> dict:
    from sqlalchemy import func
    logs = db_session.query(ReadingLog).filter_by(user_id=user_id).all()
    total_pages = sum(log.pages_read or 0 for log in logs)
    total_minutes = sum(log.minutes_read or 0 for log in logs)
    total_days = len(set(log.date_read for log in logs))
    books_read = db_session.query(Bookshelf).filter_by(
        user_id=user_id, status="completed"
    ).count()
    return {
        "total_pages": total_pages,
        "total_minutes": total_minutes,
        "total_days": total_days,
        "books_completed": books_read,
        "total_logs": len(logs),
    }