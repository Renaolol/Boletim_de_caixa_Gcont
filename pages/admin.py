import streamlit as st
from time import sleep
from config_pag import set_background, get_logo
from dependencies import cadastra_clientes ,get_clientes, get_historicos, cadastra_historico,create_conta,get_contas
get_logo()
set_background()
st.title("Página de Administração")
col_cadastro, col_clientes = st.columns([1,2])
with col_cadastro:
    nome= st.text_input("Insira o nome do cliente a ser cadastrado: ",width=300)
    cod = st.number_input("Insira o código do cliente disponível na domínio: ",width=300,step=0)
    cnpj = st.number_input("Insira o CNPJ do cliente (Somente números)",width=300, step=0)
    salvar = st.button("Salvar Cliente")    
    if salvar:
        cadastra_clientes(nome,cod,cnpj)
        st.success("Cliente salvo com sucesso!")
        sleep(1)
        st.rerun()

    empresa = st.text_input("Informe o código do cliente",1,width=300)
with col_clientes:
    clientes=get_clientes()
    st.dataframe(clientes)    
st.divider()
col1,col2 = st.columns(2)
with col1:
    historicos = get_historicos(empresa)
    st.dataframe(historicos)
with col2:
    desc_historico = st.text_area("Informe a descrição do histórico: ")
    cod_conta = st.text_input("Informe o código contabil da conta")

    slv_hist = st.button("Salvar Histórico")
    if slv_hist:
        cadastra_historico(empresa,desc_historico,cod_conta)
        st.success("Histórico Salvo com sucesso!")
        sleep(1)
        st.rerun()    

st.divider()
col3,col4 = st.columns(2)
with col3:
    nome_conta = st.text_input("Insira o nome da conta desejada: ")
    cod_contabil = st.text_input("Insira o código da conta: ")
    tipo = st.selectbox("Selecione o tipo da conta:",options=["Receita","Despesas"])
    salvar_conta = st.button("Salvar conta")
    if salvar_conta:
        create_conta(empresa, nome_conta, cod_contabil, tipo)
        st.success("Conta criada com sucesso!")
        sleep(1)
        st.rerun()
with col4:
    contas_contabeis=get_contas(empresa)
    st.dataframe(contas_contabeis)

st.divider()    