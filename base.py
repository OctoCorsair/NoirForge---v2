"""Estrutura de um idioma (locale) do NoirForge."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class Locale:
    """Todo o conteúdo narrativo e de interface de um idioma.

    Os pares (masculino, feminino) permitem concordância de gênero.
    Para o mesmo seed, todos os idiomas contam a MESMA história, por isso as
    listas de cada idioma precisam ter o mesmo tamanho (os testes garantem isso).
    """

    code: str
    first_names: Dict[str, Tuple[str, ...]]
    surnames: Tuple[str, ...]
    occupations: Tuple[Tuple[str, str], ...]
    relations: Tuple[Tuple[str, str], ...]
    motives: Tuple[str, ...]
    alibis: Tuple[str, ...]
    secrets: Tuple[str, ...]
    culprit_secret: str
    weapons: Tuple[Tuple[str, str], ...]  # (arma, pista)
    locations: Tuple[Tuple[str, str], ...]  # (local, pista)
    culprit_clues: Tuple[str, ...]
    red_herrings: Tuple[str, ...]
    twists: Tuple[str, ...]
    places: Tuple[str, ...]
    eras: Tuple[str, ...]
    titles: Tuple[str, ...]
    ui: Dict[str, str]

    def explain(self, name: str, secret: str) -> str:
        """Explica por que um inocente parecia culpado."""
        return self.ui["herring_explanation"].format(name=name, secret=secret)
