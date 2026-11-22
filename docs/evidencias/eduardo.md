# Evidências de Refatoração — Eduardo
**Frente 1:** Processamento e Modularização de Blocos Markdown  
**Cards:** 01 — Refatorar `Parser.incorporate_line`; 02 — Refatorar `parse_list_marker` (`commonmark/blocks.py`)

---

## 1. Contexto e Motivação
O método `Parser.incorporate_line` é o núcleo de ingestão e processamento de linhas do CommonMark. Anteriormente, ele acumulava múltiplas responsabilidades em um único bloco de código monolítico com mais de 140 linhas e **Complexidade Ciclomática (CC) 36**:
1. Sanitização de caracteres NUL de segurança.
2. Navegação na árvore sintática e validação de continuação de blocos abertos.
3. Despacho e identificação de abertura de novos blocos (`block_starts`).
4. Tratamento de parágrafos preguiçosos (*lazy paragraph continuation*).
5. Propagação de linhas em branco e fechamento de blocos desconectados.
6. Adição de texto a blocos existentes ou instanciação de nós de parágrafo.

O objetivo desta refatoração foi aplicar a técnica de **Extração de Métodos**, separando as responsabilidades em funções coesas e reduzindo a complexidade ciclomática, preservando 100% o comportamento original do parser.

---

## 2. Responsabilidades Extraídas

Foram extraídos métodos privados/auxiliares para lidar com fases bem delimitadas do ciclo de vida da linha:

1. **`sanitize_line(self, ln)`**:
   - *Responsabilidade:* Higienização de caracteres NUL (`\u0000` substituído por `\uFFFD`) para evitar vulnerabilidades de injeção.
2. **`continue_open_blocks(self, container, all_matched, ln)`**:
   - *Responsabilidade:* Iteração sobre os nós filhos abertos da AST e verificação de continuação através dos métodos `continue_()` de cada tipo de bloco. Retorna `(container, all_matched, should_return)`.
3. **`find_block_start(self, matched_leaf, container, ln)`**:
   - *Responsabilidade:* Otimização de busca e iteração sobre os métodos de início de bloco (`self.block_starts.METHODS`), identificando e abrindo novos containers ou nós folhas.
4. **`add_new_line(self, container, container_name, ln)`**:
   - *Responsabilidade:* Adição do texto ao bloco receptor adequado, verificação do critério de encerramento de blocos HTML (tipos 1 a 5) ou criação de um novo parágrafo.

---

## 3. Código: Antes vs. Depois

### Antes (`incorporate_line` monolítico)
```python
    def incorporate_line(self, ln):
        all_matched = True

        container = self.doc
        self.oldtip = self.tip
        self.offset = 0
        self.column = 0
        self.blank = False
        self.partially_consumed_tab = False
        self.line_number += 1

        # replace NUL characters for security
        if re.search(r'\u0000', ln) is not None:
            ln = re.sub(r'\0', '\uFFFD', ln)

        self.current_line = ln

        # Loop de continuação de blocos embutido
        while True:
            last_child = container.last_child
            if not (last_child and last_child.is_open):
                break
            container = last_child
            self.find_next_nonspace()
            rv = self.blocks[container.t].continue_(self, container)
            # ... múltiplas ramificações if/elif/else com CC alta ...

        # Loop de abertura de novos blocos embutido
        while not matched_leaf:
            # ... despacho e verificações de caracteres especiais ...

        # Lógica de inserção de texto e nós de parágrafo embutida
        if not self.all_closed and not self.blank and self.tip.t == 'paragraph':
            self.add_line()
        else:
            # ... dezenas de linhas de propagação e criação de parágrafos ...
```

### Depois (Modularizado e Coeso)
```python
    def incorporate_line(self, ln):
        """Analyze a line of text and update the document appropriately."""
        all_matched = True
        container = self.doc
        self.oldtip = self.tip
        self.offset = 0
        self.column = 0
        self.blank = False
        self.partially_consumed_tab = False
        self.line_number += 1

        # 1. Sanitização
        ln = self.sanitize_line(ln)
        self.current_line = ln

        # 2. Continuação de blocos abertos
        container, all_matched, should_return = (
            self.continue_open_blocks(container, all_matched, ln)
        )
        if should_return:
            return

        self.all_closed = (container == self.oldtip)
        self.last_matched_container = container

        matched_leaf = container.t != 'paragraph' and \
            self.blocks[container.t].accepts_lines

        # 3. Identificação e início de novos blocos
        container, matched_leaf = self.find_block_start(matched_leaf, container, ln)

        # 4. Adição de conteúdo / Lazy continuation
        if not self.all_closed and not self.blank and \
           self.tip.t == 'paragraph':
            self.add_line()
        else:
            self.close_unmatched_blocks()
            if self.blank and container.last_child:
                container.last_child.last_line_blank = True

            t = container.t
            last_line_blank = self.blank and \
                not (t == 'block_quote' or
                     (t == 'code_block' and container.is_fenced) or
                     (t == 'item' and
                      not container.first_child and
                      container.sourcepos[0][0] == self.line_number))

            cont = container
            while cont:
                cont.last_line_blank = last_line_blank
                cont = cont.parent

            container = self.add_new_line(container, t, ln)

        self.last_line_length = len(ln)
```

---

## 4. Métricas de Complexidade Ciclomática (CC)

A medição de complexidade ciclomática da AST demonstrou uma redução drástica:

| Método / Função | Complexidade Anterior | Complexidade Atual | Status |
| :--- | :---: | :---: | :---: |
| **`incorporate_line`** | **36** (Crítica) | **12** | **Redução de 66.7%** |
| `sanitize_line` | — *(embutido)* | **2** | Baixa / Ideal |
| `continue_open_blocks` | — *(embutido)* | **8** | Baixa (<= 10) |
| `find_block_start` | — *(embutido)* | **8** | Baixa (<= 10) |
| `add_new_line` | — *(embutido)* | **6** | Baixa (<= 10) |

---

## 5. Bateria de Testes e Validação de Regressão

### 5.1. Suíte Oficial de Especificação (`run_spec_tests.py`)
- Execução da suíte completa de conformidade com a especificação CommonMark (parágrafos, listas, citações, blocos de código, HTML blocks, títulos, etc.):
  - **Total:** 649 testes
  - **Passaram:** 649 testes
  - **Falhas:** 0 falhas

### 5.2. Testes Unitários e Casos de Borda (`unit_tests.py`)
Foram incorporados testes adicionais com `unittest.mock` para assegurar cobertura dos novos métodos isolados:
1. `test_sanitize_line_nul_character`:
   - Valida a substituição de byte `\u0000` por `\uFFFD`.
2. `test_continue_open_block_invalid_return_value`:
   - Simula um retorno inválido via mock no método `continue_`, garantindo o lançamento defensivo de `ValueError`.
- **Resultado:** 15 de 15 testes unitários executados com sucesso (OK).

---

## 6. Comparativo de Saídas (HTML e AST)
A geração de saídas antes e após a refatoração foi conferida contra os casos de teste de referência do CommonMark:
- **HTML:** Nenhuma alteração nas tags ou strings renderizadas.
- **AST (Árvore Sintática):** Nenhuma alteração na tipagem de nós, atributos ou posições na árvore.
- **Divergências detectadas:** 0.

---

# Card 02 — Refatorar `parse_list_marker` (`commonmark/blocks.py`)

## 1. Contexto e Motivação
`parse_list_marker` concentrava em uma única função a identificação de listas não ordenadas, ordenadas, as validações de espaçamento/delimitadores e o cálculo de padding, com **Complexidade Ciclomática (CC) 18**. A refatoração separou essas responsabilidades sem alterar o formato do dicionário retornado nem o estado do parser.

## 2. Responsabilidades extraídas

1. **`_parse_bullet_marker(rest)`**: reconhece `-`, `+` e `*` e devolve o match somente com `type` e `bullet_char`.
2. **`_parse_ordered_marker(rest, container_t)`**: reconhece `\d{1,9}` seguido de `.` ou `)`, extrai `start` e `delimiter` e aplica a regra de interrupção de parágrafo (somente `1.` pode interromper).
3. **`_has_space_after_marker` / `_has_content_after_marker`**: isolam a validação do caractere seguinte ao marcador e a existência de conteúdo não espaço.
4. **`_is_padding_space` / `_use_default_padding` / `_calculate_padding`**: isolam as regras de contagem de espaços, fallback para 1 espaço e reposicionamento de `offset`/`column`.

## 3. Código: Antes vs. Depois

### Antes (`parse_list_marker` monolítico, CC 18)
```python
def parse_list_marker(parser, container):
    """ Parse a list marker and return data on the marker (type,
    start, delimiter, bullet character, padding) or None."""
    rest = parser.current_line[parser.next_nonspace:]
    data = {
        'type': None,
        'tight': True,  # lists are tight by default
        'bullet_char': None,
        'start': None,
        'delimiter': None,
        'padding': None,
        'marker_offset': parser.indent,
    }
    if parser.indent >= 4:
        return None
    m = re.search(reBulletListMarker, rest)
    m2 = re.search(reOrderedListMarker, rest)
    if m:
        data['type'] = 'bullet'
        data['bullet_char'] = m.group()[0]
    elif m2 and (container.t != 'paragraph' or m2.group(1) == '1'):
        m = m2
        data['type'] = 'ordered'
        data['start'] = int(m.group(1))
        data['delimiter'] = m.group(2)
    else:
        return None

    # make sure we have spaces after
    nextc = peek(parser.current_line, parser.next_nonspace + len(m.group()))
    if not (nextc is None or nextc == '\t' or nextc == ' '):
        return None

    # if it interrupts paragraph, make sure first line isn't blank
    if container.t == 'paragraph' and \
       not re.search(
            reNonSpace,
            parser.current_line[parser.next_nonspace + len(m.group()):]):
        return None

    # we've got a match! advance offset and calculate padding
    parser.advance_next_nonspace()  # to start of marker
    parser.advance_offset(len(m.group()), True)  # to end of marker
    spaces_start_col = parser.column
    spaces_start_offset = parser.offset
    while True:
        parser.advance_offset(1, True)
        nextc = peek(parser.current_line, parser.offset)
        if parser.column - spaces_start_col < 5 and \
           is_space_or_tab(nextc):
            pass
        else:
            break
    blank_item = peek(parser.current_line, parser.offset) is None
    spaces_after_marker = parser.column - spaces_start_col
    if spaces_after_marker >= 5 or \
       spaces_after_marker < 1 or \
       blank_item:
        data['padding'] = len(m.group()) + 1
        parser.column = spaces_start_col
        parser.offset = spaces_start_offset
        if is_space_or_tab(peek(parser.current_line, parser.offset)):
            parser.advance_offset(1, True)
    else:
        data['padding'] = len(m.group()) + spaces_after_marker

    return data
```

### Depois (responsabilidades separadas)
```python
def _parse_bullet_marker(rest):
    match = re.search(reBulletListMarker, rest)
    if match is None:
        return None, None
    return match, {
        'type': 'bullet',
        'bullet_char': match.group()[0],
    }


def _parse_ordered_marker(rest, container_t):
    match = re.search(reOrderedListMarker, rest)
    if match is None or (container_t == 'paragraph' and
                         match.group(1) != '1'):
        return None, None
    return match, {
        'type': 'ordered',
        'start': int(match.group(1)),
        'delimiter': match.group(2),
    }


def _has_space_after_marker(parser, marker_len):
    nextc = peek(parser.current_line, parser.next_nonspace + marker_len)
    return nextc is None or is_space_or_tab(nextc)


def _has_content_after_marker(parser, marker_len):
    return bool(re.search(
        reNonSpace,
        parser.current_line[parser.next_nonspace + marker_len:]))


def _is_padding_space(parser, spaces_start_col):
    return (
        parser.column - spaces_start_col < 5 and
        is_space_or_tab(peek(parser.current_line, parser.offset))
    )


def _use_default_padding(spaces_after_marker, blank_item):
    return spaces_after_marker >= 5 or spaces_after_marker < 1 or blank_item


def _calculate_padding(parser, marker_len, data):
    parser.advance_next_nonspace()
    parser.advance_offset(marker_len, True)
    spaces_start_col = parser.column
    spaces_start_offset = parser.offset

    parser.advance_offset(1, True)
    while _is_padding_space(parser, spaces_start_col):
        parser.advance_offset(1, True)

    blank_item = peek(parser.current_line, parser.offset) is None
    spaces_after_marker = parser.column - spaces_start_col
    if _use_default_padding(spaces_after_marker, blank_item):
        data['padding'] = marker_len + 1
        parser.column = spaces_start_col
        parser.offset = spaces_start_offset
        if is_space_or_tab(peek(parser.current_line, parser.offset)):
            parser.advance_offset(1, True)
    else:
        data['padding'] = marker_len + spaces_after_marker


def parse_list_marker(parser, container):
    """ Parse a list marker and return data on the marker (type,
    start, delimiter, bullet character, padding) or None."""
    if parser.indent >= 4:
        return None

    rest = parser.current_line[parser.next_nonspace:]
    match, marker_data = _parse_bullet_marker(rest)
    if match is None:
        match, marker_data = _parse_ordered_marker(rest, container.t)
    if match is None:
        return None

    marker_len = len(match.group())
    if not _has_space_after_marker(parser, marker_len):
        return None
    if container.t == 'paragraph' and \
       not _has_content_after_marker(parser, marker_len):
        return None

    data = {
        'type': marker_data['type'],
        'tight': True,  # lists are tight by default
        'bullet_char': marker_data.get('bullet_char'),
        'start': marker_data.get('start'),
        'delimiter': marker_data.get('delimiter'),
        'padding': None,
        'marker_offset': parser.indent,
    }
    _calculate_padding(parser, marker_len, data)

    return data
```

## 4. Métricas de Complexidade Ciclomática (CC)

Medição com `radon cc commonmark/blocks.py -s`; valores anteriores obtidos de `git show HEAD:commonmark/blocks.py`.

| Função | CC anterior | CC atual | Status |
| :--- | :---: | :---: | :--- |
| **`parse_list_marker`** | **18** | **7** | **Redução de 61,1%** |
| `_parse_ordered_marker` | — *(embutido)* | 4 | Extraída |
| `_calculate_padding` | — *(embutido)* | 4 | Extraída |
| `_use_default_padding` | — *(embutido)* | 3 | Extraída |
| `_parse_bullet_marker` | — *(embutido)* | 2 | Extraída |
| `_has_space_after_marker` | — *(embutido)* | 2 | Extraída |
| `_is_padding_space` | — *(embutido)* | 2 | Extraída |
| `_has_content_after_marker` | — *(embutido)* | 1 | Extraída |

Nenhuma função extraída ultrapassa CC 4.

## 5. Testes realizados

- `python -m pytest -q`: **24 testes passaram**.
- `python -m commonmark.tests.unit_tests`: **22 testes, OK**.
- `python -m commonmark.tests.run_spec_tests`: **649 testes passaram, 0 falhas**.
- Comparação automatizada com a implementação original (`git show HEAD`): **4752 combinações** de marcadores, espaçamentos, indentação e tipo de container, com **0 divergências** de retorno e de estado do parser.

Cenários cobertos em `commonmark/tests/unit_tests.py` (`TestParseListMarker`):
- listas iniciadas por `-`, `+` e `*`, com `bullet_char` correto;
- listas ordenadas `1.`, `12)` e `123.`, com `start`, `delimiter` e padding corretos;
- delimitadores `.` e `)`;
- interrupção de parágrafo (`2.` não interrompe; `1.` interrompe);
- espaçamento válido (1 a 4 espaços) e inválido (sem espaço; 5 ou mais espaços caem no padding padrão);
- entradas que não representam listas (`text`, `1.1 item`, indentação >= 4);
- formato completo do retorno, incluindo `tight`, `padding` e `marker_offset`.

## 6. Resultado
A identificação de marcadores ficou distribuída em funções pequenas e com responsabilidade única. O retorno original (`type`, `tight`, `bullet_char`, `start`, `delimiter`, `padding`, `marker_offset`) e os efeitos colaterais em `offset`, `column`, `indent` e `partially_consumed_tab` foram preservados.
