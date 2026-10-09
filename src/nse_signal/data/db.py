"""Database Management Module: Provides SQLite database connection, schema creation, and table accessors for all production required NSE data layers."""
from __future__ import annotations
import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path("data/processed/nse_signal.db")

def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    layers = [
        "cash_daily",
        "security_master",
        "index_close",
        "fo_bhavcopy",
        "delivery",
        "impact_cost",
        "breadth",
        "india_vix",
        "surveillance",
        "price_bands",
        "short_selling",
        "corporate_adjustments",
        "corporate_events"
    ]

    for layer in layers:
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {layer} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                date TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL,
                asof_time TEXT,
                signal_time TEXT,
                payload TEXT
            )
        """)

    conn.commit()
    conn.close()

def query_table(table_name: str, limit: int = 100) -> pd.DataFrame:
    conn = get_connection()
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT {limit}", conn)
        return df
    except Exception:
        return pd.DataFrame()
    finally:
        conn.close()

def table_row_count(table_name: str) -> int:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        row = cur.fetchone()
        return row[0] if row else 0
    except Exception:
        return 0
    finally:
        conn.close()
