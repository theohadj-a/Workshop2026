import os
import sqlite3
from contextlib import contextmanager
from typing import Generator, Optional, Any, Dict, List
from .config import settings

# Détection du mode base de données : PostgreSQL ou SQLite
USE_POSTGRES = bool(settings.database_url and settings.database_url.startswith("postgres"))

if USE_POSTGRES:
    import psycopg2
    from psycopg2 import pool
    from psycopg2.extras import RealDictCursor

    pg_pool: Optional[pool.SimpleConnectionPool] = None

    def get_pg_pool() -> pool.SimpleConnectionPool:
        global pg_pool
        if pg_pool is None:
            pg_pool = pool.SimpleConnectionPool(
                minconn=2,
                maxconn=20,
                dsn=settings.database_url,
            )
        return pg_pool

@contextmanager
def db_session():
    if USE_POSTGRES:
        p = get_pg_pool()
        conn = p.getconn()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            p.putconn(conn)
    else:
        conn = sqlite3.connect(settings.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
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
    if USE_POSTGRES:
        with db_session() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS transactions (
                        id VARCHAR(64) PRIMARY KEY,
                        reference VARCHAR(64) NOT NULL,
                        amount NUMERIC(12, 2) NOT NULL,
                        currency VARCHAR(8) NOT NULL,
                        customer_name VARCHAR(128) NOT NULL,
                        customer_email VARCHAR(128) NOT NULL,
                        card_last4 VARCHAR(8) NOT NULL,
                        merchant_id VARCHAR(64) NOT NULL,
                        status VARCHAR(32) NOT NULL,
                        auth_code VARCHAR(32) NOT NULL,
                        message TEXT NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL,
                        error_message TEXT
                    );
                    CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions (created_at DESC);
                    CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions (status);
                """)
    else:
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
        if USE_POSTGRES:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO transactions (
                        id, reference, amount, currency, customer_name, customer_email,
                        card_last4, merchant_id, status, auth_code, message, created_at, error_message
                    ) VALUES (
                        %(id)s, %(reference)s, %(amount)s, %(currency)s, %(customer_name)s, %(customer_email)s,
                        %(card_last4)s, %(merchant_id)s, %(status)s, %(auth_code)s, %(message)s, %(created_at)s, %(error_message)s
                    )
                """, tx_data)
        else:
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
        if USE_POSTGRES:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM transactions WHERE id = %s", (tx_id,))
                row = cur.fetchone()
                if row:
                    row["amount"] = float(row["amount"])
                    row["created_at"] = row["created_at"].isoformat()
                    return dict(row)
                return None
        else:
            cursor = conn.execute("SELECT * FROM transactions WHERE id = ?", (tx_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

def list_transactions(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    with db_session() as conn:
        if USE_POSTGRES:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM transactions ORDER BY created_at DESC LIMIT %s OFFSET %s",
                    (limit, offset)
                )
                results = []
                for row in cur.fetchall():
                    item = dict(row)
                    item["amount"] = float(item["amount"])
                    item["created_at"] = item["created_at"].isoformat()
                    results.append(item)
                return results
        else:
            cursor = conn.execute(
                "SELECT * FROM transactions ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset)
            )
            return [dict(row) for row in cursor.fetchall()]

def count_transactions() -> int:
    with db_session() as conn:
        if USE_POSTGRES:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) as count FROM transactions")
                row = cur.fetchone()
                return int(row[0]) if row else 0
        else:
            cursor = conn.execute("SELECT COUNT(*) as count FROM transactions")
            row = cursor.fetchone()
            return int(row["count"]) if row else 0

def check_db_health() -> bool:
    try:
        with db_session() as conn:
            if USE_POSTGRES:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    return cur.fetchone() is not None
            else:
                cursor = conn.execute("SELECT 1")
                return cursor.fetchone() is not None
    except Exception:
        return False
