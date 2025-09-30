# auth_guard.py
import streamlit as st

def require_login(home_page: str = "Login.py"):
    if st.session_state.get("authentication_status") is True:
        return
    st.info("Área restrita. Faça login para continuar.")
    try:
        st.switch_page(home_page)  # precisa Streamlit recente
    except Exception:
        st.stop()  # fallback