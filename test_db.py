import os
import sqlite3
import tempfile
import unittest

from noirforge import db
from noirforge.generator import generate_case

V1_SCHEMA = """
CREATE TABLE cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT, seed INTEGER NOT NULL,
    num_suspects INTEGER NOT NULL, title TEXT NOT NULL, era TEXT NOT NULL,
    place TEXT NOT NULL, victim_name TEXT NOT NULL, victim_occupation TEXT NOT NULL,
    weapon TEXT NOT NULL, location TEXT NOT NULL, twist TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (seed, num_suspects)
);
CREATE TABLE suspects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    position INTEGER NOT NULL, name TEXT NOT NULL, relation TEXT NOT NULL,
    motive TEXT NOT NULL, alibi TEXT NOT NULL, secret TEXT NOT NULL,
    alibi_holds INTEGER NOT NULL, is_culprit INTEGER NOT NULL
);
CREATE TABLE clues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    position INTEGER NOT NULL, kind TEXT NOT NULL, text TEXT NOT NULL,
    points_to TEXT NOT NULL, explanation TEXT NOT NULL DEFAULT ''
);
INSERT INTO cases (seed, num_suspects, title, era, place, victim_name,
    victim_occupation, weapon, location, twist)
VALUES (7, 3, 'Velho Caso', 'São Paulo, 1947', 'no Brás', 'A B', 'juiz', 'faca', 'no porão', 'x');
INSERT INTO suspects (case_id, position, name, relation, motive, alibi, secret, alibi_holds, is_culprit)
VALUES (1, 0, 'C D', 'sócio', 'm', 'a', 's', 0, 1);
INSERT INTO clues (case_id, position, kind, text, points_to)
VALUES (1, 0, 'pista', 't', 'C D'), (1, 1, 'falsa_pista', 'u', 'E F');
"""


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "t.db")
        self.conn = db.connect(self.path)

    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()

    def test_roundtrip_both_languages(self):
        for lang in ("pt", "en"):
            case = generate_case(99, 5, lang)
            case_id = db.save_case(self.conn, case)
            self.assertEqual(db.load_case(self.conn, case_id), case)

    def test_same_seed_different_language_are_distinct(self):
        a = db.save_case(self.conn, generate_case(5, 4, "pt"))
        b = db.save_case(self.conn, generate_case(5, 4, "en"))
        self.assertNotEqual(a, b)

    def test_save_is_idempotent(self):
        case = generate_case(11)
        self.assertEqual(db.save_case(self.conn, case), db.save_case(self.conn, case))
        self.assertEqual(len(db.list_cases(self.conn)), 1)

    def test_load_missing(self):
        self.assertIsNone(db.load_case(self.conn, 404))

    def test_delete_cascades(self):
        case_id = db.save_case(self.conn, generate_case(3))
        self.assertTrue(db.delete_case(self.conn, case_id))
        self.assertFalse(db.delete_case(self.conn, case_id))
        for table in ("suspects", "clues"):
            left = self.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            self.assertEqual(left, 0)

    def test_stats(self):
        for seed in range(1, 11):
            db.save_case(self.conn, generate_case(seed))
        s = db.stats(self.conn)
        self.assertEqual(s["total"], 10)
        self.assertTrue(s["weapons"])
        self.assertTrue(s["culprit_relations"])
        self.assertLessEqual(len(s["weapons"]), 3)


class MigrationTests(unittest.TestCase):
    def test_v1_database_is_migrated(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "old.db")
            raw = sqlite3.connect(path)
            raw.executescript(V1_SCHEMA)
            raw.commit()
            raw.close()

            conn = db.connect(path)
            try:
                rows = db.list_cases(conn)
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]["lang"], "pt")
                case = db.load_case(conn, 1)
                self.assertEqual(case.title, "Velho Caso")
                self.assertEqual(len(case.suspects), 1)
                kinds = [c.kind for c in case.clues]
                self.assertEqual(kinds, ["clue", "red_herring"])
                # a mesma seed agora pode existir em outro idioma
                new_id = db.save_case(conn, generate_case(7, 3, "en"))
                self.assertEqual(new_id, 2)
                # chaves estrangeiras continuam valendo
                fk = conn.execute("PRAGMA foreign_keys").fetchone()[0]
                self.assertEqual(fk, 1)
            finally:
                conn.close()

    def test_fresh_database_is_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            conn = db.connect(os.path.join(tmp, "a.db"))
            conn.close()
            conn = db.connect(os.path.join(tmp, "a.db"))
            try:
                cols = {r["name"] for r in conn.execute("PRAGMA table_info(cases)")}
                self.assertIn("lang", cols)
            finally:
                conn.close()


if __name__ == "__main__":
    unittest.main()
