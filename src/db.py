import sqlite3
from src.config import DB_PATH

def get_conn():
    # read-only: the database itself refuses any write
    return sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)

def get_schema() -> str:
    conn = get_conn()
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")]
    lines = []
    for t in tables:
        cols = conn.execute(f"PRAGMA table_info({t})").fetchall()
        lines.append(f"{t}({', '.join(f'{c[1]} {c[2]}' for c in cols)})")
    conn.close()
    return "\n".join(lines)