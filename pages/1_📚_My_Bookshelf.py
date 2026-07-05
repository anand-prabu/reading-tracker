import streamlit as st
from utils.db import SessionLocal, Book, Bookshelf, User
from utils.auth import require_login, get_current_user, is_admin
from sqlalchemy import or_

st.set_page_config(page_title="My Bookshelf", page_icon="📚", layout="wide")

require_login()

st.markdown("""
<style>
    .book-card {
        background: linear-gradient(135deg, #FFF8DC 0%, #F5DEB3 100%);
        padding: 15px;
        border-radius: 10px;
        border: 2px solid #DEB887;
        margin: 10px 0;
    }
    .book-title {
        font-size: 1.2em;
        font-weight: bold;
        color: #8B4513;
        margin-bottom: 5px;
    }
    .book-author {
        font-size: 0.9em;
        color: #A0522D;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

st.title("📚 My Bookshelf")

user = get_current_user()
db = SessionLocal()

# Tabs
tab1, tab2, tab3 = st.tabs(["📖 My Books", "🔍 Library", "➕ Add Book"])

# TAB 1: My Books
with tab1:
    st.subheader("Your Personal Collection")
    
    # Filter by status
    status_filter = st.selectbox(
        "Filter by status:",
        ["All", "Want to Read", "Reading", "Completed"]
    )
    
    # Get user's bookshelf
    query = db.query(Bookshelf).filter_by(user_id=user.id)
    
    if status_filter != "All":
        status_map = {
            "Want to Read": "want_to_read",
            "Reading": "reading",
            "Completed": "completed"
        }
        query = query.filter_by(status=status_map[status_filter])
    
    my_books = query.all()
    
    if not my_books:
        st.info("Your bookshelf is empty. Add books from the Library tab!")
    else:
        for shelf_item in my_books:
            book = db.query(Book).filter_by(id=shelf_item.book_id).first()
            if book:
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="book-card">
                        <div class="book-title">📕 {book.title}</div>
                        <div class="book-author">by {book.author or 'Unknown'}</div>
                        <div style="font-size: 0.85em; color: #8B4513; margin-top: 5px;">
                            📑 {book.genre or 'General'} • {book.total_pages or 0} pages
                        </div>
                        <div style="font-size: 0.85em; color: #A0522D; margin-top: 5px;">
                            Status: <strong>{shelf_item.status.replace('_', ' ').title()}</strong>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    new_status = st.selectbox(
                        "Change status",
                        ["want_to_read", "reading", "completed"],
                        index=["want_to_read", "reading", "completed"].index(shelf_item.status),
                        key=f"status_{shelf_item.id}"
                    )
                    
                    if new_status != shelf_item.status:
                        shelf_item.status = new_status
                        db.commit()
                        st.success("Status updated!")
                        st.rerun()
                    
                    if st.button("🗑️ Remove", key=f"remove_{shelf_item.id}"):
                        db.delete(shelf_item)
                        db.commit()
                        st.success("Book removed from shelf!")
                        st.rerun()

# TAB 2: Library
with tab2:
    st.subheader("📚 Class Library")
    
    # Search
    search = st.text_input("🔍 Search books by title or author:")
    
    # Get all books
    query = db.query(Book)
    
    if search:
        query = query.filter(
            or_(
                Book.title.ilike(f"%{search}%"),
                Book.author.ilike(f"%{search}%")
            )
        )
    
    all_books = query.all()
    
    if not all_books:
        st.info("No books found. Add some books to get started!")
    else:
        # Get user's current shelf book IDs
        user_book_ids = [item.book_id for item in db.query(Bookshelf).filter_by(user_id=user.id).all()]
        
        for book in all_books:
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"""
                <div class="book-card">
                    <div class="book-title">📕 {book.title}</div>
                    <div class="book-author">by {book.author or 'Unknown'}</div>
                    <div style="font-size: 0.85em; color: #8B4513; margin-top: 5px;">
                        📑 {book.genre or 'General'} • {book.total_pages or 0} pages
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if book.id in user_book_ids:
                    st.success("✓ On Shelf")
                else:
                    if st.button("➕ Add to Shelf", key=f"add_{book.id}"):
                        new_shelf = Bookshelf(
                            user_id=user.id,
                            book_id=book.id,
                            status="want_to_read"
                        )
                        db.add(new_shelf)
                        db.commit()
                        st.success("Added to your shelf!")
                        st.rerun()

# TAB 3: Add Book (Admin or all users based on your preference)
with tab3:
    st.subheader("➕ Add New Book to Library")
    
    with st.form("add_book_form"):
        title = st.text_input("Book Title *", placeholder="Enter book title")
        author = st.text_input("Author", placeholder="Enter author name")
        genre = st.selectbox("Genre", [
            "Fiction", "Non-Fiction", "Fantasy", "Science Fiction",
            "Mystery", "Biography", "History", "Adventure", "Other"
        ])
        total_pages = st.number_input("Total Pages", min_value=1, value=100)
        cover_url = st.text_input("Cover Image URL (optional)", placeholder="https://...")
        
        submitted = st.form_submit_button("📚 Add Book")
        
        if submitted:
            if not title:
                st.error("Please enter a book title!")
            else:
                new_book = Book(
                    title=title,
                    author=author,
                    genre=genre,
                    total_pages=total_pages,
                    cover_url=cover_url if cover_url else None,
                    added_by=user.id
                )
                db.add(new_book)
                db.commit()
                st.success(f"✅ '{title}' has been added to the library!")
                st.rerun()

db.close()