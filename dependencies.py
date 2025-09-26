import psycopg2
import streamlit as st
from contextlib import contextmanager

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
    SELECT nome, codigo
    FROM clientes
    """
    cursor.execute(query, )
    clientes = cursor.fetchall()
    cursor.close()
    conn.close()
    return clientes

def cadastra_clientes (nome,codigo):
    conn = conecta_banco()
    cursor = conn.cursor()
    query="""
    INSERT INTO clientes(nome,codigo)
    VALUES(%s,%s)
"""
    cursor.execute(query, (nome,codigo))
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
        SELECT cliente, descricao, cod_conta
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

