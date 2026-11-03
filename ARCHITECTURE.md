# Arquitetura

```text
            ┌──────────────┐
            │  locales/    │  conteúdo narrativo + textos de interface (pt, en)
            └──────┬───────┘
                   │ Locale
┌──────────┐   ┌───▼───────┐   ┌───────────┐
│  seed    ├──►│ generator │──►│  models   │  Case · Suspect · Clue
└──────────┘   └───────────┘   └─────┬─────┘
                                     │
        ┌──────────────┬─────────────┼───────────────┬──────────────┐
        ▼              ▼             ▼               ▼              ▼
   render.py     interrogate.py     db.py         game.py        cli.py
 (Markdown/JSON)  (diálogos)      (SQLite)     (partida)    (argparse)
```

## Decisões de projeto

**Determinismo.** `generate_case` usa um único `random.Random(seed)` e consome números sempre na mesma ordem. Sem relógio, sem estado global. Isso permite compartilhar um mistério só com um número.

**Mesma história, vários idiomas.** O gerador sorteia *índices* sobre listas que têm o mesmo tamanho em todos os idiomas. Por isso `--seed 7` produz os mesmos personagens, o mesmo culpado e as mesmas pistas em `pt` e `en`, mudando só o texto. `tests/test_locales.py` garante o paralelismo.

**Resolubilidade por construção.** Todo caso tem exatamente um culpado e:

- 3 pistas verdadeiras ligadas a ele (arma, local e uma pista geral);
- até 3 falsas pistas, cada uma contra um inocente diferente, com explicação.

No modo de jogo, inocentes cedem sob pressão e explicam suas falsas pistas, enquanto o culpado nunca cede. A dedução é possível por eliminação.

**Sem spoilers por padrão.** `render_case` e `render_json` só incluem culpado, tipo das pistas e reviravolta com `reveal=True`. Há testes que verificam a ausência de vazamentos no JSON público.

**Banco de dados.** Três tabelas (`cases`, `suspects`, `clues`) com chaves estrangeiras e `ON DELETE CASCADE`. Salvar é idempotente por `(seed, num_suspects, lang)`. Bancos da v1.x são migrados automaticamente ao abrir.

**Testabilidade.** O jogo recebe `input_fn` e `output_fn` injetáveis. A CLI devolve códigos de saída em vez de chamar `sys.exit`, exceto nos erros de `argparse`.

## Onde mexer

| Quero…                          | Arquivo                                  |
|---------------------------------|------------------------------------------|
| Adicionar armas, locais, motivos | `locales/pt.py` e `locales/en.py`        |
| Criar um idioma                 | `locales/<codigo>.py` + `locales/__init__.py` |
| Mudar a lógica de geração       | `generator.py`                           |
| Mudar perguntas do interrogatório | `interrogate.py` + chaves `q_*`/`ans_*` |
| Mudar pontuação                 | `game.py` (`QUESTION_COST`)              |
