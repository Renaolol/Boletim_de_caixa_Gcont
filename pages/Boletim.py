import streamlit as st
from config_pag import get_logo, set_background
import pandas as pd
import psycopg2 as pg
from datetime import date, datetime
from pathlib import Path
from auth_guard import require_login
from dependencies import *
from base64 import b64encode

st.set_page_config(layout='wide', initial_sidebar_state='collapsed')

get_logo()
set_background()
require_login()
username = (st.session_state.get("username") or "").lower()
user = (st.session_state.get('username'))
#Caso o usuário for Administrador, habilita um campo para digitar o código da empresa desejada. Se não for administrador pega o código pela função
if username=="admin":
    empresa = st.text_input("empresa",0,width=300)
else:
    empresa = obter_empresa_codigo(user)

#Primeiras buscar em relação a empresa selecionada: Históricos, Contas, e portadores.
historico = get_historicos(empresa)
historicos_df = pd.DataFrame(historico,columns=["Descricao"])
conta = get_contas(empresa)
conta_df = pd.DataFrame(conta,columns=["id","Empresa","Conta","Cod_contabil","Tipo"])
contas_por_codigo = {
    row["Cod_contabil"]: f"{row['Conta']} ({row['Tipo']})" for _, row in conta_df.iterrows()
}
portadores = pd.DataFrame(get_portador(empresa),columns=["id","empresa","nome_conta","cod_contabil"])
portador_labels = dict(zip(portadores["cod_contabil"], portadores["nome_conta"]))

#Cabeçalho
st.title(f"Boletim de caixa online - GCONT - {st.session_state.get('name')}")
st.divider()

#Caso a empresa estiver em algum desses códigos específicados muda a forma de selecionar o portador. Serve para empresas que possuem muitos portadores
if empresa in ["3","183","83","74","84",3,183,83,74,84]:
    portador_select = st.selectbox(
        "Selecione a conta a ser utilizada",
        options=portadores["cod_contabil"],
        format_func=lambda codigo: f"{codigo} - {portador_labels.get(codigo, '')}",
    )
else:    
    portador_select = st.radio(
        "Selecione a conta a ser utilizada",
        options=portadores["cod_contabil"],
        horizontal=True,
        format_func=lambda codigo: f"{codigo} - {portador_labels.get(codigo, '')}",
    )
#Coluna 1 se refere as informações sobre o lançamento a ser cadastrado
col1,col2 = st.columns([1.5,3.5])
if username=='consulta_apae':
    with col1:
        st.header("Usuário apenas de consultas")
    with col2:
        st.subheader("Lançamentos")
        coldata, coldata2, colespacamento = st.columns([1,1,5])
        with coldata:
            data_inicial = st.date_input("Data inicial",width=150,format="DD/MM/YYYY")
        with coldata2:
            data_final = st.date_input("Data final",width=150,format="DD/MM/YYYY")  
        lancto=get_lancto(empresa, portador_select)
        lancto_df = pd.DataFrame(
            lancto,
            columns=["Id","Data", "Valor", "Histórico", "Complemento", "Conta", "Tipo","Portador"],
        )

        if not lancto_df.empty:
            lancto_df["Data"] = pd.to_datetime(lancto_df["Data"],format="%d/%m/%Y")
            lancto_df = lancto_df.sort_values("Data", kind="mergesort")

            saldo_movimento = lancto_df["Valor"].where(
                lancto_df["Tipo"].str.lower() == "entrada",
                -lancto_df["Valor"],
            )
            lancto_df["Saldo"] = saldo_movimento.cumsum()
            lancto_df = lancto_df.sort_values("Data") 
            if not lancto_df.empty:
                lancto_df["Data"] = pd.to_datetime(lancto_df["Data"], format="%d/%m/%Y")

                inicio = pd.Timestamp(data_inicial)
                fim = pd.Timestamp(data_final)
                if inicio > fim:
                    st.warning("A data inicial não pode ser maior que a data final.")
                    lancto_df = lancto_df.iloc[0:0]
                else:
                    lancto_df = lancto_df.loc[lancto_df["Data"].between(inicio, fim)]
        try:            
            display_df = lancto_df.drop(columns=["Id"])
            display_df["Data"] = display_df["Data"].dt.strftime("%d/%m/%Y")
            display_df["Valor"] = display_df["Valor"].apply(formata_valor)
            display_df["Saldo"] = display_df["Saldo"].apply(formata_valor)    
            editor_df = lancto_df.copy()

            editor_df["Saldo"] = editor_df["Saldo"].apply(formata_valor)          # aceita DateColumn
            edited_df = st.data_editor(
            editor_df[["Id", "Data", "Valor", "Histórico", "Complemento", "Conta", "Tipo", "Saldo"]],
            hide_index=True,
            column_config={
                "Data": st.column_config.DateColumn("Data",format="DD/MM/YYYY"),
                "Valor": st.column_config.NumberColumn("Valor", format="%.2f"),
                "Saldo": st.column_config.NumberColumn("Saldo", disabled=True),
                "Id": st.column_config.TextColumn("Id", disabled=True),
            },
            key="lancto_editor",
            )
        except:
            st.info("Selecione datas que contenham lançamentos")        
else:
    with col1:
        st.subheader("Novo lançamento")
        data = st.date_input("Data",width=300,format="DD/MM/YYYY")
        valor = st.number_input("Valor",width=300)
        historico = st.selectbox("Histórico",historicos_df["Descricao"],width=300)
        complemento = st.text_area("Complemento",width=300)
        tipo = st.radio("Tipo",["Entrada","Saída","Depósito","Saque"],horizontal=True)
        if tipo in ["Depósito","Saque"]:
            cod_contabil = st.selectbox("Portador",portadores["cod_contabil"],format_func=lambda codigo: f"{codigo} - {portador_labels.get(codigo, '')}")
        elif tipo == "Entrada":
            cod_contabil = st.selectbox("Conta",options=conta_df[conta_df['Tipo']=="Receita"]["Cod_contabil"],format_func=lambda codigo: f"{codigo} - {contas_por_codigo.get(codigo, '')}")
        elif tipo == "Saída":
            cod_contabil = st.selectbox("Conta",options=conta_df[conta_df['Tipo']=="Despesas"]["Cod_contabil"],format_func=lambda codigo: f"{codigo} - {contas_por_codigo.get(codigo, '')}")
        else:    
            cod_contabil = st.selectbox(
                "Conta",
                options=conta_df["Cod_contabil"],
                format_func=lambda codigo: f"{codigo} - {contas_por_codigo.get(codigo, '')}"
            )
        
        slv_lancto = st.button("Salvar Lançamento")
        if slv_lancto:
            if valor <=0:
                st.warning("Informe um valor")
            elif complemento =="":
                st.warning("Informe um Complemento de Histórico")
            elif tipo == "Depósito":
                create_lancto_deposito(empresa,data,valor,historico,complemento,cod_contabil,portador_select)
            elif tipo == "Saque":
                create_lancto_saque(empresa,data,valor,historico,complemento,cod_contabil,portador_select)       
            else:    
                create_lancto(empresa,data,valor,historico,complemento,cod_contabil,tipo,portador_select)
                st.rerun()
#Coluna 2 faz a busca e mostra os lançamentos que foram feitos
    with col2:
        st.subheader("Lançamentos")
        coldata, coldata2, colespacamento = st.columns([1,1,5])
        with coldata:
            data_inicial = st.date_input("Data inicial",width=150,format="DD/MM/YYYY")
        with coldata2:
            data_final = st.date_input("Data final",width=150,format="DD/MM/YYYY")  
        lancto=get_lancto(empresa, portador_select)
        lancto_df = pd.DataFrame(
            lancto,
            columns=["Id","Data", "Valor", "Histórico", "Complemento", "Conta", "Tipo","Portador"],
        )

        if not lancto_df.empty:
            lancto_df["Data"] = pd.to_datetime(lancto_df["Data"],format="%d/%m/%Y")
            lancto_df = lancto_df.sort_values("Data", kind="mergesort")

            saldo_movimento = lancto_df["Valor"].where(
                lancto_df["Tipo"].str.lower() == "entrada",
                -lancto_df["Valor"],
            )
            lancto_df["Saldo"] = saldo_movimento.cumsum()
            lancto_df = lancto_df.sort_values("Data") 
            if not lancto_df.empty:
                lancto_df["Data"] = pd.to_datetime(lancto_df["Data"], format="%d/%m/%Y")

                inicio = pd.Timestamp(data_inicial)
                fim = pd.Timestamp(data_final)
                if inicio > fim:
                    st.warning("A data inicial não pode ser maior que a data final.")
                    lancto_df = lancto_df.iloc[0:0]
                else:
                    lancto_df = lancto_df.loc[lancto_df["Data"].between(inicio, fim)]
        try:            
            display_df = lancto_df.drop(columns=["Id"])
            display_df["Data"] = display_df["Data"].dt.strftime("%d/%m/%Y")
            display_df["Valor"] = display_df["Valor"].apply(formata_valor)
            display_df["Saldo"] = display_df["Saldo"].apply(formata_valor)    
            editor_df = lancto_df.copy()

            editor_df["Saldo"] = editor_df["Saldo"].apply(formata_valor)          # aceita DateColumn
            edited_df = st.data_editor(
            editor_df[["Id", "Data", "Valor", "Histórico", "Complemento", "Conta", "Tipo", "Saldo"]],
            hide_index=True,
            column_config={
                "Data": st.column_config.DateColumn("Data",format="DD/MM/YYYY"),
                "Valor": st.column_config.NumberColumn("Valor", format="%.2f"),
                "Saldo": st.column_config.NumberColumn("Saldo", disabled=True),
                "Id": st.column_config.TextColumn("Id", disabled=True),
            },
            key="lancto_editor",
            )
            
            if st.button("Salvar alterações"):    
                base = lancto_df.set_index("Id")
                edits = edited_df.set_index("Id")
                mudou = edits.compare(base, keep_shape=False)
                ids_alterados = mudou.index.unique()

                for lancto_id in ids_alterados:
                    registro = edits.loc[lancto_id]
                    update_lancto(
                        int(lancto_id),                       # ← força int nativo
                        registro["Data"],                     # já virou date no editor
                        float(registro["Valor"]),             # float Python
                        registro["Histórico"],
                        registro["Complemento"],
                        str(registro["Conta"]),               # ou int(...) se for numérico
                        registro["Tipo"],
                    )
                if len(ids_alterados) > 0:
                    st.success("Atualizações salvas.")
                    st.rerun()
                else:
                    st.info("Nenhuma alteração detectada.")
            selecionados = st.multiselect(
                "Selecione os lançamentos para excluir",
                options=lancto_df["Id"], 
                format_func=lambda row_id: (
                    f"{lancto_df.loc[lancto_df['Id'] == row_id, 'Data'].iloc[0]:%d/%m/%Y} "
                    f"- {lancto_df.loc[lancto_df['Id'] == row_id, 'Histórico'].iloc[0]} "
                    f"- {lancto_df.loc[lancto_df['Id'] == row_id, 'Complemento'].iloc[0]}"
                    f"- {lancto_df.loc[lancto_df['Id'] == row_id, 'Valor'].iloc[0]:.2f}"
                ),
            )
            if st.button("Excluir selecionados") and selecionados:
                delete_lancto(selecionados)
                st.success("Lançamentos removidos.")
                st.rerun()
        except:
            st.info("Selecione datas que contenham lançamentos")
        st.divider()           
exportar = st.download_button("Exportar arquivo.txt",get_dominio(empresa,data_inicial,data_final),"Lancamentos_dominio.txt")
lista_lancto = get_list_lancto(empresa,data_inicial,data_final)
exportar_pdf = st.download_button(label="Baixar PDF", data=gera_pdf_df(display_df),file_name="Boletim_de_caixa.pdf",mime="application/pdf")

st.divider()
st.header('Relatório de contas')

lista_receitas = retorna_lanctos_receitas(empresa,data_inicial,data_final)
with st.expander("Receitas"):
    for x in lista_receitas:
        st.write(x[0], formata_valor(x[1]))
lista_despesas = retorna_lanctos_despesa(empresa,data_inicial,data_final)
with st.expander("Despesas"):
    for x in lista_despesas:
        st.write(x[0],formata_valor(x[1]))
