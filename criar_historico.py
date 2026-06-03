import sqlite3

conexao = sqlite3.connect("banco.db")
cursor = conexao.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS historico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    produto TEXT NOT NULL,
    pontos_usados INTEGER NOT NULL,
    data TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

conexao.commit()
conexao.close()

print("Tabela de histórico criada com sucesso!")