# -*- coding: utf-8 -*-
"""Gera um "retrato" do HTML e da AST de todos os exemplos do spec.txt.

Serve para provar que uma refatoração não mudou o comportamento:
rode na versão antiga e na nova e compare os dois arquivos.

Uso (a partir da raiz do projeto):
    git switch main
    python scripts/snapshot_outputs.py antes.json
    git switch <sua-branch>
    python scripts/snapshot_outputs.py depois.json
    python scripts/snapshot_outputs.py --compare antes.json depois.json
"""
import json
import os
import re
import sys

# Garante que o pacote commonmark da pasta atual seja o importado.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import commonmark  # noqa: E402

TAB_ARROW = '→'
EXAMPLE_RE = re.compile(
    r'^`{32} example\n([\s\S]*?)^\.\n([\s\S]*?)^`{32}$', re.MULTILINE)


def load_examples(spec_path='spec.txt'):
    with open(spec_path, encoding='utf-8') as f:
        text = f.read().replace('\r\n', '\n')
    text = text.split('<!-- END TESTS -->')[0]
    return [m.group(1).replace(TAB_ARROW, '\t')
            for m in EXAMPLE_RE.finditer(text)]


def snapshot(examples):
    result = []
    for number, markdown in enumerate(examples, start=1):
        result.append({
            'example': number,
            'html': commonmark.commonmark(markdown),
            'ast': json.loads(commonmark.commonmark(markdown, format='json')),
        })
    return result


def compare(path_a, path_b):
    with open(path_a, encoding='utf-8') as f:
        a = json.load(f)
    with open(path_b, encoding='utf-8') as f:
        b = json.load(f)
    diffs = [x['example'] for x, y in zip(a, b) if x != y]
    if len(a) != len(b):
        print('Quantidade de exemplos diferente: %d vs %d' % (len(a), len(b)))
        return 1
    if diffs:
        print('%d exemplos com HTML/AST diferente: %s' % (len(diffs), diffs))
        return 1
    print('%d exemplos comparados: HTML e AST idênticos.' % len(a))
    return 0


def main(argv):
    if len(argv) == 4 and argv[1] == '--compare':
        return compare(argv[2], argv[3])
    if len(argv) != 2:
        print(__doc__)
        return 2
    data = snapshot(load_examples())
    with open(argv[1], 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print('%d exemplos salvos em %s' % (len(data), argv[1]))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
