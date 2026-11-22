# Evidências de Refatoração — Eduardo
**Frente 1:** Processamento e Modularização de Blocos Markdown
**Card 02:** Refatorar `parse_list_marker` (`commonmark/blocks.py`)

> Evidência específica do Card 02. O registro conjunto dos cards permanece em [`eduardo.md`](eduardo.md).

---

## 1. Contexto e Motivação
`parse_list_marker` concentrava em uma única função a identificação de listas não ordenadas, ordenadas, as validações de espaçamento/delimitadores e o cálculo de padding, com **Complexidade Ciclomática (CC) 18**. A refatoração separou essas responsabilidades sem alterar o formato do dicionário retornado nem o estado do parser.

O objetivo foi extrair a identificação de marcadores ordenados para um auxiliar próprio, isolar as validações de delimitadores/espaçamento e reduzir o número de condicionais concentradas na função principal.

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

## 6. Comparativo de Saídas (HTML e AST)

A árvore original foi extraída do commit `1e7e34a` com `git archive` e as duas implementações foram executadas sobre o mesmo corpus: os **649 exemplos de `spec.txt`** (com `→` convertido em tab, como na suíte oficial) e **20 casos extras** de marcadores de lista. Para cada caso foram comparados o HTML gerado por `HtmlRenderer` e o dump da AST por `dumpAST`, incluindo `sourcepos` e `list_data`.

| Comparação | Casos | Divergências |
| :--- | :---: | :---: |
| HTML antes x depois | 669 | 0 |
| AST antes x depois | 669 | 0 |

- **HTML:** nenhuma alteração nas tags, atributos ou texto renderizado.
- **AST (Árvore Sintática):** nenhuma alteração na tipagem dos nós, `sourcepos`, `list_data` ou demais atributos.
- **Divergências detectadas:** 0.

## 7. Resultado
A identificação de marcadores ficou distribuída em funções pequenas e com responsabilidade única. O retorno original (`type`, `tight`, `bullet_char`, `start`, `delimiter`, `padding`, `marker_offset`) e os efeitos colaterais em `offset`, `column`, `indent` e `partially_consumed_tab` foram preservados.
