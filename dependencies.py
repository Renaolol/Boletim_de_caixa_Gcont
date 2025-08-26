import streamlit as st
# Lê os dados do secrets.toml

db = st.secrets["db"]

DATABASE = db["database"]
HOST = db["host"]
USER = db["user"]
PASSWORD = db["password"]
PORT = db.get("port", 5432)
SSLMODE = db.get("sslmode", "require")
