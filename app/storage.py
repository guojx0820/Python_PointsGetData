from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .models import ExtractedMetric, ReportRecord


DB_PATH = Path("data/reports.db")


def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                plan TEXT NOT NULL,
                metrics_json TEXT NOT NULL,
                abstract TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def save_report(filename: str, plan: str, metrics: list[ExtractedMetric], abstract: str) -> int:
    payload = json.dumps([m.model_dump() for m in metrics], ensure_ascii=False)
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO reports(filename, plan, metrics_json, abstract) VALUES (?, ?, ?, ?)",
            (filename, plan, payload, abstract),
        )
        return int(cur.lastrowid)


def list_reports() -> list[ReportRecord]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, filename, plan, metrics_json, abstract FROM reports ORDER BY id DESC"
        ).fetchall()
    return [ReportRecord(**dict(row)) for row in rows]


def get_report(report_id: int) -> ReportRecord | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, filename, plan, metrics_json, abstract FROM reports WHERE id = ?",
            (report_id,),
        ).fetchone()
    if not row:
        return None
    return ReportRecord(**dict(row))
