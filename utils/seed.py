from .db import get_session, get_engine, Base
from .models import Book, BadgeDefinition, LevelDefinition, User

def normalize_key(title, author, pages, isbn=None):
    if isbn:
        return f"isbn:{isbn.strip().lower()}"
    return f"{title.strip().lower()}|{author.strip().lower()}|{int(pages)}"

def initialize_database():
    Base.metadata.create_all(bind=get_engine())
    session = get_session()
    try:
        if session.query(Book).count() == 0:
            books = [
                Book(title="Charlotte's Web", author="E. B. White", total_pages=192, genre="Classic", level_hint="Explorer", cover_emoji="🕸️", normalized_key=normalize_key("Charlotte's Web","E. B. White",192)),
                Book(title="The Very Hungry Caterpillar", author="Eric Carle", total_pages=26, genre="Picture Book", level_hint="Starter", cover_emoji="🐛", normalized_key=normalize_key("The Very Hungry Caterpillar","Eric Carle",26)),
                Book(title="Harry Potter and the Philosopher's Stone", author="J. K. Rowling", total_pages=223, genre="Fantasy", level_hint="Champion", cover_emoji="🪄", normalized_key=normalize_key("Harry Potter and the Philosopher's Stone","J. K. Rowling",223)),
                Book(title="Matilda", author="Roald Dahl", total_pages=240, genre="Fiction", level_hint="Explorer", cover_emoji="📗", normalized_key=normalize_key("Matilda","Roald Dahl",240)),
            ]
            session.add_all(books)
        if session.query(BadgeDefinition).count() == 0:
            session.add_all([
                BadgeDefinition(code="streak_3", name="3-Day Streak", description="Read for 3 days in a row", icon="🔥", metric_type="streak", threshold=3),
                BadgeDefinition(code="streak_7", name="7-Day Streak", description="Read for 7 days in a row", icon="🔥", metric_type="streak", threshold=7),
                BadgeDefinition(code="pages_100", name="100 Pages Club", description="Read 100 pages total", icon="📘", metric_type="pages", threshold=100),
                BadgeDefinition(code="pages_500", name="500 Pages Club", description="Read 500 pages total", icon="🏆", metric_type="pages", threshold=500),
                BadgeDefinition(code="books_3", name="Book Explorer", description="Log 3 different books", icon="🌟", metric_type="books", threshold=3),
            ])
        if session.query(LevelDefinition).count() == 0:
            session.add_all([
                LevelDefinition(level_no=1, level_name="Tiny Tale Starter", min_pages=0),
                LevelDefinition(level_no=2, level_name="Page Explorer", min_pages=100),
                LevelDefinition(level_no=3, level_name="Chapter Champion", min_pages=300),
                LevelDefinition(level_no=4, level_name="Story Seeker", min_pages=700),
                LevelDefinition(level_no=5, level_name="Library Legend", min_pages=1200),
            ])
        session.commit()
    finally:
        session.close()
