# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e
[Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [2.0.0] - 2026-11-03

### Adicionado
- **Modo de jogo** (`noirforge play`): interrogue suspeitos, deduza e acuse. Cada pergunta nova custa 5 pontos.
- **Bilíngue** (`--lang pt|en`): a mesma seed conta a mesma história nos dois idiomas.
- **Saída JSON** (`--format json`), com visão pública sem spoilers e visão completa com `--solution`.
- Exportação para `.json` (formato inferido pela extensão).
- Migração automática de bancos criados pela v1.x.
- Tipagem completa (`py.typed`), `mypy --strict` e `ruff`.
- CI em Linux, macOS e Windows (Python 3.9 a 3.13), com cobertura mínima de 90%.
- Dockerfile, workflow de release para PyPI, Dependabot e templates de issue/PR.

### Alterado
- Código reorganizado em módulos (`models`, `locales`, `interrogate`, `game`).
- Tipos de pista agora são `clue` e `red_herring`.
- Casos salvos passam a guardar o idioma; a mesma seed pode existir em idiomas diferentes.

## [1.0.0] - 2026-11-03

### Adicionado
- Gerador determinístico de casos, persistência em SQLite e CLI.
