import unittest

from noirforge.generator import generate_case
from noirforge.models import CLUE, RED_HERRING, Case
from noirforge.render import render_case


class GeneratorTests(unittest.TestCase):
    def test_deterministic(self):
        self.assertEqual(generate_case(42), generate_case(42))

    def test_different_seeds_differ(self):
        self.assertNotEqual(generate_case(1), generate_case(2))

    def test_random_seed_when_none(self):
        case = generate_case(None)
        self.assertGreaterEqual(case.seed, 1)
        self.assertEqual(generate_case(case.seed), case)

    def test_exactly_one_culprit(self):
        for seed in range(300):
            case = generate_case(seed, 3 + seed % 4)
            self.assertEqual(sum(s.is_culprit for s in case.suspects), 1)
            self.assertFalse(case.culprit.alibi_holds)

    def test_innocents_have_valid_alibi_flag(self):
        case = generate_case(5, 6)
        self.assertTrue(all(s.alibi_holds for s in case.suspects if not s.is_culprit))

    def test_clue_structure(self):
        for seed in range(300):
            case = generate_case(seed, 3 + seed % 4)
            names = {s.name for s in case.suspects}
            true = [c for c in case.clues if c.kind == CLUE]
            false = [c for c in case.clues if c.kind == RED_HERRING]
            self.assertEqual(len(true), 3)
            self.assertTrue(all(c.points_to == case.culprit.name for c in true))
            self.assertTrue(all(c.points_to in names for c in false))
            self.assertTrue(all(c.points_to != case.culprit.name for c in false))
            self.assertTrue(all(c.explanation for c in false))
            self.assertEqual(len(false), min(3, len(case.suspects) - 1))

    def test_red_herrings_target_distinct_suspects(self):
        for seed in range(100):
            case = generate_case(seed, 6)
            targets = [c.points_to for c in case.clues if c.kind == RED_HERRING]
            self.assertEqual(len(targets), len(set(targets)))

    def test_names_are_unique(self):
        for seed in range(200):
            case = generate_case(seed, 6)
            names = [s.name for s in case.suspects] + [case.victim_name]
            self.assertEqual(len(names), len(set(names)))

    def test_no_unformatted_templates(self):
        for lang in ("pt", "en"):
            for seed in range(200):
                case = generate_case(seed, 3 + seed % 4, lang)
                blob = render_case(case, reveal=True)
                self.assertNotIn("{", blob)
                self.assertNotIn("}", blob)

    def test_same_story_in_every_language(self):
        for seed in range(100):
            pt = generate_case(seed, 5, "pt")
            en = generate_case(seed, 5, "en")
            self.assertEqual([s.name for s in pt.suspects], [s.name for s in en.suspects])
            self.assertEqual(pt.culprit.name, en.culprit.name)
            self.assertEqual(pt.victim_name, en.victim_name)

    def test_invalid_suspect_count(self):
        for n in (0, 2, 7):
            with self.assertRaises(ValueError):
                generate_case(1, n)

    def test_unknown_language(self):
        with self.assertRaises(ValueError):
            generate_case(1, 4, "xx")

    def test_dict_roundtrip(self):
        case = generate_case(9, 5, "en")
        self.assertEqual(Case.from_dict(case.to_dict()), case)


if __name__ == "__main__":
    unittest.main()
