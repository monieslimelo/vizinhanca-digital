import sqlite3

conexao = sqlite3.connect("banco.db")
cursor = conexao.cursor()

try:
    cursor.execute("""
        ALTER TABLE usuarios
        ADD COLUMN cpf TEXT UNIQUE
    """)
    print("Coluna CPF criada com sucesso!")

except sqlite3.OperationalError:
    print("A coluna CPF já existe.")

conexao.commit()
conexao.close()