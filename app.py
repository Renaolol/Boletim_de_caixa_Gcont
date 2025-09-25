import streamlit as st
from config_pag import get_logo, set_background
import pandas as pd
import psycopg2 as pg

st.set_page_config(layout='wide', initial_sidebar_state='collapsed')

get_logo()
set_background()

st.title("Boletim de Caixa Online Gcont")
options_select = ["Caixa","Sicoob","Sicredi","Bradesco"]
tipo_lancto=st.radio("Selecione o tipo de lançamento", options=["Entrada","Saída"])
contas_receitas = [
    "Receita de Vendas de Mercadorias",
    "Receita de Prestação de Serviços",
    "Receita de Vendas de Produtos",
    "Receita de Juros Ativos",
    "Receita de Descontos Obtidos",
    "Receita de Aluguéis",
    "Receita de Royalties",
    "Receita de Dividendos",
    "Receita Financeira",
    "Outras Receitas Operacionais",
    "Receita Não Operacional"
]

contas_despesas = [
    "Despesas com Salários",
    "Despesas com Encargos Sociais",
    "Despesas com Aluguel",
    "Despesas com Energia Elétrica",
    "Despesas com Água e Esgoto",
    "Despesas com Telefone e Internet",
    "Despesas com Material de Escritório",
    "Despesas com Transporte",
    "Despesas com Manutenção e Conservação",
    "Despesas com Publicidade e Propaganda",
    "Despesas Bancárias",
    "Despesas com Viagens",
    "Despesas com Honorários Contábeis",
    "Despesas com Seguros",
    "Despesas com Depreciação",
    "Despesas Diversas"
]

hist_padrao = [
    "Pagamento de Fornecedor",
    "Recebimento de Cliente",
    "Depósito Bancário",
    "Transferência",
    "Outros"
]

if tipo_lancto == "Entrada":
    conta = st.selectbox("Selecione uma conta", options=contas_receitas, width = 300)
else:
    conta = st.selectbox("Selecione uma conta", options=contas_despesas, width = 300)

select = st.segmented_control("Selecione a devida conta para receber a movimentação",options=options_select)
col1,col2 = st.columns(2)


with col1:
    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        valor = st.number_input("Digite o valor do lançamento: ")
        num_doc = st.text_input("Digite o número do documento")
    with sub_col2:
        hist = st.selectbox("Selecione o Histórico Padrão: ", options=hist_padrao)
        comp_hist = st.text_area("Complemento de Histórico")
    salvar=st.button("Salvar Lançamento")

lanctos=[]
with col2:
    if salvar:
        lanctos=([valor,num_doc,hist,comp_hist])
        st.dataframe(lanctos)