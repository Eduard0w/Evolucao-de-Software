# Testes de Caracterização — CommonMark

Este diretório contém a suíte de testes de caracterização para registrar o comportamento de referência do `commonmark.py` em **HTML** e **AST** (serializada em JSON), protegendo contra regressões durante a evolução e refatoração do código em `Eduard0w/Evolucao-de-Software`.

## Estrutura

* `cases/*.md`: aproximadamente 50 entradas Markdown pequenas e independentes cobrindo parágrafos, títulos, listas, ênfase, negrito, links, imagens, referências, citações, blocos de código, código inline, HTML, escapes, entidades e casos de borda.
* `snapshots/*.html` e `snapshots/*.ast.json`: saídas de referência geradas via `commonmark.commonmark(text, format="html")` e `commonmark.commonmark(text, format="json")`.
* `test_characterization.py`: testes `pytest` em modo somente-leitura que comparam a saída atual com os arquivos de referência.

## Como os Snapshots Foram Gerados

Os snapshots de referência foram gerados a partir da base original antes das refatorações, no commit **`40c7560`**, usando um `git worktree` temporário para importar o `commonmark` original sem alterar os arquivos de trabalho:

```bash
git worktree add /tmp/commonmark-40c7560 40c7560
PYTHONPATH=/tmp/commonmark-40c7560 python3 scripts/generate_characterization_snapshots.py
git worktree remove /tmp/commonmark-40c7560 --force
```
## Como Executar os Testes

A execução normal com pytest apenas lê os arquivos em cases/ e snapshots/ e nunca regrava os snapshots automaticamente:

```Bash
python3 -m pytest tests/characterization/ -v
```

### Atualização Manual e Explícita de Snapshots

Os arquivos em snapshots/ não devem ser atualizados durante execuções comuns de teste. Caso ocorra uma mudança de comportamento intencional e aprovada:

1. Execute explicitamente o script gerador apontando o PYTHONPATH para o código-alvo desejado (ou sem PYTHONPATH para usar o código local atual):
```Bash
python3 scripts/generate_characterization_snapshots.py
```
2. Inspecione todas as alterações geradas com git diff tests/characterization/snapshots/ para confirmar que cada diferença corresponde à mudança intencional.
3. Inclua os snapshots atualizados no commit de forma consciente e justificada.
