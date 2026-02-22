# app/database/connection.py

import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

# =========================================================
# Connection Pool (lazy-initialized)
# =========================================================
_connection_pool = None


def _get_pool():
    """
    Returns the shared connection pool, creating it on first call.
    Uses a ThreadedConnectionPool for thread-safe access.
    """
    global _connection_pool

    if _connection_pool is None:
        database_url = os.getenv("DATABASE_URL")

        if not database_url:
            raise ValueError("DATABASE_URL not set in environment variables")

        try:
            _connection_pool = pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=database_url,
                sslmode="require",
                connect_timeout=10  # Fail fast instead of hanging
            )
        except Exception as e:
            raise RuntimeError(f"Database connection pool creation failed: {e}")

    return _connection_pool


def get_connection():
    """
    Returns a connection from the pool.

    IMPORTANT: Caller must return the connection when done by calling
    return_connection(conn) or conn.close() — pool.putconn is aliased.
    """
    return _get_pool().getconn()


def return_connection(conn):
    """
    Returns a connection back to the pool.
    """
    _get_pool().putconn(conn)


def get_cursor():
    """
    Returns a cursor with dictionary output.
    Useful if you want query results as dict instead of tuple.
    """
    conn = get_connection()
    return conn.cursor(cursor_factory=RealDictCursor)