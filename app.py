import streamlit as st
from config_pag import get_logo, set_background
import pandas as pd
import psycopg2 as pg



st.set_page_config(layout='wide')

get_logo()
set_background()
st.title("Boletim de Caixa Online Gcont")
options_select = ["Caixa","Sicoob","Sicredi","Bradesco"]
select = st.segmented_control("Selecione a devida conta para receber a movimentação",options=options_select)
hist_padrao = ["Selecione o histórico padrão","Pagamento NF-e Num ", "Pagamento NFC-e "]
col1,col2 = st.columns(2)

# Bloco de Funções
def salvar_lancto (valor, num_doc,hist,comp_hist,tipo_lancto):
    
    pass


with col1:
    if select == "Caixa":
        sub_col1,sub_col2 = st.columns(2)
        with sub_col1:
            valor=st.number_input("Digite o valor do lançamento: ")
            num_doc = st.text_input("Digite o número do documento")
        with sub_col2:    
            hist = st.selectbox("Selecione o Histórico Padrão: ",options=hist_padrao)
            comp_hist = st.text_area("Complemento de Histórico")
    tipo_lancto=st.radio("Selecione o tipo de lançamento", options=["Entrada","Saída"])        
    st.button("Salvar Lançamento")

with col2:
    pass