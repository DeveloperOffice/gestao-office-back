import pyodbc
from django.conf import settings

def connect_odbc():
    """Cria a conexão com o banco via ODBC, pegando as credenciais do settings"""
    driver = settings.ODBC_DRIVER  # Correto, sem ()
    server = settings.ODBC_SERVER
    database = settings.ODBC_DATABASE
    user = settings.ODBC_USER
    password = settings.ODBC_PASSWORD

    conn_str = f"DRIVER={driver};ServerName={server};DatabaseName={database};UID={user};PWD={password}"
    
    conn = pyodbc.connect(conn_str, autocommit=True)
    return conn

def fetch_data(query):
    """Executes a SQL query and returns the results as a list of objects"""
    conn = connect_odbc()
    cursor = conn.cursor()
    cursor.execute(query)

    columns = [col[0] for col in cursor.description]  # Get column names
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]  # Convert to dictionary

    conn.close()
    return results  # Returns a list of objects
