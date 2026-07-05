import streamlit as st

def apply_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Literata:wght@400;600;700&family=Inter:wght@400;500;600;700&display=swap');
    .stApp {background: linear-gradient(180deg, #f8f6f1 0%, #f4efe7 100%); color: #28251d;}
    html, body, [class*="css"] {font-family: 'Inter', sans-serif;}
    h1, h2, h3 {font-family: 'Literata', serif;}
    .hero-card,.shelf-card,.badge-card {background: rgba(255,255,255,.86); border:1px solid rgba(40,37,29,.12); border-radius: 20px; box-shadow: 0 12px 30px rgba(40,37,29,.08); padding: 1rem;}
    .book-cover {min-height:170px; border-radius:16px; background: linear-gradient(180deg, #1e4d4f, #16383a); color:white; padding:1rem; display:flex; flex-direction:column; justify-content:space-between;}
    .shelf-wood{height:16px; background: linear-gradient(180deg, #b78655, #8b5e34); border-radius:999px; margin-top:-.2rem;}
    .level-pill{display:inline-block; padding:.3rem .7rem; border-radius:999px; background:#dbeaea; color:#01696f; font-weight:700;}
    </style>""", unsafe_allow_html=True)
