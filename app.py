import streamlit as st
from config_pag import get_logo, set_background
import pandas as pd
import psycopg2 as pg

st.set_page_config(layout='wide', initial_sidebar_state='collapsed')

get_logo()
set_background()

st.title("Boletim de caixa online - GCONT")