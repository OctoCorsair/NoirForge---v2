<div align="center">

# 🕵️ NoirForge

**Gere mistérios de ficção policial. Ou jogue um: interrogue, deduza e acuse.**

Noir paulistano, bilíngue (🇧🇷 PT · 🇺🇸 EN), determinístico e sem nenhuma dependência.

[![CI](https://github.com/OctoCorsair/NoirForge/actions/workflows/ci.yml/badge.svg)](https://github.com/OctoCorsair/NoirForge/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.9%20→%203.13-3776AB?logo=python&logoColor=white)
![Typed](https://img.shields.io/badge/tipos-mypy%20strict-2a6db2)
![Deps](https://img.shields.io/badge/depend%C3%AAncias-zero-7f1d1d)
![License](https://img.shields.io/badge/licen%C3%A7a-MIT-1f2937)

[English](README.en.md) · [Arquitetura](docs/ARCHITECTURE.md) · [Contribuir](CONTRIBUTING.md) · [Changelog](CHANGELOG.md)

</div>

---

## ✨ Por que o NoirForge

- 🎲 **Determinístico:** a mesma *seed* gera sempre o mesmo caso. Compartilhe um mistério com um número.
- 🧩 **Sempre resolvível:** todo caso tem um culpado, três pistas que levam a ele e falsas pistas, cada uma com explicação.
- 🌎 **Mesma história, vários idiomas:** `--seed 7` conta a mesma trama em português e em inglês.
- 🎮 **Modo de jogo:** interrogue suspeitos, pressione, acuse e ganhe pontos.
- 🗄️ **SQLite embutido:** salve, liste, reabra, exporte (Markdown ou JSON) e veja estatísticas.
- 🛡️ **Sem spoilers por padrão:** a solução só aparece quando você pede.
- 🧪 **Engenharia séria:** tipagem estrita, 57 testes, CI em Linux, macOS e Windows, Dockerfile e migração automática de banco.

## 🚀 Instalação

```bash
git clone https://github.com/OctoCorsair/NoirForge.git
cd NoirForge
pip install -e .
```

Ou sem instalar nada:

```bash
docker build -t noirforge . && docker run --rm -it noirforge play
```

## 🎮 Jogue

```bash
noirforge play                 # caso aleatório, em português
noirforge play --lang en       # em inglês
noirforge play --seed 7        # desafie um amigo com o mesmo caso
```

Exemplo de partida (`--seed 7 --lang en`):

```text
[1] Review the case   [2] Interrogate   [3] Accuse   [0] Give up
> 2
Whom to question? (0 to go back)
  [1] Januário Camargo   [2] Aurélio Guedes   [3] Euclides Albuquerque   [4] Berenice Barcellos
> 2
What to ask Aurélio Guedes? (0 to go back)
  [1] Where were you when it happened?
  [2] Who gains from the victim's death?
  [3] How did you know the victim?
  [4] Pressure: 'You are hiding something.'
> 4
Under pressure, Aurélio Guedes's composure cracks. Aurélio Guedes was secretly
negotiating the sale of their own business, which is why they acted suspiciously.
```

**A regra do jogo:** quem é inocente cede sob pressão e explica por que parecia culpado. O culpado nunca cede: muda de assunto, o álibi não fecha e as mãos tremem. Cada pergunta nova custa 5 pontos, então acuse com o menor número de perguntas possível.

## 🔦 Gere casos

```bash
noirforge new                          # caso aleatório, sem revelar o culpado
noirforge new --seed 7                 # sempre o mesmo caso
noirforge new --suspects 6 --lang en   # 3 a 6 suspeitos, em inglês
noirforge new --seed 7 --solution      # revela culpado, falsas pistas e reviravolta
noirforge new --seed 7 --format json   # saída JSON, ótima para integrar com outros programas
```

Veja exemplos prontos em [`examples/`](examples/).

### Exemplo de saída

```text
# Fumaça e Chantagem
*São Paulo, 1947 · seed 7*

**Vítima:** Fausto Falcão, cantor de cabaré.
**Cena do crime:** o corpo foi encontrado no sótão, num hotel decadente da Santa Ifigênia.
**Arma:** um castiçal de bronze.

## Suspeitos
- **Januário Camargo** (irmão): motivo, uma vingança antiga; conta que esperava um trem na Estação da Luz.
- **Aurélio Guedes** (vizinho): motivo, uma herança prestes a ser alterada; garante que ajudava a fechar o caixa de uma padaria.
- **Euclides Albuquerque** (afilhado): motivo, chantagem que ameaçava arruinar sua reputação; diz que jogava cartas nos fundos de um bar.
- **Berenice Barcellos** (sócia): motivo, ciúme doentio; alega ter ido ao cinema na Avenida São João.

## Evidências
1. Só Januário Camargo tinha a chave do cadeado do sótão.
2. Aurélio Guedes sumiu da cidade no dia seguinte.
3. Dinheiro vivo foi encontrado escondido na casa de Euclides Albuquerque.
4. Testemunhas viram Berenice Barcellos discutindo com a vítima poucas horas antes do crime.
5. O castiçal de bronze que sumiu da sala apareceu lavado às pressas na casa de Januário Camargo.
6. Ninguém ouviu Januário Camargo perguntar como a vítima morreu.

> 🔎 Quem fez isso? Revele com `--solution` ou jogue com `noirforge play`.
```

## 🗄️ Salve e organize

```bash
noirforge new --seed 7 --save          # salva em noirforge.db
noirforge list                         # lista os casos
noirforge show 1 --solution            # reabre um caso
noirforge export 1 --out caso.md       # exporta em Markdown (ou .json)
noirforge stats                        # estatísticas via SQL
noirforge delete 1                     # apaga um caso
```

Mude o banco com `--db caminho.db` ou `NOIRFORGE_DB`. Mude o idioma padrão com `NOIRFORGE_LANG=en`.

## 🐍 Use como biblioteca

```python
from noirforge import generate_case, render_case

case = generate_case(seed=7, num_suspects=5, lang="en")
print(case.culprit.name)
print(render_case(case, reveal=True))
```

## 🧠 Como funciona

1. Uma única `random.Random(seed)` sorteia vítima, suspeitos (nomes únicos, com concordância de gênero), álibis e segredos.
2. Escolhe **um culpado**, cujo álibi é falso.
3. Cria **3 pistas verdadeiras** (arma, local e uma geral) e até **3 falsas pistas** contra inocentes distintos.
4. Embaralha as evidências e define uma reviravolta.

Detalhes e decisões de projeto em [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## ✍️ Personalize e contribua

Todo o conteúdo narrativo vive em [`src/noirforge/locales/`](src/noirforge/locales/). Quer outra cidade, outra época ou um idioma novo? Veja o [guia de contribuição](CONTRIBUTING.md): os testes avisam exatamente o que falta.

```bash
make install   # ambiente de desenvolvimento
make check     # lint + tipos + testes com cobertura
```

## 🛣️ Roadmap

- [ ] Mais cenários (Rio, Recife, Porto Alegre) e mais idiomas
- [ ] Níveis de dificuldade (menos pistas, mais falsas pistas)
- [ ] Exportar o caso em PDF
- [ ] Interface web

## 📄 Licença

MIT. Veja [LICENSE](LICENSE). Para citar, use o [CITATION.cff](CITATION.cff).

<div align="center">

*Código limpo. Enredo sujo.* 🚬
Feito por [OctoCorsair](https://github.com/OctoCorsair)

</div>
