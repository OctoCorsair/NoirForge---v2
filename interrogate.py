"""Interrogatório de suspeitos."""

from __future__ import annotations

from typing import List, Optional, Tuple

from .locales import Locale, get_locale
from .models import Case, Suspect

QUESTION_KEYS: Tuple[str, ...] = ("alibi", "motive", "relation", "pressure")


def question_labels(locale: Locale) -> List[str]:
    return [locale.ui[f"q_{key}"] for key in QUESTION_KEYS]


def answer(
    case: Case, suspect: Suspect, key: str, locale: Optional[Locale] = None
) -> str:
    """Resposta de um suspeito.

    Os inocentes cedem sob pressão e revelam o segredo que os fazia parecer
    culpados. O culpado nunca cede: ele se trai evitando o assunto.
    """
    loc = locale or get_locale(case.lang)
    ui = loc.ui
    if key == "alibi":
        return ui["ans_alibi"].format(name=suspect.name, alibi=suspect.alibi)
    if key == "motive":
        return ui["ans_motive"].format(name=suspect.name, motive=suspect.motive)
    if key == "relation":
        return ui["ans_relation"].format(name=suspect.name, relation=suspect.relation)
    if key == "pressure":
        if suspect.is_culprit:
            return ui["ans_pressure_culprit"].format(name=suspect.name)
        return ui["ans_pressure_innocent"].format(
            name=suspect.name, explanation=loc.explain(suspect.name, suspect.secret)
        )
    raise ValueError(f"pergunta desconhecida: {key!r}")
