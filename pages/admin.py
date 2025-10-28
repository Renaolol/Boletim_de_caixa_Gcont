import streamlit as st
from time import sleep
from config_pag import set_background, get_logo
from auth_guard import require_login
from dependencies import cadastra_clientes ,get_clientes, get_historicos, cadastra_historico,create_conta,get_contas, update_conta
import pandas as pd
get_logo()
set_background()
require_login()

username = (st.session_state.get("username") or "").lower()

if username=="admin":
    st.title("Página de Administração",help="Disclaimer: BANCO DE DADOS CONECTADO É O FÍSICO.")
    col_cadastro, col_clientes = st.columns([1,2])
    with col_cadastro:
        nome= st.text_input("Insira o nome do cliente a ser cadastrado: ",width=300)
        cod = st.number_input("Insira o código do cliente disponível na domínio: ",width=300,step=0)
        cnpj = st.number_input("Insira o CNPJ do cliente (Somente números)",width=300, step=0)
        user = st.text_input("Insira o usuário para Login",width=300)
        senha = st.text_input("Insira a Senha do usuário: ",width=300)
        salvar = st.button("Salvar Cliente")    
        if salvar:
            cadastra_clientes(nome,cod,cnpj,(user.lower()),senha)
            st.success("Cliente salvo com sucesso!")
            sleep(1)
            st.rerun()
        st.divider()
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
        cod_conta = None

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
        contas_contabeis_list=get_contas(empresa)
        contas_contabeis = pd.DataFrame(contas_contabeis_list,columns=["id","Empresa","Nome Conta","Código Contábil","Tipo"])
        edited_df = st.data_editor(contas_contabeis[["id","Empresa","Nome Conta","Código Contábil","Tipo"]],hide_index=True,column_config={})
        atualizar_conta = st.button("Atualizar conta")
        if atualizar_conta: 
            base = contas_contabeis.set_index("id")
            edits = edited_df.set_index("id")
            change = edits.compare(base, keep_shape=False) 
            ids_alterados = change.index.unique()

            for lancto_id in ids_alterados:
                registro = edits.loc[lancto_id]
                update_conta(
                    int(lancto_id),
                    int(registro["Empresa"]),
                    registro["Nome Conta"],
                    int(registro["Código Contábil"]),
                    registro["Tipo"]
                )
            if len(ids_alterados) > 0:
                st.sucess("Atualização Salva")
                st.rerun()
            else:
                st.info("Nenhuma alteração detectada.")        
    st.divider()
else:
    st.warning("Acesso restrito para administradores")        