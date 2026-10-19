import sqlite3
import os
from contextlib import contextmanager
from typing import Generator, Optional, Any, Dict, List
from .config import settings

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def db_session() -> Generator[sqlite3.Connection, None, None]:
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db() -> None:
    """Initialise la table des transactions si elle n'existe pas."""
    db_dir = os.path.dirname(settings.db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    with db_session() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                reference TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT NOT NULL,
                customer_name TEXT NOT NULL,
                customer_email TEXT NOT NULL,
                card_last4 TEXT NOT NULL,
                merchant_id TEXT NOT NULL,
                status TEXT NOT NULL,
                auth_code TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL,
                error_message TEXT
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions (created_at DESC)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions (status)")

def save_transaction(tx_data: Dict[str, Any]) -> None:
    with db_session() as conn:
        conn.execute("""
            INSERT INTO transactions (
                id, reference, amount, currency, customer_name, customer_email,
                card_last4, merchant_id, status, auth_code, message, created_at, error_message
            ) VALUES (
                :id, :reference, :amount, :currency, :customer_name, :customer_email,
                :card_last4, :merchant_id, :status, :auth_code, :message, :created_at, :error_message
            )
        """, tx_data)

def get_transaction_by_id(tx_id: str) -> Optional[Dict[str, Any]]:
    with db_session() as conn:
        cursor = conn.execute("SELECT * FROM transactions WHERE id = ?", (tx_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def list_transactions(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    with db_session() as conn:
        cursor = conn.execute(
            "SELECT * FROM transactions ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset)
        )
        return [dict(row) for row in cursor.fetchall()]

def count_transactions() -> int:
    with db_session() as conn:
        cursor = conn.execute("SELECT COUNT(*) as count FROM transactions")
        row = cursor.fetchone()
        return int(row["count"]) if row else 0

def check_db_health() -> bool:
    try:
        with db_session() as conn:
            cursor = conn.execute("SELECT 1")
            return cursor.fetchone() is not None
    except Exception:
        return False
