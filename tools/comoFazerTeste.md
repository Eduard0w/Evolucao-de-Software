Como você ou qualquer colega da equipe pode usar:
Para visualizar o HTML e AST de todos os cenários de teste:
python -m tools.compare_snapshots
Para salvar e comparar com diff (Antes vs Depois):
# Salva o snapshot antes de mexer
python -m tools.compare_snapshots > snapshot_antes.txt

# (depois de refatorar o código)

# Salva o snapshot depois de mexer
python -m tools.compare_snapshots > snapshot_depois.txt

# Compara se houve qualquer alteração na AST ou HTML:
diff snapshot_antes.txt snapshot_depois.txt
Essa ferramenta vai agregar muito valor ao projeto e servirá como evidência sólida tanto para o seu Card 01 quanto para os refatores dos seus colegas!
