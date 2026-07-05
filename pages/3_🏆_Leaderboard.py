import streamlit as st
from utils.db import SessionLocal, User, ReadingLog
from utils.auth import require_login
from utils.gamification import calculate_streak, get_level
from sqlalchemy import func
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Leaderboard", page_icon="🏆", layout="wide")

require_login()

st.title("🏆 Class Leaderboard")

db = SessionLocal()

# Get all users with their stats
users = db.query(User).all()

leaderboard_data = []

for user in users:
    logs = db.query(ReadingLog).filter_by(user_id=user.id).all()
    
    total_pages = sum(log.pages_read or 0 for log in logs)
    total_minutes = sum(log.minutes_read or 0 for log in logs)
    log_dates = [log.date_read for log in logs]
    streak = calculate_streak(log_dates)
    level_info = get_level(total_pages)
    
    leaderboard_data.append({
        "name": user.name,
        "total_pages": total_pages,
        "total_minutes": total_minutes,
        "streak": streak,
        "level": level_info["level_name"],
        "books_logged": len(set([log.book_id for log in logs]))
    })

# Sort by total pages
leaderboard_data.sort(key=lambda x: x["total_pages"], reverse=True)

if not leaderboard_data:
    st.info("No reading data yet. Start logging your reading!")
else:
    # Top 3 podium
    st.subheader("🥇 Top Readers")
    
    if len(leaderboard_data) >= 3:
        col1, col2, col3 = st.columns(3)
        
        # 2nd place
        with col1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #C0C0C0 0%, #A8A8A8 100%); 
                        padding: 20px; border-radius: 15px; text-align: center;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
                <div style="font-size: 3em;">🥈</div>
                <div style="font-size: 1.5em; font-weight: bold; color: #2C3E50;">
                    {leaderboard_data[1]['name']}
                </div>
                <div style="font-size: 1.2em; color: #34495E; margin-top: 10px;">
                    {leaderboard_data[1]['total_pages']} pages
                </div>
                <div style="font-size: 0.9em; color: #7F8C8D;">
                    {leaderboard_data[1]['level']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # 1st place
        with col2:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); 
                        padding: 25px; border-radius: 15px; text-align: center;
                        box-shadow: 0 6px 12px rgba(0,0,0,0.3); margin-top: -10px;">
                <div style="font-size: 4em;">🥇</div>
                <div style="font-size: 1.8em; font-weight: bold; color: #8B4513;">
                    {leaderboard_data[0]['name']}
                </div>
                <div style="font-size: 1.5em; color: #654321; margin-top: 10px;">
                    {leaderboard_data[0]['total_pages']} pages
                </div>
                <div style="font-size: 1em; color: #A0522D;">
                    {leaderboard_data[0]['level']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # 3rd place
        with col3:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #CD7F32 0%, #B87333 100%); 
                        padding: 20px; border-radius: 15px; text-align: center;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
                <div style="font-size: 3em;">🥉</div>
                <div style="font-size: 1.5em; font-weight: bold; color: #2C3E50;">
                    {leaderboard_data[2]['name']}
                </div>
                <div style="font-size: 1.2em; color: #34495E; margin-top: 10px;">
                    {leaderboard_data[2]['total_pages']} pages
                </div>
                <div style="font-size: 0.9em; color: #7F8C8D;">
                    {leaderboard_data[2]['level']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Full leaderboard
    st.subheader("📊 Full Rankings")
    
    df = pd.DataFrame(leaderboard_data)
    df.index = df.index + 1  # Start ranking from 1
    
    # Display table
    st.dataframe(
        df[["name", "total_pages", "total_minutes", "streak", "level", "books_logged"]],
        column_config={
            "name": "Reader",
            "total_pages": st.column_config.NumberColumn("📖 Pages", format="%d"),
            "total_minutes": st.column_config.NumberColumn("⏱️ Minutes", format="%d"),
            "streak": st.column_config.NumberColumn("🔥 Streak", format="%d days"),
            "level": "Level",
            "books_logged": st.column_config.NumberColumn("📚 Books", format="%d")
        },
        use_container_width=True,
        hide_index=False
    )
    
    st.markdown("---")
    
    # Visualizations
    st.subheader("📈 Visual Rankings")
    
    tab1, tab2, tab3 = st.tabs(["Pages Read", "Reading Streaks", "Time Spent"])
    
    with tab1:
        fig = px.bar(
            df,
            x="name",
            y="total_pages",
            title="Total Pages Read by Reader",
            labels={"name": "Reader", "total_pages": "Pages Read"},
            color="total_pages",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        fig = px.bar(
            df,
            x="name",
            y="streak",
            title="Current Reading Streaks",
            labels={"name": "Reader", "streak": "Days"},
            color="streak",
            color_continuous_scale="Oranges"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        fig = px.bar(
            df,
            x="name",
            y="total_minutes",
            title="Total Reading Time",
            labels={"name": "Reader", "total_minutes": "Minutes"},
            color="total_minutes",
            color_continuous_scale="Greens"
        )
        st.plotly_chart(fig, use_container_width=True)

db.close()