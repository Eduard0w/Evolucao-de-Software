# -*- coding: utf-8 -*-
"""Testes de InlineParser.processEmphasis (card 07).

Cobrem a transformação da pilha de delimitadores em nós ``emph`` e
``strong`` (``*``, ``**``, ``_``, ``__``), ênfase aninhada, delimitadores
incompatíveis, a "regra de três" e as aspas tipográficas (modo smart).

Executar a partir da raiz do projeto:
    python -m unittest commonmark.tests.test_process_emphasis -v
"""
import unittest

import commonmark
from commonmark.blocks import Parser
from commonmark.inlines import _is_odd_match
from commonmark.render.html import HtmlRenderer


def html(markdown, smart=False):
    if not smart:
        return commonmark.commonmark(markdown)
    ast = Parser(options={'smart': True}).parse(markdown)
    return HtmlRenderer().render(ast)


class TestDelimitadoresBasicos(unittest.TestCase):

    def test_asterisco(self):
        self.assertEqual(html('*foo*'), '<p><em>foo</em></p>\n')

    def test_dois_asteriscos(self):
        self.assertEqual(html('**foo**'), '<p><strong>foo</strong></p>\n')

    def test_sublinhado(self):
        self.assertEqual(html('_foo_'), '<p><em>foo</em></p>\n')

    def test_dois_sublinhados(self):
        self.assertEqual(html('__foo__'), '<p><strong>foo</strong></p>\n')

    def test_tres_asteriscos_vira_em_e_strong(self):
        self.assertEqual(html('***foo***'),
                         '<p><em><strong>foo</strong></em></p>\n')


class TestAninhamento(unittest.TestCase):

    def test_strong_dentro_de_em(self):
        self.assertEqual(html('*foo **bar** baz*'),
                         '<p><em>foo <strong>bar</strong> baz</em></p>\n')

    def test_em_dentro_de_strong(self):
        self.assertEqual(html('**foo *bar* baz**'),
                         '<p><strong>foo <em>bar</em> baz</strong></p>\n')

    def test_strong_dentro_de_strong(self):
        self.assertEqual(
            html('__foo, __bar__, baz__'),
            '<p><strong>foo, <strong>bar</strong>, baz</strong></p>\n')

    def test_asterisco_e_sublinhado_misturados(self):
        self.assertEqual(html('*foo _bar_ baz*'),
                         '<p><em>foo <em>bar</em> baz</em></p>\n')


class TestDelimitadoresIncompativeis(unittest.TestCase):

    def test_asterisco_nao_fecha_sublinhado(self):
        self.assertEqual(html('*foo_'), '<p>*foo_</p>\n')

    def test_sobra_um_asterisco_na_abertura(self):
        self.assertEqual(html('**foo*'), '<p>*<em>foo</em></p>\n')

    def test_sobra_um_asterisco_no_fechamento(self):
        self.assertEqual(html('*foo**'), '<p><em>foo</em>*</p>\n')

    def test_abertura_sem_fechamento(self):
        self.assertEqual(html('**foo bar'), '<p>**foo bar</p>\n')


class TestSemEnfase(unittest.TestCase):

    def test_sublinhado_seguido_de_espaco(self):
        self.assertEqual(html('_ foo bar_'), '<p>_ foo bar_</p>\n')

    def test_asteriscos_cercados_por_espacos(self):
        self.assertEqual(html('a * foo bar *'), '<p>a * foo bar *</p>\n')

    def test_sublinhado_dentro_de_palavra(self):
        self.assertEqual(html('snake_case_name'),
                         '<p>snake_case_name</p>\n')


class TestRegraDeTres(unittest.TestCase):

    def test_duplo_dentro_de_simples_e_enfase(self):
        self.assertEqual(html('*foo**bar**baz*'),
                         '<p><em>foo<strong>bar</strong>baz</em></p>\n')

    def test_duplo_nao_fecha_simples(self):
        self.assertEqual(html('*foo**bar*'), '<p><em>foo**bar</em></p>\n')

    def test_funcao_regra_de_tres(self):
        # '*' (1) abrindo e '**' (2) que pode abrir e fechar: 1 + 2 = 3
        opener = {'origdelims': 1, 'can_open': True, 'can_close': False}
        closer = {'origdelims': 2, 'can_open': True, 'can_close': True}
        self.assertTrue(_is_odd_match(opener, closer))

    def test_regra_de_tres_nao_se_aplica_a_multiplos_de_tres(self):
        opener = {'origdelims': 3, 'can_open': True, 'can_close': True}
        closer = {'origdelims': 3, 'can_open': True, 'can_close': True}
        self.assertFalse(_is_odd_match(opener, closer))

    def test_regra_de_tres_ignorada_se_ninguem_e_ambiguo(self):
        opener = {'origdelims': 1, 'can_open': True, 'can_close': False}
        closer = {'origdelims': 2, 'can_open': False, 'can_close': True}
        self.assertFalse(_is_odd_match(opener, closer))


class TestEstruturaDaAst(unittest.TestCase):

    def test_delimitadores_usados_somem_da_arvore(self):
        doc = Parser().parse('**foo**')
        paragraph = doc.first_child
        strong = paragraph.first_child
        self.assertEqual(strong.t, 'strong')
        self.assertIs(paragraph.last_child, strong)
        self.assertEqual(strong.first_child.literal, 'foo')

    def test_sobra_de_delimitador_vira_texto(self):
        doc = Parser().parse('**foo*')
        paragraph = doc.first_child
        self.assertEqual(paragraph.first_child.t, 'text')
        self.assertEqual(paragraph.first_child.literal, '*')
        self.assertEqual(paragraph.last_child.t, 'emph')


class TestAspasTipograficas(unittest.TestCase):

    def test_aspas_simples(self):
        self.assertEqual(html("'foo'", smart=True),
                         '<p>‘foo’</p>\n')

    def test_aspas_duplas(self):
        self.assertEqual(html('"foo"', smart=True),
                         '<p>“foo”</p>\n')

    def test_apostrofo_sem_abertura(self):
        self.assertEqual(html("don't", smart=True),
                         '<p>don’t</p>\n')


if __name__ == '__main__':
    unittest.main()
