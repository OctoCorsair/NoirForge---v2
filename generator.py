"""Gerador determinístico de casos policiais."""

from __future__ import annotations

import random
from typing import List, Optional, Tuple

from .locales import DEFAULT_LANG, Locale, get_locale
from .models import CLUE, RED_HERRING, Case, Clue, Suspect

MIN_SUSPECTS = 3
MAX_SUSPECTS = 6


def _gendered(pair: Tuple[str, str], gender: str) -> str:
    return pair[0] if gender == "m" else pair[1]


def _make_people(rng: random.Random, loc: Locale, count: int) -> List[Tuple[str, str]]:
    pools = {g: list(names) for g, names in loc.first_names.items()}
    surnames = rng.sample(loc.surnames, count)
    people: List[Tuple[str, str]] = []
    for surname in surnames:
        gender = rng.choice(("m", "f"))
        first = pools[gender].pop(rng.randrange(len(pools[gender])))
        people.append((f"{first} {surname}", gender))
    return people


def generate_case(
    seed: Optional[int] = None,
    num_suspects: int = 4,
    lang: str = DEFAULT_LANG,
) -> Case:
    """Gera um caso resolvível.

    A mesma ``seed`` e o mesmo ``num_suspects`` produzem sempre a mesma história,
    em qualquer idioma: só o texto muda.
    """
    if not MIN_SUSPECTS <= num_suspects <= MAX_SUSPECTS:
        raise ValueError(
            f"num_suspects deve estar entre {MIN_SUSPECTS} e {MAX_SUSPECTS}"
        )
    loc = get_locale(lang)
    if seed is None:
        seed = random.SystemRandom().randrange(1, 1_000_000)
    rng = random.Random(seed)

    people = _make_people(rng, loc, num_suspects + 1)
    victim_name, victim_gender = people[0]
    victim_occupation = _gendered(rng.choice(loc.occupations), victim_gender)

    relations = rng.sample(loc.relations, num_suspects)
    motives = rng.sample(loc.motives, num_suspects)
    alibis = rng.sample(loc.alibis, num_suspects)
    culprit_index = rng.randrange(num_suspects)
    secrets = iter(rng.sample(loc.secrets, num_suspects - 1))

    suspects: List[Suspect] = []
    for i, (name, gender) in enumerate(people[1:]):
        is_culprit = i == culprit_index
        suspects.append(
            Suspect(
                name=name,
                relation=_gendered(relations[i], gender),
                motive=motives[i],
                alibi=alibis[i],
                secret=loc.culprit_secret if is_culprit else next(secrets),
                alibi_holds=not is_culprit,
                is_culprit=is_culprit,
            )
        )
    culprit = suspects[culprit_index]

    weapon, weapon_clue = rng.choice(loc.weapons)
    location, location_clue = rng.choice(loc.locations)
    generic_clue = rng.choice(loc.culprit_clues)

    clues = [
        Clue(CLUE, text.format(culprit=culprit.name), culprit.name)
        for text in (weapon_clue, location_clue, generic_clue)
    ]

    others = [s for s in suspects if not s.is_culprit]
    herring_count = min(3, len(others))
    for suspect, template in zip(
        rng.sample(others, herring_count),
        rng.sample(loc.red_herrings, herring_count),
    ):
        clues.append(
            Clue(
                RED_HERRING,
                template.format(suspect=suspect.name),
                suspect.name,
                loc.explain(suspect.name, suspect.secret),
            )
        )
    rng.shuffle(clues)

    first, surname = victim_name.split()
    title = rng.choice(loc.titles).format(first=first, surname=surname)

    return Case(
        seed=seed,
        title=title,
        era=rng.choice(loc.eras),
        place=rng.choice(loc.places),
        victim_name=victim_name,
        victim_occupation=victim_occupation,
        weapon=weapon,
        location=location,
        twist=rng.choice(loc.twists),
        suspects=suspects,
        clues=clues,
        lang=lang,
    )
