"""Interface de linha de comando."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Optional, Sequence

from . import __version__, db, game
from .generator import MAX_SUSPECTS, MIN_SUSPECTS, generate_case
from .locales import DEFAULT_LANG, LOCALES, get_locale
from .models import Case
from .render import render_case, render_json

DEFAULT_DB = os.environ.get("NOIRFORGE_DB", "noirforge.db")
_env_lang = os.environ.get("NOIRFORGE_LANG", DEFAULT_LANG)
ENV_LANG = _env_lang if _env_lang in LOCALES else DEFAULT_LANG


def _add_generation_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--seed", type=int, help="seed para reproduzir um caso")
    p.add_argument("--suspects", type=int, default=4,
                   help=f"número de suspeitos ({MIN_SUSPECTS} a {MAX_SUSPECTS})")
    p.add_argument("--lang", choices=sorted(LOCALES), default=ENV_LANG,
                   help="idioma do caso (padrão: %(default)s)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="noirforge",
        description="Gerador e jogo de casos de ficção policial (noir paulistano).",
    )
    parser.add_argument("--version", action="version", version=f"noirforge {__version__}")
    parser.add_argument("--db", default=DEFAULT_DB, help="caminho do banco SQLite")
    sub = parser.add_subparsers(dest="command", required=True)

    new = sub.add_parser("new", help="gera um novo caso")
    _add_generation_args(new)
    new.add_argument("--save", action="store_true", help="salva no banco")
    new.add_argument("--solution", action="store_true", help="revela a solução")
    new.add_argument("--format", choices=("md", "json"), default="md")

    play = sub.add_parser("play", help="joga: interrogue, deduza e acuse")
    _add_generation_args(play)

    sub.add_parser("list", help="lista os casos salvos")

    show = sub.add_parser("show", help="mostra um caso salvo")
    show.add_argument("id", type=int)
    show.add_argument("--solution", action="store_true")
    show.add_argument("--format", choices=("md", "json"), default="md")

    export = sub.add_parser("export", help="exporta um caso (Markdown ou JSON)")
    export.add_argument("id", type=int)
    export.add_argument("--out", required=True, help="arquivo de saída (.md ou .json)")
    export.add_argument("--solution", action="store_true")
    export.add_argument("--format", choices=("md", "json"),
                        help="padrão: json se --out terminar em .json, senão md")

    delete = sub.add_parser("delete", help="apaga um caso salvo")
    delete.add_argument("id", type=int)

    sub.add_parser("stats", help="estatísticas dos casos salvos")
    return parser


def _render(case: Case, reveal: bool, fmt: str) -> str:
    return render_json(case, reveal) if fmt == "json" else render_case(case, reveal)


def main(argv: Optional[Sequence[str]] = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command in ("new", "play"):
        try:
            case = generate_case(args.seed, args.suspects, args.lang)
        except ValueError as exc:
            parser.error(str(exc))
        if args.command == "play":
            game.play(case, get_locale(args.lang))
            return 0
        print(_render(case, args.solution, args.format))
        if args.save:
            conn = db.connect(args.db)
            try:
                case_id = db.save_case(conn, case)
            finally:
                conn.close()
            print(f"💾 Caso salvo com id {case_id} em {args.db}")
        return 0

    conn = db.connect(args.db)
    try:
        if args.command == "list":
            rows = db.list_cases(conn)
            if not rows:
                print("Nenhum caso salvo ainda. Use: noirforge new --save")
            for r in rows:
                print(f"{r['id']:>3}  {r['lang']}  seed={r['seed']:<7} "
                      f"{r['num_suspects']} suspeitos  {r['era']:<16} {r['title']}")
            return 0

        if args.command in ("show", "export"):
            loaded = db.load_case(conn, args.id)
            if loaded is None:
                print(f"Caso {args.id} não encontrado.", file=sys.stderr)
                return 1
            if args.command == "show":
                print(_render(loaded, args.solution, args.format))
            else:
                fmt = args.format or ("json" if args.out.lower().endswith(".json") else "md")
                with open(args.out, "w", encoding="utf-8") as fh:
                    fh.write(_render(loaded, args.solution, fmt))
                print(f"📄 Exportado para {args.out}")
            return 0

        if args.command == "delete":
            if db.delete_case(conn, args.id):
                print(f"Caso {args.id} apagado.")
                return 0
            print(f"Caso {args.id} não encontrado.", file=sys.stderr)
            return 1

        if args.command == "stats":
            s = db.stats(conn)
            print(f"Casos salvos: {s['total']}")
            print("Armas mais comuns:")
            for name, n in s["weapons"]:  # type: ignore[attr-defined]
                print(f"  {n}x {name}")
            print("Relação mais comum do culpado com a vítima:")
            for name, n in s["culprit_relations"]:  # type: ignore[attr-defined]
                print(f"  {n}x {name}")
            return 0
    finally:
        conn.close()
    return 0
