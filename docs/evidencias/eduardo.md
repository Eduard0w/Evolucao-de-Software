# Evidências de Refatoração — Eduardo
**Frente 1:** Processamento e Modularização de Blocos Markdown  
**Card 01:** Refatorar `Parser.incorporate_line` (`commonmark/blocks.py`)

---

## 1. Contexto e Motivação
O método `Parser.incorporate_line` é o núcleo de ingestão e processamento de linhas do CommonMark. Anteriormente, ele acumulava múltiplas responsabilidades em um único bloco de código monolítico com mais de 140 linhas e **Complexidade Ciclomática (CC) 36**:
1. Sanitização de caracteres NUL de segurança.
2. Navegação na árvore sintática e validação de continuação de blocos abertos.
3. Despacho e identificação de abertura de novos blocos (`block_starts`).
4. Tratamento de parágrafos preguiçosos (*lazy paragraph continuation*).
5. Propagação de linhas em branco e fechamento de blocos desconectados.
6. Adição de texto a blocos existentes ou instanciação de nós de parágrafo.

O objetivo desta refatoração foi aplicar a técnica de **Extração de Métodos**, separando as responsabilidades em funções coesas e reduzindo a complexidade ciclomática, preservando 100% o comportamento original do parser.

---

## 2. Responsabilidades Extraídas

Foram extraídos métodos privados/auxiliares para lidar com fases bem delimitadas do ciclo de vida da linha:

1. **`sanitize_line(self, ln)`**:
   - *Responsabilidade:* Higienização de caracteres NUL (`\u0000` substituído por `\uFFFD`) para evitar vulnerabilidades de injeção.
2. **`continue_open_blocks(self, container, all_matched, ln)`**:
   - *Responsabilidade:* Iteração sobre os nós filhos abertos da AST e verificação de continuação através dos métodos `continue_()` de cada tipo de bloco. Retorna `(container, all_matched, should_return)`.
3. **`find_block_start(self, matched_leaf, container, ln)`**:
   - *Responsabilidade:* Otimização de busca e iteração sobre os métodos de início de bloco (`self.block_starts.METHODS`), identificando e abrindo novos containers ou nós folhas.
4. **`add_new_line(self, container, container_name, ln)`**:
   - *Responsabilidade:* Adição do texto ao bloco receptor adequado, verificação do critério de encerramento de blocos HTML (tipos 1 a 5) ou criação de um novo parágrafo.

---

## 3. Código: Antes vs. Depois

### Antes (`incorporate_line` monolítico)
```python
    def incorporate_line(self, ln):
        all_matched = True

        container = self.doc
        self.oldtip = self.tip
        self.offset = 0
        self.column = 0
        self.blank = False
        self.partially_consumed_tab = False
        self.line_number += 1

        # replace NUL characters for security
        if re.search(r'\u0000', ln) is not None:
            ln = re.sub(r'\0', '\uFFFD', ln)

        self.current_line = ln

        # Loop de continuação de blocos embutido
        while True:
            last_child = container.last_child
            if not (last_child and last_child.is_open):
                break
            container = last_child
            self.find_next_nonspace()
            rv = self.blocks[container.t].continue_(self, container)
            # ... múltiplas ramificações if/elif/else com CC alta ...

        # Loop de abertura de novos blocos embutido
        while not matched_leaf:
            # ... despacho e verificações de caracteres especiais ...

        # Lógica de inserção de texto e nós de parágrafo embutida
        if not self.all_closed and not self.blank and self.tip.t == 'paragraph':
            self.add_line()
        else:
            # ... dezenas de linhas de propagação e criação de parágrafos ...
```

### Depois (Modularizado e Coeso)
```python
    def incorporate_line(self, ln):
        """Analyze a line of text and update the document appropriately."""
        all_matched = True
        container = self.doc
        self.oldtip = self.tip
        self.offset = 0
        self.column = 0
        self.blank = False
        self.partially_consumed_tab = False
        self.line_number += 1

        # 1. Sanitização
        ln = self.sanitize_line(ln)
        self.current_line = ln

        # 2. Continuação de blocos abertos
        container, all_matched, should_return = (
            self.continue_open_blocks(container, all_matched, ln)
        )
        if should_return:
            return

        self.all_closed = (container == self.oldtip)
        self.last_matched_container = container

        matched_leaf = container.t != 'paragraph' and \
            self.blocks[container.t].accepts_lines

        # 3. Identificação e início de novos blocos
        container, matched_leaf = self.find_block_start(matched_leaf, container, ln)

        # 4. Adição de conteúdo / Lazy continuation
        if not self.all_closed and not self.blank and \
           self.tip.t == 'paragraph':
            self.add_line()
        else:
            self.close_unmatched_blocks()
            if self.blank and container.last_child:
                container.last_child.last_line_blank = True

            t = container.t
            last_line_blank = self.blank and \
                not (t == 'block_quote' or
                     (t == 'code_block' and container.is_fenced) or
                     (t == 'item' and
                      not container.first_child and
                      container.sourcepos[0][0] == self.line_number))

            cont = container
            while cont:
                cont.last_line_blank = last_line_blank
                cont = cont.parent

            container = self.add_new_line(container, t, ln)

        self.last_line_length = len(ln)
```

---

## 4. Métricas de Complexidade Ciclomática (CC)

A medição de complexidade ciclomática da AST demonstrou uma redução drástica:

| Método / Função | Complexidade Anterior | Complexidade Atual | Status |
| :--- | :---: | :---: | :---: |
| **`incorporate_line`** | **36** (Crítica) | **12** | **Redução de 66.7%** |
| `sanitize_line` | — *(embutido)* | **2** | Baixa / Ideal |
| `continue_open_blocks` | — *(embutido)* | **8** | Baixa (<= 10) |
| `find_block_start` | — *(embutido)* | **8** | Baixa (<= 10) |
| `add_new_line` | — *(embutido)* | **6** | Baixa (<= 10) |

---

## 5. Bateria de Testes e Validação de Regressão

### 5.1. Suíte Oficial de Especificação (`run_spec_tests.py`)
- Execução da suíte completa de conformidade com a especificação CommonMark (parágrafos, listas, citações, blocos de código, HTML blocks, títulos, etc.):
  - **Total:** 649 testes
  - **Passaram:** 649 testes
  - **Falhas:** 0 falhas

### 5.2. Testes Unitários e Casos de Borda (`unit_tests.py`)
Foram incorporados testes adicionais com `unittest.mock` para assegurar cobertura dos novos métodos isolados:
1. `test_sanitize_line_nul_character`:
   - Valida a substituição de byte `\u0000` por `\uFFFD`.
2. `test_continue_open_block_invalid_return_value`:
   - Simula um retorno inválido via mock no método `continue_`, garantindo o lançamento defensivo de `ValueError`.
- **Resultado:** 15 de 15 testes unitários executados com sucesso (OK).

---

## 6. Comparativo de Saídas (HTML e AST)
A geração de saídas antes e após a refatoração foi conferida contra os casos de teste de referência do CommonMark:
- **HTML:** Nenhuma alteração nas tags ou strings renderizadas.
- **AST (Árvore Sintática):** Nenhuma alteração na tipagem de nós, atributos ou posições na árvore.
- **Divergências detectadas:** 0.
