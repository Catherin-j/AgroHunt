# app/database/connection.py

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """
    Creates a secure PostgreSQL connection to Supabase.

    Uses DATABASE_URL environment variable.

    Required in Render:
        DATABASE_URL = postgresql://user:password@host:5432/dbname
    """

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL not set in environment variables")

    try:
        conn = psycopg2.connect(
            database_url,
            sslmode="require"  # 🔥 Required for Supabase
        )
        return conn

    except Exception as e:
        raise RuntimeError(f"Database connection failed: {e}")


def get_cursor():
    """
    Returns a cursor with dictionary output.
    Useful if you want query results as dict instead of tuple.
    """
    conn = get_connection()
    return conn.cursor(cursor_factory=RealDictCursor)