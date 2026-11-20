#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utilitário para geração e comparação de Snapshots (HTML e AST).

Uso:
    python tools/compare_snapshots.py               # Exibe HTML e AST dos casos de teste
    python tools/compare_snapshots.py > snapshot.txt # Salva snapshot para comparação com diff
"""

from __future__ import unicode_literals
import io
import sys
from contextlib import redirect_stdout

import commonmark
from commonmark.blocks import Parser
from commonmark.render.html import HtmlRenderer
from commonmark.dump import dumpAST

# Casos de teste de referência cobrindo diferentes estruturas de blocos e inlines
TEST_CASES = {
    "01_paragrafos_e_enfase": (
        "*Texto com ênfase*, **negrito** e _itálico_.\n\n"
        "Segundo parágrafo com linha comum."
    ),
    "02_listas_nao_ordenadas": (
        "- Item 1\n"
        "- Item 2\n"
        "  - Subitem A\n"
        "  - Subitem B\n"
        "- Item 3"
    ),
    "03_listas_ordenadas": (
        "1. Primeiro passo\n"
        "2. Segundo passo\n"
        "   1. Subpasso 2.1\n"
        "3. Terceiro passo"
    ),
    "04_citacao_em_bloco": (
        "> Esta é uma citação de bloco.\n"
        "> Continuação da mesma citação.\n"
        ">\n"
        "> Parágrafo adicional dentro da citação."
    ),
    "05_bloco_de_codigo_fenced": (
        "```python\n"
        "def hello_world():\n"
        "    return 'Hello, World!'\n"
        "```"
    ),
    "06_bloco_de_codigo_indentado": (
        "Texto introdutório:\n\n"
        "    codigo_indentado_1 = True\n"
        "    codigo_indentado_2 = False\n"
    ),
    "07_titulos_atx_e_setext": (
        "# Título Nível 1 ATX\n"
        "## Título Nível 2 ATX\n\n"
        "Título Setext Nível 1\n"
        "===============\n\n"
        "Título Setext Nível 2\n"
        "---------------"
    ),
    "08_html_blocks": (
        "<div>\n"
        "  <p>Conteúdo HTML inline/bloco</p>\n"
        "</div>"
    ),
    "09_links_e_imagens": (
        "[Link do Google](https://www.google.com 'Buscador')\n\n"
        "![Imagem Exemplo](https://via.placeholder.com/150)"
    ),
    "10_lazy_continuation": (
        "> Citação inicial\n"
        "linha preguiçosa sem marcador de citação continuando o parágrafo."
    ),
}


def generate_snapshots():
    outputs = {}
    parser = Parser()
    renderer = HtmlRenderer()

    for name in sorted(TEST_CASES.keys()):
        md_text = TEST_CASES[name]

        # 1. Gera a AST
        ast = parser.parse(md_text)

        # 2. Gera o HTML renderizado
        html = renderer.render(ast)

        # 3. Captura a representação textual da AST via dumpAST
        f = io.StringIO()
        with redirect_stdout(f):
            dumpAST(ast)
        ast_repr = f.getvalue()

        outputs[name] = {
            "html": html,
            "ast": ast_repr,
        }

    return outputs


def main():
    snapshots = generate_snapshots()

    for name, data in snapshots.items():
        print("=" * 60)
        print("CASO DE TESTE: {}".format(name))
        print("=" * 60)
        print("\n--- [HTML RENDERIZADO] ---")
        print(data["html"].strip())
        print("\n--- [ÁRVORE SINTÁTICA (AST)] ---")
        print(data["ast"].strip())
        print("\n")


if __name__ == "__main__":
    main()
