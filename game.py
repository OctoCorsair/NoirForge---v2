"""Modo de jogo: interrogue, deduza e acuse."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional, Set, Tuple

from .interrogate import QUESTION_KEYS, answer, question_labels
from .locales import Locale
from .models import Case
from .render import render_case

QUESTION_COST = 5


@dataclass
class GameResult:
    won: bool
    score: int
    questions: int
    accused: Optional[str]


def _read(input_fn: Callable[[str], str], prompt: str) -> Optional[str]:
    try:
        return input_fn(prompt).strip()
    except EOFError:
        return None


def _pick(
    options: List[str],
    header: str,
    locale: Locale,
    input_fn: Callable[[str], str],
    output_fn: Callable[[str], None],
) -> Optional[int]:
    """Mostra um menu numerado. Devolve o índice escolhido ou None para voltar."""
    while True:
        output_fn(header)
        for i, option in enumerate(options, 1):
            output_fn(f"  [{i}] {option}")
        choice = _read(input_fn, locale.ui["g_prompt"])
        if choice is None or choice == "0":
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return int(choice) - 1
        output_fn(locale.ui["g_invalid"])


def play(
    case: Case,
    locale: Locale,
    input_fn: Optional[Callable[[str], str]] = None,
    output_fn: Optional[Callable[[str], None]] = None,
) -> GameResult:
    """Roda uma partida. ``input_fn`` e ``output_fn`` são injetáveis para teste."""
    # Resolvidos na chamada (e não na definição) para respeitar mocks de input/print.
    read_fn: Callable[[str], str] = input_fn if input_fn is not None else input
    write_fn: Callable[[str], None] = output_fn if output_fn is not None else print
    ui = locale.ui
    names = [s.name for s in case.suspects]
    asked: Set[Tuple[int, str]] = set()

    write_fn(ui["g_welcome"])
    write_fn(render_case(case))

    while True:
        write_fn(ui["g_menu"])
        choice = _read(read_fn, ui["g_prompt"])

        if choice is None or choice == "0":
            write_fn(ui["g_quit"].format(culprit=case.culprit.name))
            return GameResult(False, 0, len(asked), None)

        if choice == "1":
            write_fn(render_case(case))

        elif choice == "2":
            while True:
                s_idx = _pick(names, ui["g_pick_suspect"], locale, read_fn, write_fn)
                if s_idx is None:
                    break
                suspect = case.suspects[s_idx]
                header = ui["g_pick_question"].format(name=suspect.name)
                while True:
                    q_idx = _pick(question_labels(locale), header, locale, read_fn, write_fn)
                    if q_idx is None:
                        break
                    asked.add((s_idx, QUESTION_KEYS[q_idx]))
                    write_fn(answer(case, suspect, QUESTION_KEYS[q_idx], locale))

        elif choice == "3":
            a_idx = _pick(names, ui["g_pick_accuse"], locale, read_fn, write_fn)
            if a_idx is None:
                continue
            accused = case.suspects[a_idx]
            if accused.is_culprit:
                score = max(0, 100 - QUESTION_COST * len(asked))
                write_fn(ui["g_correct"].format(name=accused.name))
                write_fn(ui["g_score"].format(score=score, questions=len(asked)))
                return GameResult(True, score, len(asked), accused.name)
            write_fn(
                ui["g_wrong"].format(name=accused.name, culprit=case.culprit.name)
            )
            write_fn(ui["g_score"].format(score=0, questions=len(asked)))
            return GameResult(False, 0, len(asked), accused.name)

        else:
            write_fn(ui["g_invalid"])
