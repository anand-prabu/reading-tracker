import streamlit as st

def level_greeting(level_name, name):
    tone = "A new chapter begins" if "Starter" in level_name else "Your reading rhythm is growing nicely" if "Explorer" in level_name else "Your bookshelf is getting impressive" if "Champion" in level_name else "Stories seem to follow you everywhere" if "Seeker" in level_name else "Your reading journey is inspiring the class"
    st.markdown(f'<div class="hero-card"><div style="text-transform:uppercase;letter-spacing:.12em;color:#6f6b63;font-size:.78rem">Welcome back</div><div style="font-size:2rem;line-height:1.1;margin-top:.25rem">Hi {name}.</div><p style="color:#6f6b63">{tone}.</p><span class="level-pill">{level_name}</span></div>', unsafe_allow_html=True)
