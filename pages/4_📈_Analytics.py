import streamlit as st
from utils.db import SessionLocal, ReadingLog, Book
from utils.auth import require_login, get_current_user
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from collections import defaultdict

st.set_page_config(page_title="Analytics", page_icon="📈", layout="wide")

require_login()

st.title("📈 Reading Analytics")

user = get_current_user()
db = SessionLocal()

# Get user's logs
logs = db.query(ReadingLog).filter_by(user_id=user.id).order_by(ReadingLog.date_read).all()

if not logs:
    st.info("📊 No reading data yet. Start logging your reading to see analytics!")
    if st.button("Go to Log Reading"):
        st.switch_page("pages/2_✍️_Log_Reading.py")
else:
    # Prepare data
    dates = [log.date_read for log in logs]
    pages = [log.pages_read or 0 for log in logs]
    minutes = [log.minutes_read or 0 for log in logs]
    
    # Calculate cumulative
    cumulative_pages = []
    total = 0
    for p in pages:
        total += p
        cumulative_pages.append(total)
    
    df = pd.DataFrame({
        "date": dates,
        "pages": pages,
        "minutes": minutes,
        "cumulative_pages": cumulative_pages
    })
    
    # Summary stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📖 Total Pages", sum(pages))
    
    with col2:
        st.metric("⏱️ Total Minutes", sum(minutes))
    
    with col3:
        avg_pages = sum(pages) / len(pages) if pages else 0
        st.metric("📊 Avg Pages/Day", f"{avg_pages:.1f}")
    
    with col4:
        total_days = (max(dates) - min(dates)).days + 1 if dates else 0
        st.metric("📅 Days Tracked", total_days)
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Progress Over Time",
        "📅 Reading Calendar",
        "📚 By Book",
        "⏰ Reading Patterns"
    ])
    
    # TAB 1: Progress over time
    with tab1:
        st.subheader("Cumulative Progress")
        
        fig = px.line(
            df,
            x="date",
            y="cumulative_pages",
            title="Total Pages Read Over Time",
            labels={"date": "Date", "cumulative_pages": "Total Pages"},
            markers=True
        )
        fig.update_traces(line_color="#8B4513", line_width=3)
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Daily Reading Activity")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                df,
                x="date",
                y="pages",
                title="Pages Read Each Day",
                labels={"date": "Date", "pages": "Pages"},
                color="pages",
                color_continuous_scale="Blues"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                df,
                x="date",
                y="minutes",
                title="Minutes Spent Each Day",
                labels={"date": "Date", "minutes": "Minutes"},
                color="minutes",
                color_continuous_scale="Greens"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # TAB 2: Calendar heatmap
    with tab2:
        st.subheader("📅 Reading Calendar")
        
        # Group by date
        date_pages = defaultdict(int)
        for log in logs:
            date_pages[log.date_read] += log.pages_read or 0
        
        # Create calendar data
        if dates:
            start_date = min(dates)
            end_date = max(dates)
            
            calendar_data = []
            current_date = start_date
            
            while current_date <= end_date:
                calendar_data.append({
                    "date": current_date,
                    "pages": date_pages.get(current_date, 0),
                    "day_of_week": current_date.strftime("%A"),
                    "week": current_date.isocalendar()[1]
                })
                current_date += timedelta(days=1)
            
            cal_df = pd.DataFrame(calendar_data)
            
            # Heatmap
            fig = px.density_heatmap(
                cal_df,
                x="week",
                y="day_of_week",
                z="pages",
                title="Reading Activity Heatmap",
                labels={"week": "Week of Year", "day_of_week": "Day", "pages": "Pages Read"},
                color_continuous_scale="YlOrRd",
                category_orders={"day_of_week": [
                    "Monday", "Tuesday", "Wednesday", "Thursday", 
                    "Friday", "Saturday", "Sunday"
                ]}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # TAB 3: By book
    with tab3:
        st.subheader("📚 Reading by Book")
        
        book_stats = defaultdict(lambda: {"pages": 0, "minutes": 0, "sessions": 0})
        
        for log in logs:
            book = db.query(Book).filter_by(id=log.book_id).first()
            if book:
                book_name = book.title
                book_stats[book_name]["pages"] += log.pages_read or 0
                book_stats[book_name]["minutes"] += log.minutes_read or 0
                book_stats[book_name]["sessions"] += 1
        
        book_df = pd.DataFrame([
            {"book": k, "pages": v["pages"], "minutes": v["minutes"], "sessions": v["sessions"]}
            for k, v in book_stats.items()
        ])
        
        book_df = book_df.sort_values("pages", ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                book_df,
                values="pages",
                names="book",
                title="Pages Distribution by Book"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                book_df,
                x="book",
                y="sessions",
                title="Reading Sessions per Book",
                labels={"book": "Book", "sessions": "Sessions"},
                color="sessions",
                color_continuous_scale="Purples"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(book_df, use_container_width=True, hide_index=True)
    
    # TAB 4: Reading patterns
    with tab4:
        st.subheader("⏰ Reading Patterns")
        
        # Day of week analysis
        df["day_of_week"] = pd.to_datetime(df["date"]).dt.day_name()
        
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_stats = df.groupby("day_of_week").agg({
            "pages": "sum",
            "minutes": "sum"
        }).reindex(day_order)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                day_stats.reset_index(),
                x="day_of_week",
                y="pages",
                title="Pages Read by Day of Week",
                labels={"day_of_week": "Day", "pages": "Total Pages"},
                color="pages",
                color_continuous_scale="Blues"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                day_stats.reset_index(),
                x="day_of_week",
                y="minutes",
                title="Time Spent by Day of Week",
                labels={"day_of_week": "Day", "minutes": "Total Minutes"},
                color="minutes",
                color_continuous_scale="Greens"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Best day
        best_day = day_stats["pages"].idxmax()
        best_pages = day_stats["pages"].max()
        
        st.info(f"📊 Your most productive reading day is **{best_day}** with **{best_pages:.0f} total pages**!")

db.close()