import sqlite3

conexao = sqlite3.connect("banco.db")
cursor = conexao.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT,
    pontos INTEGER NOT NULL,
    imagem TEXT
)
""")

cursor.execute("""
INSERT INTO produtos (nome, descricao, pontos, imagem)
SELECT 'Arroz Tipo 1', 'Pacote 1kg', 500, 'arroz.png'
WHERE NOT EXISTS (SELECT 1 FROM produtos WHERE nome = 'Arroz Tipo 1')
""")

cursor.execute("""
INSERT INTO produtos (nome, descricao, pontos, imagem)
SELECT 'Feijão Preto', 'Pacote 1kg', 400, 'feijao.png'
WHERE NOT EXISTS (SELECT 1 FROM produtos WHERE nome = 'Feijão Preto')
""")

cursor.execute("""
INSERT INTO produtos (nome, descricao, pontos, imagem)
SELECT 'Óleo de Soja', '900ml', 300, 'oleo.png'
WHERE NOT EXISTS (SELECT 1 FROM produtos WHERE nome = 'Óleo de Soja')
""")

conexao.commit()
conexao.close()

print("Produtos criados com sucesso!")