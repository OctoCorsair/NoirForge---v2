# Contribuindo com o NoirForge

Obrigado pelo interesse! Toda contribuição é bem-vinda: código, idiomas, cenários, correções de texto.

## Ambiente

```bash
git clone https://github.com/OctoCorsair/NoirForge.git
cd NoirForge
python -m venv .venv && source .venv/bin/activate
make install        # instala em modo editável com ferramentas de desenvolvimento
make check          # lint + tipos + testes com cobertura
```

## Regras do projeto

- **Zero dependências em runtime.** Só biblioteca padrão.
- **Determinismo é sagrado.** A mesma seed precisa gerar sempre o mesmo caso. Se você mudar a ordem das chamadas ao `random`, isso muda todas as seeds: registre no `CHANGELOG.md` como mudança incompatível.
- **Todo caso precisa ser resolvível.** Existe sempre um culpado e pistas que levam a ele. Os testes verificam isso em centenas de seeds.
- Código tipado (`mypy --strict`) e formatado com `ruff`.

## Adicionando um idioma

1. Copie `src/noirforge/locales/en.py` para `locales/<codigo>.py` e traduza.
2. Mantenha **o mesmo número de itens em cada lista** e **os mesmos `{placeholders}`** em cada texto de interface. É isso que faz a mesma seed contar a mesma história em todos os idiomas.
3. Registre o idioma em `locales/__init__.py`.
4. Rode `make test`. `tests/test_locales.py` aponta exatamente o que está diferente.

## Adicionando conteúdo (armas, locais, motivos…)

Adicione o item **em todos os idiomas ao mesmo tempo**. Os testes falham se as listas ficarem com tamanhos diferentes.

## Pull requests

- Um assunto por PR, com testes.
- Atualize o `CHANGELOG.md`.
- Descreva o *porquê*, não só o *o quê*.
