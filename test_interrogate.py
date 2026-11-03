import unittest

from noirforge.generator import generate_case
from noirforge.interrogate import QUESTION_KEYS, answer, question_labels
from noirforge.locales import get_locale


class InterrogationTests(unittest.TestCase):
    def test_every_question_answers_for_everyone(self):
        for lang in ("pt", "en"):
            case = generate_case(8, 6, lang)
            for suspect in case.suspects:
                for key in QUESTION_KEYS:
                    text = answer(case, suspect, key)
                    self.assertIn(suspect.name, text)
                    self.assertNotIn("{", text)

    def test_innocents_confess_under_pressure(self):
        for seed in range(100):
            case = generate_case(seed, 5, "en")
            for s in case.suspects:
                text = answer(case, s, "pressure")
                if s.is_culprit:
                    self.assertNotIn(s.secret, text)
                else:
                    self.assertIn(s.secret, text)

    def test_culprit_never_confesses(self):
        for seed in range(100):
            case = generate_case(seed, 4, "pt")
            text = answer(case, case.culprit, "pressure")
            self.assertNotIn(case.culprit.secret, text)

    def test_unknown_question(self):
        case = generate_case(1)
        with self.assertRaises(ValueError):
            answer(case, case.suspects[0], "nope")

    def test_question_labels_match_keys(self):
        for lang in ("pt", "en"):
            self.assertEqual(len(question_labels(get_locale(lang))), len(QUESTION_KEYS))


if __name__ == "__main__":
    unittest.main()
