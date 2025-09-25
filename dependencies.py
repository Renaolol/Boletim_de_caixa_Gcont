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
    SELECT nome
    FROM clientes
    """
    cursor.execute(query, )
    cursor.fetchall