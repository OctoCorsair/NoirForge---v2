<div align="center">

# 🕵️ NoirForge

**Generate crime-fiction mysteries. Or play one: interrogate, deduce, accuse.**

São Paulo noir, bilingual (🇧🇷 PT · 🇺🇸 EN), deterministic, zero dependencies.

[![CI](https://github.com/OctoCorsair/NoirForge/actions/workflows/ci.yml/badge.svg)](https://github.com/OctoCorsair/NoirForge/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.9%20→%203.13-3776AB?logo=python&logoColor=white)
![Typed](https://img.shields.io/badge/types-mypy%20strict-2a6db2)
![Deps](https://img.shields.io/badge/dependencies-zero-7f1d1d)
![License](https://img.shields.io/badge/license-MIT-1f2937)

[Português](README.md) · [Architecture](docs/ARCHITECTURE.md) · [Contributing](CONTRIBUTING.md) · [Changelog](CHANGELOG.md)

</div>

---

## ✨ Why NoirForge

- 🎲 **Deterministic:** the same *seed* always yields the same case. Share a mystery with a single number.
- 🧩 **Always solvable:** every case has one culprit, three clues that point to them, and red herrings that each come with an explanation.
- 🌎 **Same story, many languages:** `--seed 7` tells the same plot in Portuguese and English.
- 🎮 **Game mode:** question suspects, apply pressure, accuse, and score points.
- 🗄️ **Built-in SQLite:** save, list, reopen, export (Markdown or JSON) and query stats.
- 🛡️ **Spoiler-free by default:** the solution appears only when you ask for it.
- 🧪 **Real engineering:** strict typing, 57 tests, CI on Linux/macOS/Windows, Dockerfile, automatic database migration.

## 🚀 Install

```bash
git clone https://github.com/OctoCorsair/NoirForge.git
cd NoirForge
pip install -e .
```

Or with Docker:

```bash
docker build -t noirforge . && docker run --rm -it noirforge play --lang en
```

## 🎮 Play

```bash
noirforge play --lang en       # random case
noirforge play --seed 7        # challenge a friend with the same case
```

**The rule of the game:** innocent suspects crack under pressure and explain why they looked guilty. The culprit never cracks: they change the subject, the alibi doesn't add up, and their hands shake. Each new question costs 5 points, so accuse with as few questions as you can.

## 🔦 Generate

```bash
noirforge new --lang en                 # random case, culprit hidden
noirforge new --seed 7 --lang en        # always the same case
noirforge new --suspects 6 --lang en    # 3 to 6 suspects
noirforge new --seed 7 --solution       # reveal culprit, red herrings and twist
noirforge new --seed 7 --format json    # JSON output for other programs
```

See ready-made samples in [`examples/`](examples/).

## 🗄️ Save and organize

```bash
noirforge new --seed 7 --save           # stores in noirforge.db
noirforge list
noirforge show 1 --solution
noirforge export 1 --out case.json      # Markdown or JSON, inferred from extension
noirforge stats                         # SQL-powered statistics
noirforge delete 1
```

Change the database with `--db path.db` or `NOIRFORGE_DB`. Change the default language with `NOIRFORGE_LANG=en`.

## 🐍 Use as a library

```python
from noirforge import generate_case, render_case

case = generate_case(seed=7, num_suspects=5, lang="en")
print(case.culprit.name)
print(render_case(case, reveal=True))
```

## 🧠 How it works

1. A single `random.Random(seed)` draws the victim, suspects (unique names, gender-aware), alibis and secrets.
2. It picks **one culprit** whose alibi is false.
3. It creates **3 genuine clues** (weapon, location, general) and up to **3 red herrings** against distinct innocents.
4. It shuffles the evidence and picks a twist.

Design notes in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## ✍️ Customize and contribute

All narrative content lives in [`src/noirforge/locales/`](src/noirforge/locales/). Want another city, era or language? See [CONTRIBUTING.md](CONTRIBUTING.md): the tests tell you exactly what is missing.

```bash
make install   # dev environment
make check     # lint + types + tests with coverage
```

## 🛣️ Roadmap

- [ ] More settings (Rio, Recife, Porto Alegre) and more languages
- [ ] Difficulty levels (fewer clues, more red herrings)
- [ ] PDF export
- [ ] Web interface

## 📄 License

MIT. See [LICENSE](LICENSE). To cite, use [CITATION.cff](CITATION.cff).

<div align="center">

*Clean code. Dirty plot.* 🚬
Made by [OctoCorsair](https://github.com/OctoCorsair)

</div>
