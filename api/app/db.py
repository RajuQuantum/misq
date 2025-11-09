from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from typing import Dict, Optional, Tuple

import numpy as np

from . import quantum
from .models import QuantumStateModel, SessionResponse
from .utils import deserialize_state, serialize_state, vector_to_dict

DB_PATH = Path(__file__).resolve().parent.parent / 'data' / 'quantum.db'
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

_DB_LOCK = Lock()


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _DB_LOCK:
        with get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    vector TEXT NOT NULL,
                    collapsed_q1 INTEGER NOT NULL,
                    collapsed_q2 INTEGER NOT NULL,
                    last_measurement_q1 INTEGER,
                    last_measurement_q2 INTEGER,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    payload TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(session_id) REFERENCES sessions(id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS trials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    n INTEGER NOT NULL,
                    counts TEXT NOT NULL,
                    freqs TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(session_id) REFERENCES sessions(id)
                )
                """
            )


def _state_model_from_row(row: sqlite3.Row) -> QuantumStateModel:
    vector = deserialize_state(row['vector'])
    state = QuantumStateModel(
        vector=vector_to_dict(vector),
        collapsed={'Q1': bool(row['collapsed_q1']), 'Q2': bool(row['collapsed_q2'])},
        last_measurement={'Q1': row['last_measurement_q1'], 'Q2': row['last_measurement_q2']},
    )
    return state


def create_session() -> SessionResponse:
    session_id = str(uuid.uuid4())
    vector = quantum.initial_state()
    state_model = QuantumStateModel(
        vector=vector_to_dict(vector),
        collapsed={'Q1': False, 'Q2': False},
        last_measurement={'Q1': None, 'Q2': None},
    )
    now = datetime.now(UTC).isoformat()
    payload = serialize_state(vector)
    with _DB_LOCK:
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO sessions (
                    id, vector, collapsed_q1, collapsed_q2, last_measurement_q1, last_measurement_q2, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (session_id, payload, 0, 0, None, None, now, now),
            )
            conn.execute(
                "INSERT INTO actions (session_id, action_type, payload, created_at) VALUES (?, ?, ?, ?)",
                (session_id, 'SESSION_CREATE', json.dumps({'state': state_model.dict()}), now),
            )
    return SessionResponse(session_id=session_id, state=state_model)


def fetch_session(session_id: str) -> Tuple[np.ndarray, QuantumStateModel]:
    with _DB_LOCK:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    if row is None:
        raise KeyError("Session not found")
    state_model = _state_model_from_row(row)
    vector = deserialize_state(row['vector'])
    return vector, state_model


def update_session_state(
    session_id: str,
    vector: np.ndarray,
    collapsed: Dict[str, bool],
    last_measurement: Dict[str, Optional[int]],
) -> QuantumStateModel:
    now = datetime.now(UTC).isoformat()
    payload = serialize_state(vector)
    with _DB_LOCK:
        with get_connection() as conn:
            conn.execute(
                """
                UPDATE sessions
                SET vector = ?,
                    collapsed_q1 = ?,
                    collapsed_q2 = ?,
                    last_measurement_q1 = ?,
                    last_measurement_q2 = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    payload,
                    int(collapsed['Q1']),
                    int(collapsed['Q2']),
                    last_measurement['Q1'],
                    last_measurement['Q2'],
                    now,
                    session_id,
                ),
            )
    return QuantumStateModel(
        vector=vector_to_dict(vector),
        collapsed=collapsed,
        last_measurement=last_measurement,
    )


def log_action(session_id: str, action_type: str, payload: Dict) -> None:
    now = datetime.now(UTC).isoformat()
    with _DB_LOCK:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO actions (session_id, action_type, payload, created_at) VALUES (?, ?, ?, ?)",
                (session_id, action_type, json.dumps(payload), now),
            )


def log_trials(session_id: str, scope: str, n: int, counts: Dict[str, int], freqs: Dict[str, float]) -> None:
    now = datetime.now(UTC).isoformat()
    with _DB_LOCK:
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO trials (session_id, scope, n, counts, freqs, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (session_id, scope, n, json.dumps(counts), json.dumps(freqs), now),
            )
