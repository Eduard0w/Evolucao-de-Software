# -*- coding: utf-8 -*-
"""Testes de caracterização de HTML e AST para o CommonMark."""
from __future__ import unicode_literals

import io
import json
import os
import pytest

import commonmark

BASE_DIR = os.path.dirname(__file__)
CASES_DIR = os.path.join(BASE_DIR, 'cases')
SNAPSHOTS_DIR = os.path.join(BASE_DIR, 'snapshots')


def _load_case_ids():
    if not os.path.isdir(CASES_DIR):
        return []
    return sorted(
        os.path.splitext(name)[0]
        for name in os.listdir(CASES_DIR)
        if name.endswith('.md')
    )


CASE_IDS = _load_case_ids()


@pytest.mark.parametrize('case_id', CASE_IDS)
def test_characterization_html_and_ast(case_id):
    md_path = os.path.join(CASES_DIR, case_id + '.md')
    html_path = os.path.join(SNAPSHOTS_DIR, case_id + '.html')
    ast_path = os.path.join(SNAPSHOTS_DIR, case_id + '.ast.json')

    with io.open(md_path, encoding='utf-8') as f:
        markdown_input = f.read()

    with io.open(html_path, encoding='utf-8') as f:
        expected_html = f.read()

    with io.open(ast_path, encoding='utf-8') as f:
        expected_ast = json.load(f)

    actual_html = commonmark.commonmark(markdown_input, format='html')
    actual_ast = json.loads(commonmark.commonmark(markdown_input, format='json'))

    assert actual_html == expected_html
    assert actual_ast == expected_ast