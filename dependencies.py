import psycopg2
import streamlit as st
from contextlib import contextmanager
from decimal import Decimal, InvalidOperation
import pandas as pd
from datetime import date, datetime
from pathlib import Path

# db = st.secrets["db"]

# DATABASE = db["database"]
# HOST = db["host"]
# USER = db["user"]
# PASSWORD = db["password"]
# PORT = db.get("port", 5432)
# SSLMODE = db.get("sslmode", "require")

# @contextmanager
# def instance_cursor():
#     connection = psycopg2.connect(
#         database=DATABASE,
#         host=HOST,
#         user=USER,
#         password=PASSWORD,
#         port=PORT,
#         sslmode=SSLMODE,
#         connect_timeout=10,
#     )
#     cursor = connection.cursor()
#     try:
#         yield cursor
#         connection.commit()
#     finally:
#         cursor.close()
#         connection.close()

# def consulta_associacoes():
#     with instance_cursor() as cursor:
#         cursor.execute("""
#             SELECT nome, usuario, senha, cod_empresa
#             FROM Associacoes
#             ORDER BY nome
#         """)
#         return cursor.fetchall()
db_config = {
    "host":"localhost",
    "dbname":"boletimcaixa",
    "user":"postgres",
    "password":"0176",
    "port":"5432"
}
def conecta_banco():
    return psycopg2.connect(**db_config)

def get_clientes():
    conn= conecta_banco()
    cursor = conn.cursor()
    query="""
    SELECT nome, codigo, cnpj
    FROM clientes
    """
    cursor.execute(query, )
    clientes = cursor.fetchall()
    cursor.close()
    conn.close()
    return clientes

def cadastra_clientes (nome,codigo,cnpj):
    conn = conecta_banco()
    cursor = conn.cursor()
    query="""
    INSERT INTO clientes(nome,codigo,cnpj)
    VALUES(%s,%s,%s)
"""
    cursor.execute(query, (nome,codigo,cnpj))
    conn.commit()
    cursor.close()
    conn.close()

    return("Cliente cadastrado")


def cadastra_historico (cliente,descricao,cod_conta):
    conn=conecta_banco()
    cursor = conn.cursor()
    query = """
        INSERT INTO historicos(cliente, descricao, cod_conta)
        VALUES (%s,%s,%s)
        """
    cursor.execute(query, (cliente,descricao,cod_conta))
    conn.commit()
    cursor.close()
    conn.close()
    return

def get_historicos(empresa):
    conn = conecta_banco()
    cursor = conn.cursor()
    query="""
        SELECT descricao
        FROM historicos
        WHERE cliente = %s
    """
    cursor.execute(query, (empresa,))
    historicos = cursor.fetchall()
    cursor.close()
    conn.close()
    return historicos  

def create_conta(empresa, conta, cod_contabil, tipo):
    conn = conecta_banco()
    cursor = conn.cursor()
    query="""
    INSERT INTO contas(empresa,conta,cod_contabil,tipo)
    VALUES (%s,%s,%s,%s)
    """
    cursor.execute(query, (empresa, conta, cod_contabil, tipo))
    conn.commit()
    cursor.close()
    conn.close()
    return

def get_contas(empresa):
    conn=conecta_banco()
    cursor=conn.cursor()
    query="""
    SELECT empresa, conta,cod_contabil,tipo
    FROM contas
    WHERE empresa = %s
    """  
    cursor.execute(query, (empresa, ))
    contas = cursor.fetchall()
    cursor.close()
    conn.close()
    return contas

def create_lancto(empresa,data,valor,historico,complemento,conta,tipo):
    conn = conecta_banco()
    cursor=conn.cursor()
    query="""
    INSERT INTO movimentacoes(empresa,data_mov,valor,historico,complemento,conta,tipo)
    VALUES (%s,%s,%s,%s,%s,%s,%s)
    """
    cursor.execute(query, (empresa,data,valor,historico,complemento,conta,tipo))
    conn.commit()
    cursor.close()
    conn.close()
    return

def get_lancto(empresa):
    conn=conecta_banco()
    cursor=conn.cursor()
    query="""
        SELECT id, data_mov, valor, historico, complemento, conta, tipo
        FROM movimentacoes
        WHERE empresa = %s
        ORDER BY data_mov
    """  
    cursor.execute(query, (empresa, ))
    lancto = cursor.fetchall()
    cursor.close()
    conn.close()
    return lancto

def delete_lancto(ids):
    conn = conecta_banco()
    cursor = conn.cursor()
    query = "DELETE FROM movimentacoes WHERE id = ANY(%s)"
    cursor.execute(query, (list(ids),))
    conn.commit()
    cursor.close()
    conn.close()

def formata_valor(valor):
    if valor is None or (hasattr(valor, "__float__") and pd.isna(valor)):
        return "R$ 0,00"

    try:
        quantia = Decimal(str(valor))
    except (InvalidOperation, ValueError, TypeError):
        return "R$ 0,00"

    sinal = "-" if quantia < 0 else ""
    quantia = abs(quantia)

    bruto = f"{quantia:,.2f}"
    bruto = bruto.replace(",", "_").replace(".", ",").replace("_", ".")

    return f"{sinal}R$ {bruto}"
def update_lancto(lancto_id, data, valor, historico, complemento, conta, tipo):
    conn = conecta_banco()
    cursor = conn.cursor()
    query = """
        UPDATE movimentacoes
        SET data_mov = %s,
            valor = %s,
            historico = %s,
            complemento = %s,
            conta = %s,
            tipo = %s
        WHERE id = %s
    """
    cursor.execute(query, (data, valor, historico, complemento, conta, tipo, lancto_id))
    conn.commit()
    cursor.close()
    conn.close()

def get_dominio(empresa):
    conn = conecta_banco()
    cursor = conn.cursor()
    query = """
        SELECT data_mov, conta, valor, historico, complemento, tipo
        FROM movimentacoes
        WHERE empresa = %s
        ORDER BY data_mov
    """
    cursor.execute(query, (empresa,))
    dominio = cursor.fetchall()
    cursor.close()
    conn.close()

    if not dominio:
        return ""

    dominio_df = pd.DataFrame(
        dominio,
        columns=["Data", "Conta", "Valor", "Historico", "Complemento", "Tipo"],
    )

    linhas = []

    for _, row in dominio_df.iterrows():
        data_valor = row["Data"]
        if isinstance(data_valor, (datetime, date)):
            data_fmt = data_valor.strftime("%d/%m/%Y")
        else:
            data_fmt = str(data_valor)

        descricao = " ".join(filter(None, [row["Historico"], row["Complemento"]])).strip()
        valor_fmt = f"{float(row['Valor']):.2f}"

        if str(row["Tipo"]).lower() == "entrada":
            linha = (
                "|6000|X||||\n"
                f"|6100|{data_fmt}|5|{row['Conta']}|{valor_fmt}||{descricao}||||"
            )
        else:
            linha = (
                "|6000|X||||\n"
                f"|6100|{data_fmt}|{row['Conta']}|5|{valor_fmt}||{descricao}||||"
            )
        linhas.append(linha)
        
    saida = "\n".join(linhas)
    return saida
