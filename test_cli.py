import contextlib
import io
import json
import os
import tempfile
import unittest
from unittest import mock

from noirforge.cli import main


def run(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = main(list(argv))
        except SystemExit as exc:
            code = int(exc.code or 0)
    return code, out.getvalue(), err.getvalue()


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = os.path.join(self.tmp.name, "cli.db")

    def tearDown(self):
        self.tmp.cleanup()

    def cmd(self, *argv):
        return run("--db", self.db, *argv)

    def test_new_default(self):
        code, out, _ = self.cmd("new", "--seed", "7")
        self.assertEqual(code, 0)
        self.assertIn("seed 7", out)
        self.assertNotIn("## Solução", out)

    def test_new_english_json_solution(self):
        code, out, _ = self.cmd("new", "--seed", "7", "--lang", "en", "--format", "json", "--solution")
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertEqual(payload["lang"], "en")
        self.assertIn("solution", payload)

    def test_invalid_suspects(self):
        code, _, err = self.cmd("new", "--suspects", "9")
        self.assertEqual(code, 2)
        self.assertIn("num_suspects", err)

    def test_invalid_language(self):
        code, _, _ = self.cmd("new", "--lang", "xx")
        self.assertEqual(code, 2)

    def test_missing_command(self):
        code, _, _ = self.cmd()
        self.assertEqual(code, 2)

    def test_list_empty(self):
        code, out, _ = self.cmd("list")
        self.assertEqual(code, 0)
        self.assertIn("Nenhum caso", out)

    def test_full_workflow(self):
        code, out, _ = self.cmd("new", "--seed", "7", "--save")
        self.assertEqual(code, 0)
        self.assertIn("id 1", out)
        self.cmd("new", "--seed", "7", "--lang", "en", "--save")

        code, out, _ = self.cmd("list")
        self.assertIn("seed=7", out)
        self.assertEqual(len(out.strip().splitlines()), 2)

        code, out, _ = self.cmd("show", "1", "--solution")
        self.assertIn("## Solução", out)

        md = os.path.join(self.tmp.name, "caso.md")
        code, _, _ = self.cmd("export", "1", "--out", md)
        self.assertEqual(code, 0)
        with open(md, encoding="utf-8") as fh:
            self.assertIn("seed 7", fh.read())

        js = os.path.join(self.tmp.name, "caso.json")
        self.cmd("export", "2", "--out", js, "--solution")
        with open(js, encoding="utf-8") as fh:
            self.assertEqual(json.load(fh)["lang"], "en")

        code, out, _ = self.cmd("stats")
        self.assertIn("Casos salvos: 2", out)

        code, _, _ = self.cmd("delete", "1")
        self.assertEqual(code, 0)
        code, _, err = self.cmd("show", "1")
        self.assertEqual(code, 1)
        self.assertIn("não encontrado", err)
        code, _, _ = self.cmd("delete", "1")
        self.assertEqual(code, 1)

    def test_export_missing_case(self):
        code, _, _ = self.cmd("export", "5", "--out", os.path.join(self.tmp.name, "x.md"))
        self.assertEqual(code, 1)

    def test_play_via_cli(self):
        with mock.patch("builtins.input", side_effect=["0"]):
            code, out, _ = self.cmd("play", "--seed", "7", "--lang", "en")
        self.assertEqual(code, 0)
        self.assertIn("abandoned", out)


if __name__ == "__main__":
    unittest.main()
