import streamlit as st
from utils.db import init_db, SessionLocal, get_or_create_user, get_user_stats
from utils.auth import get_login_url, fetch_user_info, is_logged_in, get_current_user, logout
from utils.gamification import get_level, calculate_streak, BADGES, get_level_greeting
from datetime import datetime

st.set_page_config(
    page_title="Reading Tracker",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #8B4513;
        font-size: 3em;
        margin-bottom: 0;
    }
    .subtitle {
        text-align: center;
        color: #A0522D;
        font-size: 1.2em;
        margin-top: 0;
    }
    .stat-card {
        background: linear-gradient(135deg, #FFF8DC 0%, #F5DEB3 100%);
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #DEB887;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .level-badge {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        padding: 15px 25px;
        border-radius: 25px;
        text-align: center;
        font-size: 1.5em;
        font-weight: bold;
        color: #8B4513;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize DB
init_db()

# DEBUG MODE - Remove after testing
DEBUG = False

# Handle OAuth callback - CHECK THIS FIRST
query_params = st.query_params

if DEBUG:
    with st.expander("🔍 Debug Info (Remove after testing)"):
        st.write("**Query Params:**", dict(query_params))
        st.write("**Session State:**", dict(st.session_state))
        st.write("**Is Logged In:**", is_logged_in())

# Process OAuth callback
if "code" in query_params:
    st.info("🔄 Processing login callback...")
    
    try:
        code = query_params["code"]
        st.write(f"✅ Received OAuth code: {code[:10]}...")
        
        # Fetch user info from Google
        st.write("📡 Fetching user info from Google...")
        user_info = fetch_user_info(code)
        st.write(f"✅ Got user info: {user_info.get('email')}")
        
        # Create or get user from database
        st.write("💾 Creating/updating user in database...")
        db = SessionLocal()
        user = get_or_create_user(
            email=user_info.get("email"),
            name=user_info.get("name"),
            db_session=db
        )
        db.close()
        
        st.write(f"✅ User created/found: {user.name} (ID: {user.id})")
        
        # Store user in session state
        st.session_state["user"] = user
        st.session_state["logged_in"] = True
        
        st.success(f"✅ Login successful! Welcome, {user.name}!")
        st.write("🔄 Redirecting to dashboard...")
        
        # Clear query params
        st.query_params.clear()
        
        # Force rerun
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Login failed: {str(e)}")
        st.exception(e)
        st.write("---")
        if st.button("Clear and Try Again"):
            st.query_params.clear()
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        st.stop()

# Main App
st.markdown('<h1 class="main-title">📚 Reading Tracker</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Track your reading journey, earn badges, and level up!</p>', unsafe_allow_html=True)

if not is_logged_in():
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("👋 Welcome! Please log in to start tracking your reading adventure.")
        
        # Get login URL
        try:
            login_url = get_login_url()
            
            if DEBUG:
                st.code(login_url, language=None)
            
            # Display login button with direct link
            st.markdown(
                f"""
                <div style="text-align: center; margin: 20px 0;">
                    <a href="{login_url}" target="_self" style="text-decoration: none;">
                        <button style="
                            background: linear-gradient(135deg, #4285f4 0%, #34a853 100%);
                            color: white;
                            padding: 15px 40px;
                            border: none;
                            border-radius: 10px;
                            font-size: 18px;
                            font-weight: bold;
                            cursor: pointer;
                            width: 100%;
                            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                            transition: transform 0.2s;
                        " onmouseover="this.style.transform='scale(1.05)'" 
                           onmouseout="this.style.transform='scale(1)'">
                            🔐 Login with Google
                        </button>
                    </a>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown("---")
            st.caption("🔒 Secure login powered by Google OAuth")
            
        except Exception as e:
            st.error(f"Configuration error: {str(e)}")
            st.exception(e)
        
else:
    user = get_current_user()
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {user.name}")
        st.caption(f"📧 {user.email}")
        st.caption(f"🎭 Role: **{user.role.capitalize()}**")
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            logout()
    
    # Get user stats
    db = SessionLocal()
    stats = get_user_stats(user.id, db)
    
    # Get reading logs for streak calculation
    from utils.db import ReadingLog
    logs = db.query(ReadingLog).filter_by(user_id=user.id).all()
    log_dates = [log.date_read for log in logs]
    streak = calculate_streak(log_dates)
    
    # Get badges
    from utils.db import Badge
    user_badges = db.query(Badge).filter_by(user_id=user.id).all()
    badge_names = [b.badge_name for b in user_badges]
    
    db.close()
    
    # Level info
    level_info = get_level(stats["total_pages"])
    greeting = get_level_greeting(level_info["level_name"], user.name)
    
    # Display greeting
    st.markdown(f'<div class="level-badge">{level_info["level_name"]}</div>', unsafe_allow_html=True)
    st.success(greeting)
    
    # Progress to next level
    if not level_info["is_max_level"]:
        progress = level_info["pages_in_level"] / (level_info["pages_in_level"] + level_info["pages_to_next"])
        st.progress(progress)
        st.info(f"📖 **{level_info['pages_to_next']} pages** until **{level_info['next_level_name']}**!")
    else:
        st.balloons()
        st.success("🎉 You've reached the maximum level! You're a true reading champion!")
    
    st.markdown("---")
    
    # Stats Dashboard
    st.subheader("📊 Your Reading Stats")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <h2 style="text-align: center; margin: 0;">📖</h2>
            <h3 style="text-align: center; margin: 5px 0;">{stats['total_pages']}</h3>
            <p style="text-align: center; margin: 0; color: #8B4513;">Total Pages</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <h2 style="text-align: center; margin: 0;">⏱️</h2>
            <h3 style="text-align: center; margin: 5px 0;">{stats['total_minutes']}</h3>
            <p style="text-align: center; margin: 0; color: #8B4513;">Minutes Read</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <h2 style="text-align: center; margin: 0;">🔥</h2>
            <h3 style="text-align: center; margin: 5px 0;">{streak}</h3>
            <p style="text-align: center; margin: 0; color: #8B4513;">Day Streak</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <h2 style="text-align: center; margin: 0;">✅</h2>
            <h3 style="text-align: center; margin: 5px 0;">{stats['books_completed']}</h3>
            <p style="text-align: center; margin: 0; color: #8B4513;">Books Done</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Badges
    st.subheader("🏆 Your Badges")
    
    if badge_names:
        badge_cols = st.columns(min(len(badge_names), 4))
        for idx, badge_key in enumerate(badge_names):
            with badge_cols[idx % 4]:
                badge_info = BADGES.get(badge_key, {"name": "Unknown", "desc": ""})
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
                    padding: 15px;
                    border-radius: 10px;
                    text-align: center;
                    margin: 5px 0;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                ">
                    <div style="font-size: 2em;">{badge_info['name'].split()[0]}</div>
                    <div style="font-size: 0.9em; color: #8B4513; font-weight: bold;">
                        {' '.join(badge_info['name'].split()[1:])}
                    </div>
                    <div style="font-size: 0.8em; color: #654321; margin-top: 5px;">
                        {badge_info['desc']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("🎯 Start reading to earn your first badge!")
    
    st.markdown("---")
    
    # Quick Actions
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📚 My Bookshelf", use_container_width=True):
            st.switch_page("pages/1_📚_My_Bookshelf.py")
    
    with col2:
        if st.button("✍️ Log Reading", use_container_width=True):
            st.switch_page("pages/2_✍️_Log_Reading.py")
    
    with col3:
        if st.button("🏆 Leaderboard", use_container_width=True):
            st.switch_page("pages/3_🏆_Leaderboard.py")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #A0522D; padding: 20px;">
            <p>📚 Reading Tracker v1.0 | Made with ❤️ using Streamlit</p>
        </div>
        """,
        unsafe_allow_html=True
    )