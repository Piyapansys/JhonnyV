import pyodbc
import time
import logging
from app.config import Config

logger = logging.getLogger(__name__)

# SQLSTATE codes that are safe to retry (transient network/Azure SQL issues)
_RETRYABLE_STATES = {
    '08S01',  # Communication link failure (most common Azure SQL drop)
    '08001',  # Unable to connect to data source
    '08003',  # Connection not open
    '08007',  # Connection failure during transaction
    'HYT00',  # Timeout expired
    'HYT01',  # Connection timeout expired
    '40001',  # Deadlock (also worth retrying)
    '40613',  # Azure SQL: database not currently available
}


def _is_retryable(error: pyodbc.Error) -> bool:
    args = error.args
    if args and isinstance(args[0], str):
        return args[0] in _RETRYABLE_STATES
    return False


def _make_connection() -> pyodbc.Connection:
    """Open a single raw pyodbc connection."""
    conn = pyodbc.connect(Config.SQL_SERVER_CONNECTION_STRING, timeout=30)
    conn.setdecoding(pyodbc.SQL_CHAR, encoding='cp874')
    conn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-16')
    conn.setencoding(encoding='utf-8')
    return conn


def get_db_connection(retries: int = 3, delay: float = 1.0):
    """
    Returns a pyodbc connection with retry logic for transient Azure SQL errors.
    Retries with exponential backoff on network/communication failures.
    """
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            return _make_connection()
        except pyodbc.Error as e:
            last_error = e
            sqlstate = e.args[0] if e.args else ''
            if _is_retryable(e) and attempt < retries:
                wait = delay * (2 ** (attempt - 1))  # 1s → 2s → 4s
                logger.warning(
                    f"DB connect attempt {attempt}/{retries} failed [{sqlstate}]. "
                    f"Retrying in {wait:.0f}s..."
                )
                time.sleep(wait)
            else:
                break

    logger.error(f"DB connection failed after {retries} attempts: {last_error}")
    return None


def execute_with_retry(conn, query_fn, retries: int = 2, delay: float = 1.0):
    """
    Execute a query function with retry on 08S01 communication link failures.
    
    Usage:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        def run(cursor):
            cursor.execute("SELECT ...")
            return cursor.fetchall()
        
        result = execute_with_retry(conn, run)
    
    If the connection drops mid-query, it reconnects and retries automatically.
    """
    last_error = None
    current_conn = conn

    for attempt in range(1, retries + 1):
        try:
            cursor = current_conn.cursor()
            try:
                result = query_fn(cursor)
                return result, cursor, current_conn
            finally:
                # Caller is responsible for closing cursor/conn
                # We just pass them back
                pass
        except pyodbc.Error as e:
            last_error = e
            sqlstate = e.args[0] if e.args else ''
            if _is_retryable(e) and attempt < retries:
                wait = delay * (2 ** (attempt - 1))
                logger.warning(
                    f"Query attempt {attempt}/{retries} failed [{sqlstate}] - reconnecting in {wait:.0f}s..."
                )
                time.sleep(wait)
                try:
                    current_conn.close()
                except Exception:
                    pass
                current_conn = _make_connection()
                if current_conn is None:
                    break
            else:
                raise  # Non-retryable or out of retries — let caller handle it

    raise last_error
