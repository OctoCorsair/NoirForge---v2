import unittest

from noirforge.game import QUESTION_COST, play
from noirforge.generator import generate_case
from noirforge.locales import get_locale


def scripted(inputs):
    it = iter(inputs)

    def fake_input(prompt=""):
        try:
            return next(it)
        except StopIteration:
            raise EOFError from None

    return fake_input


def run(case, inputs):
    out = []
    result = play(case, get_locale(case.lang), scripted(inputs), out.append)
    return result, "\n".join(out)


class GameTests(unittest.TestCase):
    def setUp(self):
        self.case = generate_case(7, 4, "en")
        self.culprit_choice = str(
            next(i for i, s in enumerate(self.case.suspects, 1) if s.is_culprit)
        )
        self.innocent_choice = str(
            next(i for i, s in enumerate(self.case.suspects, 1) if not s.is_culprit)
        )

    def test_win_without_questions(self):
        result, out = run(self.case, ["3", self.culprit_choice])
        self.assertTrue(result.won)
        self.assertEqual(result.score, 100)
        self.assertEqual(result.accused, self.case.culprit.name)
        self.assertIn("Case closed", out)

    def test_questions_cost_points(self):
        # interrogar suspeito 1, perguntas 1 e 2, depois acusar
        inputs = ["2", "1", "1", "2", "0", "0", "3", self.culprit_choice]
        result, _ = run(self.case, inputs)
        self.assertTrue(result.won)
        self.assertEqual(result.questions, 2)
        self.assertEqual(result.score, 100 - 2 * QUESTION_COST)

    def test_repeating_a_question_is_free(self):
        inputs = ["2", "1", "1", "1", "1", "0", "0", "3", self.culprit_choice]
        result, _ = run(self.case, inputs)
        self.assertEqual(result.questions, 1)

    def test_wrong_accusation(self):
        result, out = run(self.case, ["3", self.innocent_choice])
        self.assertFalse(result.won)
        self.assertEqual(result.score, 0)
        self.assertIn(self.case.culprit.name, out)

    def test_give_up(self):
        result, out = run(self.case, ["0"])
        self.assertFalse(result.won)
        self.assertIsNone(result.accused)
        self.assertIn("abandoned", out)

    def test_eof_quits_cleanly(self):
        result, _ = run(self.case, [])
        self.assertFalse(result.won)

    def test_invalid_input_is_handled(self):
        result, out = run(self.case, ["x", "9", "2", "banana", "99", "0", "3", self.culprit_choice])
        self.assertTrue(result.won)
        self.assertGreaterEqual(out.count("Invalid option"), 3)

    def test_review_case(self):
        _, out = run(self.case, ["1", "0"])
        self.assertGreaterEqual(out.count(self.case.title), 2)

    def test_accuse_then_go_back(self):
        result, _ = run(self.case, ["3", "0", "3", self.culprit_choice])
        self.assertTrue(result.won)

    def test_portuguese_game(self):
        case = generate_case(7, 4, "pt")
        result, out = run(case, ["0"])
        self.assertFalse(result.won)
        self.assertIn("abandonou", out)


if __name__ == "__main__":
    unittest.main()
