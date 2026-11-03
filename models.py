"""Modelos de dados do NoirForge."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List

CLUE = "clue"
RED_HERRING = "red_herring"


@dataclass
class Suspect:
    name: str
    relation: str
    motive: str
    alibi: str
    secret: str
    alibi_holds: bool
    is_culprit: bool


@dataclass
class Clue:
    kind: str  # CLUE ou RED_HERRING
    text: str
    points_to: str
    explanation: str = ""


@dataclass
class Case:
    seed: int
    title: str
    era: str
    place: str
    victim_name: str
    victim_occupation: str
    weapon: str
    location: str
    twist: str
    suspects: List[Suspect]
    clues: List[Clue]
    lang: str = "pt"

    @property
    def culprit(self) -> Suspect:
        return next(s for s in self.suspects if s.is_culprit)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Case":
        fields = dict(data)
        fields["suspects"] = [Suspect(**s) for s in data["suspects"]]
        fields["clues"] = [Clue(**c) for c in data["clues"]]
        return cls(**fields)
