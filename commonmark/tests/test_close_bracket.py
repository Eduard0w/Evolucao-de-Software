# -*- coding: utf-8 -*-
"""Testes de InlineParser.parseCloseBracket (card 09).

Cobrem links inline (com e sem título), links por referência (completa,
recolhida e atalho), referências ausentes, imagens, colchetes soltos,
sequências inválidas e a regra "sem links dentro de links".

Executar a partir da raiz do projeto:
    python -m unittest commonmark.tests.test_close_bracket -v
"""
import unittest

import commonmark
from commonmark.blocks import Parser


def html(markdown):
    return commonmark.commonmark(markdown)


class TestLinkInline(unittest.TestCase):

    def test_com_titulo(self):
        self.assertEqual(html('[link](/uri "title")'),
                         '<p><a href="/uri" title="title">link</a></p>\n')

    def test_sem_titulo(self):
        self.assertEqual(html('[link](/uri)'),
                         '<p><a href="/uri">link</a></p>\n')

    def test_destino_vazio(self):
        self.assertEqual(html('[link]()'), '<p><a href="">link</a></p>\n')

    def test_destino_entre_sinais_de_menor_e_maior(self):
        self.assertEqual(html('[link](</my uri>)'),
                         '<p><a href="/my%20uri">link</a></p>\n')

    def test_enfase_dentro_do_texto_do_link(self):
        self.assertEqual(html('[*foo*](/uri)'),
                         '<p><a href="/uri"><em>foo</em></a></p>\n')


class TestLinkPorReferencia(unittest.TestCase):

    def test_referencia_completa(self):
        self.assertEqual(
            html('[foo][bar]\n\n[bar]: /url "title"'),
            '<p><a href="/url" title="title">foo</a></p>\n')

    def test_referencia_recolhida(self):
        self.assertEqual(html('[foo][]\n\n[foo]: /url'),
                         '<p><a href="/url">foo</a></p>\n')

    def test_referencia_atalho(self):
        self.assertEqual(html('[foo]\n\n[foo]: /url'),
                         '<p><a href="/url">foo</a></p>\n')

    def test_rotulo_nao_diferencia_maiusculas(self):
        self.assertEqual(html('[FOO]\n\n[foo]: /url'),
                         '<p><a href="/url">FOO</a></p>\n')

    def test_referencia_completa_ausente(self):
        self.assertEqual(html('[foo][bar]'), '<p>[foo][bar]</p>\n')

    def test_referencia_atalho_ausente(self):
        self.assertEqual(html('[foo]'), '<p>[foo]</p>\n')


class TestImagens(unittest.TestCase):

    def test_imagem_inline(self):
        self.assertEqual(
            html('![foo](/url "title")'),
            '<p><img src="/url" alt="foo" title="title" /></p>\n')

    def test_imagem_por_referencia(self):
        self.assertEqual(html('![foo]\n\n[foo]: /url'),
                         '<p><img src="/url" alt="foo" /></p>\n')

    def test_imagem_dentro_de_link(self):
        self.assertEqual(
            html('[![moon](moon.jpg)](/uri)'),
            '<p><a href="/uri"><img src="moon.jpg" alt="moon" /></a></p>\n')


class TestColchetesSoltosEInvalidos(unittest.TestCase):

    def test_fecha_colchete_sem_abertura(self):
        self.assertEqual(html(']'), '<p>]</p>\n')

    def test_abre_colchete_sem_fechamento(self):
        self.assertEqual(html('['), '<p>[</p>\n')

    def test_colchete_no_meio_da_palavra(self):
        self.assertEqual(html('foo]bar'), '<p>foo]bar</p>\n')

    def test_destino_com_espaco_nao_e_link(self):
        self.assertEqual(html('[link](/my uri)'),
                         '<p>[link](/my uri)</p>\n')

    def test_parentese_sem_fechamento_nao_e_link(self):
        self.assertEqual(html('[link](/uri'), '<p>[link](/uri</p>\n')


class TestPilhas(unittest.TestCase):

    def test_link_dentro_de_link_nao_e_permitido(self):
        self.assertEqual(
            html('[foo [bar](/uri)](/uri)'),
            '<p>[foo <a href="/uri">bar</a>](/uri)</p>\n')

    def test_enfase_aberta_antes_do_colchete_nao_entra_no_link(self):
        self.assertEqual(html('*[foo*](/uri)'),
                         '<p>*<a href="/uri">foo*</a></p>\n')


class TestEstruturaDaAst(unittest.TestCase):

    def test_atributos_do_no_link(self):
        doc = Parser().parse('[foo](/url "bar")')
        link = doc.first_child.first_child
        self.assertEqual(link.t, 'link')
        self.assertEqual(link.destination, '/url')
        self.assertEqual(link.title, 'bar')
        self.assertEqual(link.first_child.literal, 'foo')

    def test_colchete_de_abertura_sai_da_arvore(self):
        doc = Parser().parse('[foo](/url)')
        paragraph = doc.first_child
        self.assertIs(paragraph.first_child, paragraph.last_child)


if __name__ == '__main__':
    unittest.main()
