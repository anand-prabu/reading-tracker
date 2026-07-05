import streamlit as st
from utils.db import SessionLocal, Book, ReadingLog, Bookshelf, Badge
from utils.auth import require_login, get_current_user, is_admin
from utils.gamification import check_badges, BADGES
from utils.db import get_user_stats
from datetime import date, datetime

st.set_page_config(page_title="Log Reading", page_icon="✍️", layout="wide")

require_login()

st.title("✍️ Log Your Reading")

user = get_current_user()
db = SessionLocal()

# Get user's books
my_books = db.query(Bookshelf).filter_by(user_id=user.id).all()

if not my_books:
    st.warning("📚 You don't have any books on your shelf yet!")
    st.info("Visit the 'My Bookshelf' page to add books first.")
    if st.button("Go to Bookshelf"):
        st.switch_page("pages/1_📚_My_Bookshelf.py")
else:
    # Create book options
    book_options = {}
    for shelf_item in my_books:
        book = db.query(Book).filter_by(id=shelf_item.book_id).first()
        if book:
            book_options[f"{book.title} by {book.author or 'Unknown'}"] = book.id
    
    with st.form("reading_log_form"):
        st.subheader("📝 New Reading Entry")
        
        # Book selection
        selected_book = st.selectbox(
            "Select Book *",
            options=list(book_options.keys())
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Date selection with restrictions
            today = date.today()
            
            if is_admin():
                log_date = st.date_input(
                    "Date *",
                    value=today,
                    help="Admins can log historical dates"
                )
            else:
                # Regular users can only log today or yesterday
                log_date = st.date_input(
                    "Date *",
                    value=today,
                    max_value=today,
                    help="You can only log for today or past dates"
                )
            
            pages_read = st.number_input("Pages Read *", min_value=0, value=10)
        
        with col2:
            minutes_read = st.number_input("Minutes Spent *", min_value=0, value=30)
            notes = st.text_area("Notes (optional)", placeholder="What did you think about today's reading?")
        
        submitted = st.form_submit_button("📖 Save Reading Log", use_container_width=True)
        
        if submitted:
            # Validate date
            if not is_admin() and log_date > today:
                st.error("❌ You cannot log reading for future dates!")
            elif pages_read <= 0:
                st.error("❌ Please enter pages read!")
            elif minutes_read <= 0:
                st.error("❌ Please enter minutes spent!")
            else:
                book_id = book_options[selected_book]
                
                # Check for duplicate entry
                existing = db.query(ReadingLog).filter_by(
                    user_id=user.id,
                    book_id=book_id,
                    date_read=log_date
                ).first()
                
                if existing:
                    st.warning(f"⚠️ You already logged reading for this book on {log_date}. Updating...")
                    existing.pages_read = pages_read
                    existing.minutes_read = minutes_read
                    existing.notes = notes
                else:
                    new_log = ReadingLog(
                        user_id=user.id,
                        book_id=book_id,
                        date_read=log_date,
                        pages_read=pages_read,
                        minutes_read=minutes_read,
                        notes=notes
                    )
                    db.add(new_log)
                
                db.commit()
                
                # Check for new badges
                from utils.db import get_user_stats
                stats = get_user_stats(user.id, db)
                logs = db.query(ReadingLog).filter_by(user_id=user.id).all()
                log_dates = [log.date_read for log in logs]
                
                existing_badges = [b.badge_name for b in db.query(Badge).filter_by(user_id=user.id).all()]
                new_badges = check_badges(stats, log_dates, existing_badges)
                
                if new_badges:
                    st.balloons()
                    st.success("✅ Reading logged successfully!")
                    st.markdown("### 🎉 New Badges Earned!")
                    
                    for badge_key in new_badges:
                        badge_info = BADGES[badge_key]
                        st.markdown(f"**{badge_info['name']}** - {badge_info['desc']}")
                        
                        new_badge = Badge(
                            user_id=user.id,
                            badge_name=badge_key
                        )
                        db.add(new_badge)
                    
                    db.commit()
                else:
                    st.success("✅ Reading logged successfully!")
                
                st.rerun()
    
    st.markdown("---")
    
    # Recent logs
    st.subheader("📜 Recent Reading History")
    
    recent_logs = db.query(ReadingLog).filter_by(user_id=user.id).order_by(
        ReadingLog.date_read.desc()
    ).limit(10).all()
    
    if recent_logs:
        for log in recent_logs:
            book = db.query(Book).filter_by(id=log.book_id).first()
            if book:
                with st.expander(f"📅 {log.date_read} - {book.title}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Pages:** {log.pages_read}")
                        st.write(f"**Minutes:** {log.minutes_read}")
                    with col2:
                        if log.notes:
                            st.write(f"**Notes:** {log.notes}")
                    
                    if st.button("🗑️ Delete", key=f"del_{log.id}"):
                        db.delete(log)
                        db.commit()
                        st.success("Log deleted!")
                        st.rerun()
    else:
        st.info("No reading logs yet. Start logging your reading above!")

db.close()