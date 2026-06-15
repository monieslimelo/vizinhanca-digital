import sqlite3

conexao = sqlite3.connect("banco.db")
cursor = conexao.cursor()

cursor.execute("""
UPDATE usuarios
SET tipo = 'comerciante'
WHERE email = 'monieslimelo@gmail.com'
""")

conexao.commit()
conexao.close()

print("Usuário alterado para comerciante!")