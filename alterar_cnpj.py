import sqlite3

conexao = sqlite3.connect("banco.db")
cursor = conexao.cursor()

try:
    cursor.execute("""
        ALTER TABLE usuarios
        ADD COLUMN cnpj TEXT UNIQUE
    """)
    print("Coluna CNPJ criada com sucesso!")

except sqlite3.OperationalError:
    print("A coluna CNPJ já existe.")

conexao.commit()
conexao.close()