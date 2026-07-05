import streamlit as st
from utils.db import SessionLocal, User, Book, ReadingLog, Bookshelf, Badge
from utils.auth import require_login, get_current_user, is_admin
from datetime import date
from sqlalchemy import func

st.set_page_config(page_title="Admin Dashboard", page_icon="🛠️", layout="wide")

require_login()

# Check admin access
if not is_admin():
    st.error("🚫 Access Denied: Admin privileges required")
    st.stop()

st.title("🛠️ Admin Dashboard")

user = get_current_user()
db = SessionLocal()

st.success(f"👋 Welcome, Admin {user.name}!")

# Tabs for different admin functions
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "👥 Manage Users",
    "📚 Manage Books",
    "📝 Manage Logs",
    "🎯 Assign Books"
])

# TAB 1: Overview
with tab1:
    st.subheader("System Overview")
    
    total_users = db.query(User).count()
    total_books = db.query(Book).count()
    total_logs = db.query(ReadingLog).count()
    total_pages = db.query(func.sum(ReadingLog.pages_read)).scalar() or 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Total Users", total_users)
    with col2:
        st.metric("📚 Total Books", total_books)
    with col3:
        st.metric("📝 Total Logs", total_logs)
    with col4:
        st.metric("📖 Total Pages", total_pages)
    
    st.markdown("---")
    
    # Recent activity
    st.subheader("📈 Recent Reading Activity")
    
    recent_logs = db.query(ReadingLog).order_by(
        ReadingLog.created_at.desc()
    ).limit(10).all()
    
    for log in recent_logs:
        log_user = db.query(User).filter_by(id=log.user_id).first()
        book = db.query(Book).filter_by(id=log.book_id).first()
        
        if log_user and book:
            st.write(f"📌 **{log_user.name}** read **{log.pages_read} pages** of *{book.title}* on {log.date_read}")

# TAB 2: Manage Users
with tab2:
    st.subheader("👥 User Management")
    
    users = db.query(User).all()
    
    for usr in users:
        with st.expander(f"{usr.name} ({usr.email})"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Role:** {usr.role}")
                st.write(f"**Joined:** {usr.created_at.strftime('%Y-%m-%d')}")
                
                # Count stats
                user_logs = db.query(ReadingLog).filter_by(user_id=usr.id).count()
                user_books = db.query(Bookshelf).filter_by(user_id=usr.id).count()
                st.write(f"**Logs:** {user_logs} | **Books on Shelf:** {user_books}")
            
            with col2:
                new_role = st.selectbox(
                    "Change Role",
                    ["reader", "admin"],
                    index=0 if usr.role == "reader" else 1,
                    key=f"role_{usr.id}"
                )
                
                if new_role != usr.role:
                    if st.button("Update Role", key=f"update_role_{usr.id}"):
                        usr.role = new_role
                        db.commit()
                        st.success(f"Role updated to {new_role}!")
                        st.rerun()

# TAB 3: Manage Books
with tab3:
    st.subheader("📚 Book Management")
    
    # Add new book
    with st.expander("➕ Add New Book"):
        with st.form("admin_add_book"):
            title = st.text_input("Title *")
            author = st.text_input("Author")
            genre = st.selectbox("Genre", [
                "Fiction", "Non-Fiction", "Fantasy", "Science Fiction",
                "Mystery", "Biography", "History", "Adventure", "Other"
            ])
            total_pages = st.number_input("Total Pages", min_value=1, value=100)
            cover_url = st.text_input("Cover URL")
            
            if st.form_submit_button("Add Book"):
                if title:
                    new_book = Book(
                        title=title,
                        author=author,
                        genre=genre,
                        total_pages=total_pages,
                        cover_url=cover_url,
                        added_by=user.id
                    )
                    db.add(new_book)
                    db.commit()
                    st.success("Book added!")
                    st.rerun()
                else:
                    st.error("Title is required!")
    
    st.markdown("---")
    
    # List all books
    books = db.query(Book).all()
    
    for book in books:
        with st.expander(f"📕 {book.title}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Author:** {book.author or 'Unknown'}")
                st.write(f"**Genre:** {book.genre}")
                st.write(f"**Pages:** {book.total_pages}")
                
                # Count usage
                shelved = db.query(Bookshelf).filter_by(book_id=book.id).count()
                logs = db.query(ReadingLog).filter_by(book_id=book.id).count()
                st.write(f"**On {shelved} shelves | {logs} reading logs**")
            
            with col2:
                if st.button("🗑️ Delete", key=f"del_book_{book.id}"):
                    # Delete related records
                    db.query(Bookshelf).filter_by(book_id=book.id).delete()
                    db.query(ReadingLog).filter_by(book_id=book.id).delete()
                    db.delete(book)
                    db.commit()
                    st.success("Book deleted!")
                    st.rerun()

# TAB 4: Manage Logs
with tab4:
    st.subheader("📝 Reading Log Management")
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        all_users = db.query(User).all()
        selected_user = st.selectbox(
            "Filter by User",
            ["All"] + [u.name for u in all_users]
        )
    
    with col2:
        all_books = db.query(Book).all()
        selected_book = st.selectbox(
            "Filter by Book",
            ["All"] + [b.title for b in all_books]
        )
    
    # Get logs with filters
    query = db.query(ReadingLog)
    
    if selected_user != "All":
        usr = db.query(User).filter_by(name=selected_user).first()
        if usr:
            query = query.filter_by(user_id=usr.id)
    
    if selected_book != "All":
        bk = db.query(Book).filter_by(title=selected_book).first()
        if bk:
            query = query.filter_by(book_id=bk.id)
    
    logs = query.order_by(ReadingLog.date_read.desc()).all()
    
    st.write(f"**Found {len(logs)} logs**")
    
    for log in logs:
        log_user = db.query(User).filter_by(id=log.user_id).first()
        book = db.query(Book).filter_by(id=log.book_id).first()
        
        if log_user and book:
            with st.expander(f"{log.date_read} - {log_user.name} - {book.title}"):
                st.write(f"**Pages:** {log.pages_read}")
                st.write(f"**Minutes:** {log.minutes_read}")
                if log.notes:
                    st.write(f"**Notes:** {log.notes}")
                
                if st.button("🗑️ Delete Log", key=f"del_log_{log.id}"):
                    db.delete(log)
                    db.commit()
                    st.success("Log deleted!")
                    st.rerun()

# TAB 5: Assign Books
with tab5:
    st.subheader("🎯 Assign Books to Readers")
    
    with st.form("assign_book_form"):
        all_users = db.query(User).filter_by(role="reader").all()
        all_books = db.query(Book).all()
        
        selected_user = st.selectbox(
            "Select Reader",
            [u.name for u in all_users]
        )
        
        selected_book = st.selectbox(
            "Select Book",
            [b.title for b in all_books]
        )
        
        if st.form_submit_button("Assign Book"):
            usr = db.query(User).filter_by(name=selected_user).first()
            bk = db.query(Book).filter_by(title=selected_book).first()
            
            if usr and bk:
                # Check if already assigned
                existing = db.query(Bookshelf).filter_by(
                    user_id=usr.id,
                    book_id=bk.id
                ).first()
                
                if existing:
                    st.warning(f"{selected_book} is already on {selected_user}'s shelf!")
                else:
                    new_assignment = Bookshelf(
                        user_id=usr.id,
                        book_id=bk.id,
                        status="reading"
                    )
                    db.add(new_assignment)
                    db.commit()
                    st.success(f"✅ Assigned {selected_book} to {selected_user}!")
                    st.rerun()

db.close()