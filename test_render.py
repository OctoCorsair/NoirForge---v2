import json
import unittest

from noirforge.generator import generate_case
from noirforge.render import case_to_public_dict, render_case, render_json


class RenderTests(unittest.TestCase):
    def test_solution_hidden_by_default(self):
        for lang in ("pt", "en"):
            case = generate_case(5, 4, lang)
            hidden = render_case(case)
            self.assertNotIn(case.twist, hidden)
            self.assertNotIn("## Solu", hidden)
            self.assertNotIn("## Solution", hidden)
            self.assertIn(case.title, hidden)

    def test_solution_revealed(self):
        pt = render_case(generate_case(5, 4, "pt"), reveal=True)
        en = render_case(generate_case(5, 4, "en"), reveal=True)
        self.assertIn("## Solução", pt)
        self.assertIn("## Solution", en)

    def test_all_suspects_and_clues_rendered(self):
        case = generate_case(3, 6, "en")
        text = render_case(case)
        for suspect in case.suspects:
            self.assertIn(suspect.name, text)
        for clue in case.clues:
            self.assertIn(clue.text, text)

    def test_public_json_has_no_spoilers(self):
        case = generate_case(12, 5, "en")
        payload = json.loads(render_json(case))
        raw = json.dumps(payload, ensure_ascii=False)
        self.assertNotIn("is_culprit", raw)
        self.assertNotIn("alibi_holds", raw)
        self.assertNotIn("red_herring", raw)
        self.assertNotIn(case.twist, raw)
        self.assertNotIn("solution", payload)
        self.assertEqual(payload, case_to_public_dict(case))
        self.assertEqual(len(payload["suspects"]), 5)

    def test_revealed_json_has_solution(self):
        case = generate_case(12, 5, "pt")
        payload = json.loads(render_json(case, reveal=True))
        self.assertEqual(payload["solution"]["culprit"], case.culprit.name)
        self.assertEqual(payload["twist"], case.twist)

    def test_json_keeps_accents(self):
        self.assertIn("São Paulo", render_json(generate_case(1, 4, "pt")))


if __name__ == "__main__":
    unittest.main()
