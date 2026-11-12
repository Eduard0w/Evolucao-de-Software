# -*- coding: utf-8 -*-
"""Testes de InlineParser.scanDelims (card 08).

Cobrem a classificação de delimitadores de ênfase segundo a especificação
CommonMark (seção "Emphasis and strong emphasis"): left-flanking,
right-flanking e as regras específicas de ``*``, ``_`` e aspas.

Executar a partir da raiz do projeto:
    python -m unittest commonmark.tests.test_scan_delims -v
"""
import unittest

import commonmark
from commonmark.inlines import InlineParser


def scan(subject, pos):
    """Roda scanDelims no caractere da posição ``pos`` de ``subject``."""
    parser = InlineParser()
    parser.subject = subject
    parser.pos = pos
    result = parser.scanDelims(subject[pos])
    return parser, result


class TestContagem(unittest.TestCase):

    def test_conta_sequencia_de_asteriscos(self):
        _, res = scan('***foo***', 0)
        self.assertEqual(res['numdelims'], 3)

    def test_conta_sequencia_de_sublinhados(self):
        _, res = scan('__foo__', 0)
        self.assertEqual(res['numdelims'], 2)

    def test_aspas_sao_contadas_uma_por_vez(self):
        _, res = scan("''foo", 0)
        self.assertEqual(res['numdelims'], 1)

    def test_sem_delimitador_retorna_none(self):
        parser = InlineParser()
        parser.subject = 'abc'
        parser.pos = 0
        self.assertIsNone(parser.scanDelims('*'))

    def test_nao_move_a_posicao(self):
        parser, _ = scan('foo **bar**', 4)
        self.assertEqual(parser.pos, 4)


class TestAsterisco(unittest.TestCase):

    def test_inicio_de_palavra_so_abre(self):
        # antes: início do texto (conta como \n); depois: letra
        _, res = scan('*foo bar*', 0)
        self.assertTrue(res['can_open'])
        self.assertFalse(res['can_close'])

    def test_fim_de_palavra_so_fecha(self):
        _, res = scan('foo bar*', 7)
        self.assertFalse(res['can_open'])
        self.assertTrue(res['can_close'])

    def test_cercado_por_espacos_nao_atua(self):
        _, res = scan('a * b', 2)
        self.assertFalse(res['can_open'])
        self.assertFalse(res['can_close'])

    def test_dentro_da_palavra_abre_e_fecha(self):
        _, res = scan('foo*bar', 3)
        self.assertTrue(res['can_open'])
        self.assertTrue(res['can_close'])

    def test_espaco_nao_quebravel_conta_como_espaco(self):
        # U+00A0 depois do delimitador: não é left-flanking
        _, res = scan('*\xa0foo', 0)
        self.assertFalse(res['can_open'])

    def test_pontuacao_depois_exige_espaco_ou_pontuacao_antes(self):
        # 'a*"foo"': depois vem pontuação e antes vem letra -> não abre
        _, res = scan('a*"foo"', 1)
        self.assertFalse(res['can_open'])
        self.assertTrue(res['can_close'])

    def test_pontuacao_dos_dois_lados_abre_e_fecha(self):
        _, res = scan('(*)', 1)
        self.assertTrue(res['can_open'])
        self.assertTrue(res['can_close'])


class TestSublinhado(unittest.TestCase):

    def test_dentro_da_palavra_nao_atua(self):
        # Diferente de '*', '_' entre letras não abre nem fecha
        _, res = scan('foo_bar_', 3)
        self.assertFalse(res['can_open'])
        self.assertFalse(res['can_close'])

    def test_inicio_de_palavra_so_abre(self):
        _, res = scan('_foo_', 0)
        self.assertTrue(res['can_open'])
        self.assertFalse(res['can_close'])

    def test_fim_de_palavra_so_fecha(self):
        _, res = scan('_foo_', 4)
        self.assertFalse(res['can_open'])
        self.assertTrue(res['can_close'])

    def test_entre_pontuacoes_abre_e_fecha(self):
        # '_(bar)_.': o '_' final tem ')' antes e '.' depois
        _, res = scan('_(bar)_.', 6)
        self.assertTrue(res['can_open'])
        self.assertTrue(res['can_close'])


class TestAspas(unittest.TestCase):

    def test_aspa_inicial_so_abre(self):
        _, res = scan("'foo'", 0)
        self.assertTrue(res['can_open'])
        self.assertFalse(res['can_close'])

    def test_aspa_final_so_fecha(self):
        _, res = scan("'foo'", 4)
        self.assertFalse(res['can_open'])
        self.assertTrue(res['can_close'])

    def test_apostrofo_dentro_da_palavra_so_fecha(self):
        _, res = scan("don't", 3)
        self.assertFalse(res['can_open'])
        self.assertTrue(res['can_close'])


class TestHtmlFinal(unittest.TestCase):
    """O resultado de scanDelims visto pelo HTML gerado."""

    def assertHtml(self, markdown, html):
        self.assertEqual(commonmark.commonmark(markdown), html)

    def test_enfase_simples(self):
        self.assertHtml('*foo*', '<p><em>foo</em></p>\n')

    def test_enfase_forte(self):
        self.assertHtml('**foo**', '<p><strong>foo</strong></p>\n')

    def test_asterisco_dentro_da_palavra(self):
        self.assertHtml('foo*bar*', '<p>foo<em>bar</em></p>\n')

    def test_sublinhado_dentro_da_palavra_fica_literal(self):
        self.assertHtml('foo_bar_', '<p>foo_bar_</p>\n')

    def test_asterisco_cercado_por_espacos_fica_literal(self):
        self.assertHtml('a * foo bar*', '<p>a * foo bar*</p>\n')


if __name__ == '__main__':
    unittest.main()
