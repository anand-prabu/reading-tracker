import streamlit as st
import httpx
from authlib.integrations.httpx_client import OAuth2Client

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

def get_oauth_client():
    return OAuth2Client(
        client_id=st.secrets["google"]["client_id"],
        client_secret=st.secrets["google"]["client_secret"],
        redirect_uri=st.secrets["auth"]["redirect_uri"],
        scope="openid email profile",
    )

def get_login_url():
    client = get_oauth_client()
    uri, state = client.create_authorization_url(GOOGLE_AUTH_URL)
    st.session_state["oauth_state"] = state
    return uri

def fetch_user_info(code: str) -> dict:
    try:
        client = get_oauth_client()
        
        # Fetch token
        token = client.fetch_token(
            GOOGLE_TOKEN_URL,
            code=code,
        )
        
        # Get user info
        resp = client.get(GOOGLE_USERINFO_URL)
        resp.raise_for_status()
        
        return resp.json()
    except Exception as e:
        st.error(f"Error fetching user info: {str(e)}")
        raise

def is_logged_in() -> bool:
    return "user" in st.session_state and st.session_state["user"] is not None

def get_current_user():
    return st.session_state.get("user", None)

def is_admin() -> bool:
    user = get_current_user()
    if user is None:
        return False
    return user.role == "admin"

def require_login():
    """Call at top of each page to enforce login."""
    if not is_logged_in():
        st.warning("Please log in to continue.")
        st.stop()

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()