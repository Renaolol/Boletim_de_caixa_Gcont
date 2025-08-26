import streamlit as st
from config_pag import get_logo, set_background


st.set_page_config(layout='wide')

get_logo()
set_background()
st.title("Boletim de Caixa Online Gcont")