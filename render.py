"""Renderização de casos em Markdown e JSON."""

from __future__ import annotations

import json
from typing import Any, Dict, List

from .locales import get_locale
from .models import CLUE, Case


def render_case(case: Case, reveal: bool = False) -> str:
    """Renderiza o caso em Markdown. A solução só aparece com ``reveal=True``."""
    ui = get_locale(case.lang).ui
    lines: List[str] = [
        f"# {case.title}",
        ui["meta"].format(era=case.era, seed=case.seed),
        "",
        ui["victim"].format(name=case.victim_name, occupation=case.victim_occupation),
        ui["scene"].format(location=case.location, place=case.place),
        ui["weapon"].format(weapon=case.weapon),
        "",
        f"## {ui['suspects_h']}",
    ]
    for s in case.suspects:
        lines.append(
            ui["suspect_line"].format(
                name=s.name, relation=s.relation, motive=s.motive, alibi=s.alibi
            )
        )

    lines += ["", f"## {ui['evidence_h']}"]
    for i, clue in enumerate(case.clues, 1):
        lines.append(f"{i}. {clue.text}")
        if reveal:
            if clue.kind == CLUE:
                lines.append(ui["clue_true"].format(name=clue.points_to))
            else:
                lines.append(ui["clue_false"].format(explanation=clue.explanation))

    if reveal:
        c = case.culprit
        lines += [
            "",
            f"## {ui['solution_h']}",
            ui["culprit_line"].format(name=c.name, relation=c.relation),
            ui["motive_line"].format(motive=c.motive),
            ui["alibi_line"].format(name=c.name, alibi=c.alibi),
            ui["twist_line"].format(twist=case.twist),
        ]
    else:
        lines += ["", ui["hint"]]
    return "\n".join(lines) + "\n"


def case_to_public_dict(case: Case) -> Dict[str, Any]:
    """Visão do caso sem nenhum spoiler."""
    return {
        "seed": case.seed,
        "lang": case.lang,
        "title": case.title,
        "era": case.era,
        "place": case.place,
        "victim": {"name": case.victim_name, "occupation": case.victim_occupation},
        "weapon": case.weapon,
        "location": case.location,
        "suspects": [
            {"name": s.name, "relation": s.relation, "motive": s.motive, "alibi": s.alibi}
            for s in case.suspects
        ],
        "clues": [c.text for c in case.clues],
    }


def render_json(case: Case, reveal: bool = False) -> str:
    """Renderiza o caso em JSON. Com ``reveal=True`` inclui a solução completa."""
    if reveal:
        payload: Dict[str, Any] = case.to_dict()
        payload["solution"] = {"culprit": case.culprit.name}
    else:
        payload = case_to_public_dict(case)
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
