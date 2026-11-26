# -*- coding: utf-8 -*-
"""Cria 50 casos Markdown pequenos e independentes em tests/characterization/cases/."""
from __future__ import unicode_literals

import io
import os

CASES_DIR = os.path.join('tests', 'characterization', 'cases')

CASES = {
    # Parágrafos e quebras de linha (01–05)
    '01_paragraph_simple.md': 'Texto simples dentro de um parágrafo.\n',
    '02_paragraph_multiple.md': 'Primeiro parágrafo.\n\nSegundo parágrafo.\n',
    '03_paragraph_softbreak.md': 'Linha um do parágrafo\nlinha dois no mesmo parágrafo.\n',
    '04_paragraph_hardbreak_spaces.md': 'Linha com quebra dura  \napós dois espaços.\n',
    '05_paragraph_hardbreak_backslash.md': 'Linha com quebra dura\\\napós barra invertida.\n',

    # Títulos ATX e Setext (06–10)
    '06_atx_heading_h1.md': '# Título nível 1\n',
    '07_atx_heading_h2_h6.md': '## Título 2\n\n### Título 3\n\n###### Título 6\n',
    '08_atx_heading_closing_hashes.md': '## Título com hashes no fim ##\n',
    '09_setext_heading_equals.md': 'Título Setext nível 1\n====================\n',
    '10_setext_heading_dashes.md': 'Título Setext nível 2\n--------------------\n',

    # Listas simples, aninhadas e ordenadas (11–18)
    '11_list_bullet_dash.md': '- Item A\n- Item B\n- Item C\n',
    '12_list_bullet_plus_star.md': '+ Item 1\n+ Item 2\n\n* Item X\n* Item Y\n',
    '13_list_ordered_from_one.md': '1. Primeiro\n2. Segundo\n3. Terceiro\n',
    '14_list_ordered_custom_start.md': '5. Começa em cinco\n6. Próximo item\n',
    '15_list_ordered_paren_delimiter.md': '1) Item com parêntese\n2) Segundo item\n',
    '16_list_nested_bullet.md': '- Pai 1\n  - Filho 1.1\n  - Filho 1.2\n- Pai 2\n',
    '17_list_nested_mixed.md': '1. Ordenado pai\n   - Marcado filho\n2. Ordenado dois\n',
    '18_list_loose_vs_tight.md': '- Item apertado 1\n- Item apertado 2\n\n- Item solto 1\n\n- Item solto 2\n',

    # Ênfase, negrito, links, imagens e referências (19–28)
    '19_emphasis_asterisk.md': 'Texto com *ênfase em asterisco*.\n',
    '20_emphasis_underscore.md': 'Texto com _ênfase em sublinhado_.\n',
    '21_strong_asterisk.md': 'Texto com **negrito duplo**.\n',
    '22_strong_underscore.md': 'Texto com __negrito com sublinhado__.\n',
    '23_emphasis_and_strong_combined.md': 'Texto com ***ênfase e negrito*** e **parte em *itálico***.\n',
    '24_link_inline_basic.md': 'Visite [o site](https://example.com).\n',
    '25_link_inline_with_title.md': 'Veja [documentação](https://example.com/docs "Título do link").\n',
    '26_link_autolink.md': 'Link automático <https://example.com/auto> e e-mail <contato@example.com>.\n',
    '27_image_inline_alt_title.md': '![Texto alternativo](https://example.com/img.png "Legenda da imagem")\n',
    '28_link_reference_definition.md': 'Veja a [referência][ref1] e [atalho].\n\n[ref1]: https://example.com/ref1 "Ref 1"\n[atalho]: https://example.com/short\n',

    # Citações, blocos de código e código inline (29–36)
    '29_blockquote_simple.md': '> Citação simples em bloco.\n',
    '30_blockquote_nested.md': '> Nível 1\n>> Nível 2 aninhado\n',
    '31_blockquote_multiline_lazy.md': '> Primeira linha da citação\ncontinuação preguiçosa na mesma citação.\n',
    '32_code_fenced_backticks.md': '```python\ndef soma(a, b):\n    return a + b\n```\n',
    '33_code_fenced_tildes.md': '~~~\nbloco com til\n~~~\n',
    '34_code_fenced_no_info.md': '```\nbloco sem linguagem\n```\n',
    '35_code_indented_four_spaces.md': '    x = 10\n    y = 20\n',
    '36_code_span_inline.md': 'Use `codigo_inline` e ``crase `interna` dupla``.\n',

    # HTML inline e em bloco (37–41)
    '37_html_block_div.md': '<div>\n  <p>Conteúdo dentro de div</p>\n</div>\n',
    '38_html_block_pre.md': '<pre>texto\n  formatado</pre>\n',
    '39_html_block_comment.md': '<!-- comentário HTML de bloco -->\n',
    '40_html_inline_span.md': 'Palavra com <span class="destaque">destaque inline</span>.\n',
    '41_html_inline_br_hr.md': 'Linha um<br>Linha dois\n\n<hr>\n',

    # Caracteres especiais, escapes, entidades e bordas (42–50)
    '42_backslash_escapes_punctuation.md': '\\*não é ênfase\\* \\[não é link\\] \\\\barra\\\\\n',
    '43_backslash_non_punctuation.md': 'Letra \\a e dígito \\1 mantêm a barra.\n',
    '44_entity_named.md': 'Entidades &amp; &lt; &gt; &quot; &copy;\n',
    '45_entity_numeric_decimal_hex.md': 'Decimal &#65; e hexadecimal &#x42;.\n',
    '46_thematic_break_dashes.md': 'Acima\n\n---\n\nAbaixo\n',
    '47_thematic_break_asterisks.md': '* * *\n',
    '48_edge_empty_and_whitespace.md': '   \n\t\n',
    '49_edge_ambiguous_delimiters.md': '*a*b**c**d***e***f\n',
    '50_edge_nul_and_unicode.md': 'Acentos: áéíóú çãõ — NUL: \x00 fim.\n',
}


def main():
    os.makedirs(CASES_DIR, exist_ok=True)
    for filename, content in sorted(CASES.items()):
        path = os.path.join(CASES_DIR, filename)
        with io.open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    print('Criados %d arquivos em %s.' % (len(CASES), CASES_DIR))


if __name__ == '__main__':
    main()