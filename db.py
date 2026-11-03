"""Persistência em SQLite, com migração automática do esquema v1."""

from __future__ import annotations

import sqlite3
from typing import Dict, List, Optional, Tuple

from .models import Case, Clue, Suspect


def _cases_ddl(table: str) -> str:
    return f"""
CREATE TABLE IF NOT EXISTS {table} (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    seed              INTEGER NOT NULL,
    num_suspects      INTEGER NOT NULL,
    lang              TEXT NOT NULL DEFAULT 'pt',
    title             TEXT NOT NULL,
    era               TEXT NOT NULL,
    place             TEXT NOT NULL,
    victim_name       TEXT NOT NULL,
    victim_occupation TEXT NOT NULL,
    weapon            TEXT NOT NULL,
    location          TEXT NOT NULL,
    twist             TEXT NOT NULL,
    created_at        TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (seed, num_suspects, lang)
)"""


SCHEMA = (
    _cases_ddl("cases")
    + """;

CREATE TABLE IF NOT EXISTS suspects (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id     INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    position    INTEGER NOT NULL,
    name        TEXT NOT NULL,
    relation    TEXT NOT NULL,
    motive      TEXT NOT NULL,
    alibi       TEXT NOT NULL,
    secret      TEXT NOT NULL,
    alibi_holds INTEGER NOT NULL,
    is_culprit  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS clues (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id     INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    position    INTEGER NOT NULL,
    kind        TEXT NOT NULL,
    text        TEXT NOT NULL,
    points_to   TEXT NOT NULL,
    explanation TEXT NOT NULL DEFAULT ''
);
"""
)

_CASE_COLUMNS = (
    "id, seed, num_suspects, title, era, place, victim_name, victim_occupation, "
    "weapon, location, twist, created_at"
)


def _migrate_v1(conn: sqlite3.Connection) -> None:
    """Converte um banco criado pela versão 1.x (sem coluna ``lang``)."""
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(cases)")}
    if not columns or "lang" in columns:
        return
    conn.execute("PRAGMA foreign_keys = OFF")
    try:
        conn.execute("BEGIN")
        conn.execute(_cases_ddl("cases_new"))
        conn.execute(
            f"INSERT INTO cases_new ({_CASE_COLUMNS}, lang) "
            f"SELECT {_CASE_COLUMNS}, 'pt' FROM cases"
        )
        conn.execute("UPDATE clues SET kind = 'clue' WHERE kind = 'pista'")
        conn.execute("UPDATE clues SET kind = 'red_herring' WHERE kind = 'falsa_pista'")
        conn.execute("DROP TABLE cases")
        conn.execute("ALTER TABLE cases_new RENAME TO cases")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.execute("PRAGMA foreign_keys = ON")


def connect(path: str = "noirforge.db") -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    _migrate_v1(conn)
    conn.executescript(SCHEMA)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def save_case(conn: sqlite3.Connection, case: Case) -> int:
    """Salva o caso e devolve o id. Salvar o mesmo caso duas vezes é idempotente."""
    n = len(case.suspects)
    existing = conn.execute(
        "SELECT id FROM cases WHERE seed = ? AND num_suspects = ? AND lang = ?",
        (case.seed, n, case.lang),
    ).fetchone()
    if existing:
        return int(existing["id"])

    with conn:
        cur = conn.execute(
            """INSERT INTO cases (seed, num_suspects, lang, title, era, place,
                                  victim_name, victim_occupation, weapon, location, twist)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (case.seed, n, case.lang, case.title, case.era, case.place,
             case.victim_name, case.victim_occupation, case.weapon,
             case.location, case.twist),
        )
        case_id = cur.lastrowid
        conn.executemany(
            """INSERT INTO suspects (case_id, position, name, relation, motive, alibi,
                                     secret, alibi_holds, is_culprit)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [(case_id, i, s.name, s.relation, s.motive, s.alibi, s.secret,
              int(s.alibi_holds), int(s.is_culprit))
             for i, s in enumerate(case.suspects)],
        )
        conn.executemany(
            """INSERT INTO clues (case_id, position, kind, text, points_to, explanation)
               VALUES (?, ?, ?, ?, ?, ?)""",
            [(case_id, i, c.kind, c.text, c.points_to, c.explanation)
             for i, c in enumerate(case.clues)],
        )
    assert case_id is not None
    return case_id


def load_case(conn: sqlite3.Connection, case_id: int) -> Optional[Case]:
    row = conn.execute("SELECT * FROM cases WHERE id = ?", (case_id,)).fetchone()
    if row is None:
        return None
    suspects = [
        Suspect(r["name"], r["relation"], r["motive"], r["alibi"], r["secret"],
                bool(r["alibi_holds"]), bool(r["is_culprit"]))
        for r in conn.execute(
            "SELECT * FROM suspects WHERE case_id = ? ORDER BY position", (case_id,))
    ]
    clues = [
        Clue(r["kind"], r["text"], r["points_to"], r["explanation"])
        for r in conn.execute(
            "SELECT * FROM clues WHERE case_id = ? ORDER BY position", (case_id,))
    ]
    return Case(
        seed=row["seed"], title=row["title"], era=row["era"], place=row["place"],
        victim_name=row["victim_name"], victim_occupation=row["victim_occupation"],
        weapon=row["weapon"], location=row["location"], twist=row["twist"],
        suspects=suspects, clues=clues, lang=row["lang"],
    )


def list_cases(conn: sqlite3.Connection) -> List[sqlite3.Row]:
    return conn.execute(
        "SELECT id, seed, num_suspects, lang, title, era, created_at FROM cases ORDER BY id"
    ).fetchall()


def delete_case(conn: sqlite3.Connection, case_id: int) -> bool:
    with conn:
        cur = conn.execute("DELETE FROM cases WHERE id = ?", (case_id,))
    return cur.rowcount > 0


def stats(conn: sqlite3.Connection) -> Dict[str, object]:
    total = conn.execute("SELECT COUNT(*) AS n FROM cases").fetchone()["n"]
    weapons: List[Tuple[str, int]] = [
        (r["weapon"], r["n"])
        for r in conn.execute(
            """SELECT weapon, COUNT(*) AS n FROM cases
               GROUP BY weapon ORDER BY n DESC, weapon LIMIT 3"""
        )
    ]
    relations: List[Tuple[str, int]] = [
        (r["relation"], r["n"])
        for r in conn.execute(
            """SELECT relation, COUNT(*) AS n FROM suspects
               WHERE is_culprit = 1 GROUP BY relation ORDER BY n DESC, relation LIMIT 3"""
        )
    ]
    return {"total": total, "weapons": weapons, "culprit_relations": relations}
