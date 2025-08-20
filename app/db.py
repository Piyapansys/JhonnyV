import pyodbc
from app.config import Config

def get_db_connection():
    try:
        conn = pyodbc.connect(Config.SQL_SERVER_CONNECTION_STRING)
        return conn
    except pyodbc.Error as e:
        print(f"Error connecting to the database: {e}")
        return None
