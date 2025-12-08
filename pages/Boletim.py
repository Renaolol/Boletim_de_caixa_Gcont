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
if username=="admin":
    empresa = st.text_input("empresa",0,width=300)
else:
    empresa = obter_empresa_codigo(user)

historico = get_historicos(empresa)
historicos_df = pd.DataFrame(historico,columns=["Descricao"])
conta = get_contas(empresa)
conta_df = pd.DataFrame(conta,columns=["id","Empresa","Conta","Cod_contabil","Tipo"])
contas_por_codigo = {
    row["Cod_contabil"]: f"{row['Conta']} ({row['Tipo']})" for _, row in conta_df.iterrows()
}
st.title(f"Boletim de caixa online - GCONT - {st.session_state.get('name')}")
st.divider()
portadores = pd.DataFrame(get_portador(empresa),columns=["id","empresa","nome_conta","cod_contabil"])
portador_labels = dict(zip(portadores["cod_contabil"], portadores["nome_conta"]))
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
col1,col2 = st.columns([1.5,3.5])
with col1:
    st.subheader("Novo lançamento")
    data = st.date_input("Data",width=300,format="DD/MM/YYYY")
    valor = st.number_input("Valor",width=300)
    historico = st.selectbox("Histórico",historicos_df["Descricao"],width=300)
    complemento = st.text_area("Complemento",width=300)
    cod_contabil = st.selectbox(
        "Conta",
        options=conta_df["Cod_contabil"],
        format_func=lambda codigo: f"{codigo} - {contas_por_codigo.get(codigo, '')}"
    )
    tipo = st.radio("Tipo",["Entrada","Saída"],horizontal=True)
    slv_lancto = st.button("Salvar Lançamento")
    if slv_lancto:
        if valor <=0:
            st.warning("Informe um valor")
        elif complemento =="":
            st.warning("Informe um Complemento de Histórico")
        else:    
            create_lancto(empresa,data,valor,historico,complemento,cod_contabil,tipo,portador_select)
            st.rerun()

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
        "Data": st.column_config.DateColumn("Data"),
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

st.divider()        
exportar = st.download_button("Exportar arquivo.txt",get_dominio(empresa,data_inicial,data_final),"Lancamentos_dominio.txt")
lista_lancto = get_list_lancto(empresa,data_inicial,data_final)
def gera_pdf(dominio:list):
    pdf = fpdf.FPDF(format='A4')
    pdf.add_page()
    pdf.set_font("Arial",size=9)
    pdf.multi_cell(200,10,"BOLETIM DE CAIXA")
    for x in dominio:
        y = (f"Data: {x[0].strftime('%d/%m/%Y')}| Conta: {x[2]} | Valor: {formata_valor(x[3])} | Historico: {x[4]} {x[5]} | Tipo: {x[6]}")
        pdf.multi_cell(200,10,y)   
    return bytes(pdf.output(dest="S").encode('latin-1'))

exportar_pdf = st.download_button(label="Baixar PDF", data=gera_pdf(lista_lancto),file_name="Boletim_de_caixa.pdf",mime="application/pdf")