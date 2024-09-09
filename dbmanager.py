import sqlite3

db = sqlite3.connect('details.db')
sql = db.cursor()

sql.execute("""CREATE TABLE IF NOT EXISTS ev3 (
    name TEXT,
    id TEXT,
    alt_id TEXT,
    ml_id TEXT
)""")

db.commit()
a = '3x3'
b = '1'
c = 'a'
d = '0'
i1, i2, i3, i4 = [], [], [], []
for i in sql.execute('SELECT name FROM ev3'):
    i1.append(i[0])
for i in sql.execute('SELECT id FROM ev3'):
    i2.append(i[0])
for i in sql.execute('SELECT alt_id FROM ev3'):
    i3.append(i[0])
for i in sql.execute('SELECT ml_id FROM ev3'):
    i4.append(i[0])
if a not in i1 and b not in i2 and c not in i3 and d not in i4:
    sql.execute(f'INSERT INTO ev3 VALUES (?, ?, ?, ?)', (a, b, c, d))
    print('Success')
else:
    print('Something gone wrong')
db.commit()
