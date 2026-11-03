import string
import unittest

from noirforge.locales import LOCALES, get_locale

SEQUENCE_FIELDS = (
    "surnames", "occupations", "relations", "motives", "alibis", "secrets",
    "weapons", "locations", "culprit_clues", "red_herrings", "twists",
    "places", "eras", "titles",
)


def placeholders(template: str) -> set:
    return {name for _, name, _, _ in string.Formatter().parse(template) if name}


class LocaleTests(unittest.TestCase):
    def test_at_least_two_languages(self):
        self.assertGreaterEqual(len(LOCALES), 2)

    def test_parallel_list_sizes(self):
        base = LOCALES["pt"]
        for loc in LOCALES.values():
            for field in SEQUENCE_FIELDS:
                self.assertEqual(
                    len(getattr(loc, field)), len(getattr(base, field)),
                    f"{loc.code}.{field} tem tamanho diferente de pt.{field}",
                )
            for gender in ("m", "f"):
                self.assertEqual(
                    len(loc.first_names[gender]), len(base.first_names[gender])
                )

    def test_minimum_pool_sizes(self):
        for loc in LOCALES.values():
            self.assertGreaterEqual(len(loc.surnames), 7)
            self.assertGreaterEqual(len(loc.first_names["m"]), 7)
            self.assertGreaterEqual(len(loc.first_names["f"]), 7)
            self.assertGreaterEqual(len(loc.motives), 6)
            self.assertGreaterEqual(len(loc.alibis), 6)
            self.assertGreaterEqual(len(loc.secrets), 5)
            self.assertGreaterEqual(len(loc.red_herrings), 3)

    def test_same_ui_keys_and_placeholders(self):
        base = LOCALES["pt"].ui
        for loc in LOCALES.values():
            self.assertEqual(set(loc.ui), set(base), loc.code)
            for key, template in loc.ui.items():
                self.assertEqual(
                    placeholders(template), placeholders(base[key]),
                    f"{loc.code}.ui[{key!r}] usa placeholders diferentes de pt",
                )

    def test_clue_templates_use_culprit_placeholder(self):
        for loc in LOCALES.values():
            for _, clue in loc.weapons + loc.locations:
                self.assertIn("{culprit}", clue)
            for clue in loc.culprit_clues:
                self.assertIn("{culprit}", clue)
            for herring in loc.red_herrings:
                self.assertIn("{suspect}", herring)

    def test_get_locale(self):
        self.assertEqual(get_locale("pt").code, "pt")
        with self.assertRaises(ValueError):
            get_locale("zz")


if __name__ == "__main__":
    unittest.main()
