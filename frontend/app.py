import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

st.set_page_config(page_title="Collabook", page_icon="📖")

st.title("Collabook 📖")
st.write("Welcome to the collaborative story generation platform.")

try:
    res = requests.get(f"{BACKEND_URL}/")
    if res.status_code == 200:
        st.success(f"Backend connected: {res.json()['message']}")
    else:
        st.error("Backend returned an error.")
except Exception as e:
    st.error(f"Could not connect to backend: {e}")
