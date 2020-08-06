import sqlite3

conn = sqlite3.Connection('../databases/santaDb.db')
cur = conn.cursor()

print('before')
for row in cur.execute('SELECT * FROM santaUsers'):
    print(row)

name = 'Katya'
email = 'abc@dot.com'
wish = 'I wanna cat'
cur.execute("INSERT INTO santaUsers (name, email, wishes) VALUES (?, ?, ?)", (name, email, wish))

print('after insertion')
for row in cur.execute('SELECT * FROM santaUsers'):
    print(row)

cur.execute('SELECT userId FROM santaUsers WHERE email = ?', (email,))
id = cur.fetchone()[0]

cur.execute("DELETE FROM santaUsers WHERE userId = ?", (id,))

print('after deletion')
for row in cur.execute('SELECT * FROM santaUsers'):
    print(row)

conn.commit()
conn.close()