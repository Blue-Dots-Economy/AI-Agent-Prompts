"""Shared ingestion helpers: hashing, idempotent upsert, source-file provenance."""
from __future__ import annotations
import hashlib
import json
import time
from pathlib import Path


def h(*parts) -> str:
    """Stable natural-key hash for an entity id."""
    return hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:16]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def file_unchanged(conn, path: Path) -> bool:
    """True if this file's sha matches the last ingest (skip re-parse)."""
    path = Path(path)
    if not path.exists():
        return False
    cur = conn.execute("SELECT sha256 FROM source_files WHERE path=?", (str(path),)).fetchone()
    return bool(cur) and cur[0] == sha256_file(path)


def mark_source(conn, path: Path, row_count: int):
    path = Path(path)
    conn.execute(
        "INSERT INTO source_files(path,sha256,mtime,last_ingested_at,row_count) VALUES(?,?,?,?,?) "
        "ON CONFLICT(path) DO UPDATE SET sha256=excluded.sha256, mtime=excluded.mtime, "
        "last_ingested_at=excluded.last_ingested_at, row_count=excluded.row_count",
        (str(path), sha256_file(path) if path.exists() else "", path.stat().st_mtime if path.exists() else 0,
         time.strftime("%Y-%m-%dT%H:%M:%S"), row_count),
    )


def upsert(conn, table: str, rows: list[dict], pk: str):
    """Idempotent upsert by primary key. `rows` are dicts of column->value.
    Non-pk columns are updated on conflict; JSON-encodes list/dict values."""
    n = 0
    for r in rows:
        r = {k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v)
             for k, v in r.items()}
        cols = list(r.keys())
        placeholders = ",".join("?" for _ in cols)
        updates = ",".join(f"{c}=excluded.{c}" for c in cols if c != pk)
        sql = (f"INSERT INTO {table}({','.join(cols)}) VALUES({placeholders}) "
               f"ON CONFLICT({pk}) DO UPDATE SET {updates}" if updates
               else f"INSERT OR IGNORE INTO {table}({','.join(cols)}) VALUES({placeholders})")
        conn.execute(sql, [r[c] for c in cols])
        n += 1
    return n
