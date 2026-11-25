# -*- coding: utf-8 -*-
"""Gera snapshots de referência (HTML e AST JSON) a partir do commonmark base.

Execute explicitamente apontando o PYTHONPATH para o worktree original (ex.: 40c7560):
    PYTHONPATH=/tmp/commonmark-40c7560 python3 scripts/generate_characterization_snapshots.py
"""
from __future__ import unicode_literals

import io
import json
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# Se PYTHONPATH apontar para um worktree (ex.: /tmp/commonmark-40c7560), prioriza-o.
# Caso contrário, usa o código local de REPO_ROOT.
if not os.environ.get('PYTHONPATH') and REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import commonmark  # noqa: E402

CASES_DIR = os.path.join(REPO_ROOT, 'tests', 'characterization', 'cases')
SNAPSHOTS_DIR = os.path.join(REPO_ROOT, 'tests', 'characterization', 'snapshots')


def generate_snapshots():
    os.makedirs(SNAPSHOTS_DIR, exist_ok=True)
    case_files = sorted(
        name for name in os.listdir(CASES_DIR) if name.endswith('.md')
    )

    for filename in case_files:
        stem = os.path.splitext(filename)[0]
        md_path = os.path.join(CASES_DIR, filename)
        with io.open(md_path, encoding='utf-8') as f:
            markdown_input = f.read()

        html_output = commonmark.commonmark(markdown_input, format='html')
        ast_data = json.loads(commonmark.commonmark(markdown_input, format='json'))
        ast_serialized = (
            json.dumps(ast_data, ensure_ascii=False, indent=2, sort_keys=True)
            + '\n'
        )

        with io.open(
            os.path.join(SNAPSHOTS_DIR, stem + '.html'),
            'w',
            encoding='utf-8',
        ) as f:
            f.write(html_output)

        with io.open(
            os.path.join(SNAPSHOTS_DIR, stem + '.ast.json'),
            'w',
            encoding='utf-8',
        ) as f:
            f.write(ast_serialized)

    print('Gerados %d pares de snapshots (HTML + AST).' % len(case_files))


if __name__ == '__main__':
    generate_snapshots()