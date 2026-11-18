
from __future__ import absolute_import, unicode_literals

from builtins import str
import json
from commonmark.node import is_container


def prepare(obj, topnode=False):
    """Walk the complete AST, only returning needed data.

    This removes circular references and allows us to output
    JSON.
    """
    a = []
    for subnode, entered in obj.walker():
        rep = {
            'type': subnode.t,
        }
        if subnode.literal:
            rep['literal'] = subnode.literal

        if subnode.string_content:
            rep['string_content'] = subnode.string_content

        if subnode.title:
            rep['title'] = subnode.title

        if subnode.info:
            rep['info'] = subnode.info

        if subnode.destination:
            rep['destination'] = subnode.destination

        if subnode.list_data:
            rep['list_data'] = subnode.list_data

        if is_container(subnode):
            rep['children'] = []

        if entered and len(a) > 0:
            if a[-1]['children']:
                a[-1]['children'].append(rep)
            else:
                a[-1]['children'] = [rep]
        else:
            a.append(rep)
    return a


def dumpJSON(obj):
    """Output AST in JSON form, this is destructive of block."""
    prepared = prepare(obj)
    return json.dumps(prepared, indent=4, sort_keys=True)


# 1. Organiza a indentação de cada nó.
def _get_indentation(ind):
    return ("\t" * ind) + "-> " if ind else ""


# 2. Imprime atributos de texto.
def _print_attribute(value, label, ind_char):
    if value != "":
        print("\t" + ind_char + label + (value or ''))


# 3. Imprime informações que possuem valor verdadeiro.
def _print_flag(value, label, ind_char):
    if value:
        print("\t" + ind_char + label + str(value))


# 4. Imprime a posição do nó no documento original.
def _print_sourcepos(obj, ind_char):
    if obj.sourcepos:
        print("\t" + ind_char + "Sourcepos: " + str(obj.sourcepos))


# 5. Imprime uma informação específica da lista.
def _print_list_value(list_data, key, ind_char, convert_to_string=False):
    value = list_data.get(key)

    if value:
        if convert_to_string:
            value = str(value)

        print("\t\t" + ind_char + "[" + key + "] = " + value)


# 6. Organiza a impressão dos dados das listas.
def _print_list_data(obj, ind_char):
    list_data = obj.list_data

    if list_data.get('type'):
        print("\t" + ind_char + "List Data: ")

        _print_list_value(list_data, 'type', ind_char)
        _print_list_value(list_data, 'bullet_char', ind_char)
        _print_list_value(list_data, 'start', ind_char, True)
        _print_list_value(list_data, 'delimiter', ind_char)
        _print_list_value(list_data, 'padding', ind_char, True)
        _print_list_value(list_data, 'marker_offset', ind_char, True)


# 7. Organiza a impressão dos atributos do nó.
def _print_node_attributes(obj, ind_char):
    _print_attribute(obj.title, 'Title: ', ind_char)
    _print_attribute(obj.info, 'Info: ', ind_char)
    _print_attribute(obj.destination, 'Destination: ', ind_char)

    _print_flag(obj.is_open, 'Open: ', ind_char)
    _print_flag(obj.last_line_blank, 'Last line blank: ', ind_char)

    _print_sourcepos(obj, ind_char)

    _print_attribute(obj.string_content, 'String content: ', ind_char)

    # Mantido duas vezes para preservar a saída original.
    _print_attribute(obj.info, 'Info: ', ind_char)

    _print_attribute(obj.literal, 'Literal: ', ind_char)


# 8. Percorre e imprime os filhos do nó.
def _print_children(obj, ind, topnode):
    if obj.walker:
        print("\t" + _get_indentation(ind) + "Children:")

        walker = obj.walker()
        nxt = walker.nxt()

        while nxt is not None and topnode is False:
            dumpAST(nxt['node'], ind + 2, topnode=True)
            nxt = walker.nxt()


# 9. Função principal.

# ============================================================
# SERIALIZADOR PADRAO
# ============================================================

def _serialize_node(obj, ind, topnode):
    """Imprime o nó atual, seus atributos, listas e filhos."""

    # Calcula a indentação do nó.
    ind_char = _get_indentation(ind)

    # Imprime o tipo do nó.
    print(ind_char + "[" + obj.t + "]")

    # Imprime os atributos gerais.
    _print_node_attributes(obj, ind_char)

    # Imprime os dados específicos de listas.
    _print_list_data(obj, ind_char)

    # Percorre os filhos, quando necessário.
    _print_children(obj, ind, topnode)


# ============================================================
# SERIALIZADORES POR TIPO DE NO
# ============================================================

def _serialize_container_node(obj, ind, topnode):
    """Trata nós estruturais que podem possuir outros nós."""
    _serialize_node(obj, ind, topnode)


def _serialize_list_node(obj, ind, topnode):
    """Trata nós relacionados a listas."""
    _serialize_node(obj, ind, topnode)


def _serialize_code_node(obj, ind, topnode):
    """Trata nós relacionados a blocos de código."""
    _serialize_node(obj, ind, topnode)


def _serialize_inline_node(obj, ind, topnode):
    """Trata elementos que aparecem dentro de uma linha."""
    _serialize_node(obj, ind, topnode)


def _serialize_leaf_node(obj, ind, topnode):
    """Trata nós de conteúdo sem filhos."""
    _serialize_node(obj, ind, topnode)


def _serialize_unknown_node(obj, ind, topnode):
    """Trata nós que não estão cadastrados na tabela."""
    _serialize_node(obj, ind, topnode)


# ============================================================
# TABELA DE DESPACHO
# ============================================================

NODE_SERIALIZERS = {

    # Nós estruturais.
    'document': _serialize_container_node,
    'block_quote': _serialize_container_node,
    'paragraph': _serialize_container_node,
    'heading': _serialize_container_node,
    'emph': _serialize_container_node,
    'strong': _serialize_container_node,
    'link': _serialize_container_node,
    'image': _serialize_container_node,
    'custom_inline': _serialize_container_node,
    'custom_block': _serialize_container_node,

    # Nós de listas.
    'list': _serialize_list_node,
    'item': _serialize_list_node,

    # Nós de código.
    'code_block': _serialize_code_node,
    'code': _serialize_inline_node,

    # Nós que aparecem dentro de linhas.
    'text': _serialize_inline_node,
    'softbreak': _serialize_inline_node,
    'linebreak': _serialize_inline_node,
    'html_inline': _serialize_inline_node,

    # Outros nós de conteúdo.
    'html_block': _serialize_leaf_node,
    'thematic_break': _serialize_leaf_node,
}


# ============================================================
# FUNÇÃO PRINCIPAL
# ============================================================

def dumpAST(obj, ind=0, topnode=False):
    """Seleciona o serializador e inicia a impressão do nó."""

    # Procura o tipo do nó na tabela.
    # Se não encontrar, utiliza o serializador padrão.
    serializer = NODE_SERIALIZERS.get(
        obj.t,
        _serialize_unknown_node
    )

    # Chama o serializador encontrado.
    serializer(obj, ind, topnode)
