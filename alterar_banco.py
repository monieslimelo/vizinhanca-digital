import sqlite3

conexao = sqlite3.connect("banco.db")
cursor = conexao.cursor()

try:
    cursor.execute("""
        ALTER TABLE usuarios
        ADD COLUMN tipo TEXT DEFAULT 'cliente'
    """)

    print("Coluna tipo criada com sucesso!")

except sqlite3.OperationalError:
    print("A coluna tipo já existe.")

conexao.commit()
conexao.close()