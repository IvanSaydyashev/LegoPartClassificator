import sqlite3

from absl.logging import exception

db = sqlite3.connect('details.db')

sql = db.cursor()


def create_table(name):
    sql.execute(f"""CREATE TABLE IF NOT EXISTS {name} (
        part_name TEXT,
        part_id TEXT,
        part_alt_id TEXT,
        part_ml_id TEXT
    )""")
    db.commit()


def add_row(table_name, part_name, part_id, part_alt_id, part_ml_id):
    names, ids, alt_ids, ml_ids = [], [], [], []
    for i in sql.execute(f'SELECT part_name FROM {table_name}'):
        names.append(i[0])
    for i in sql.execute(f'SELECT part_id FROM {table_name}'):
        ids.append(i[0])
    for i in sql.execute(f'SELECT part_alt_id FROM {table_name}'):
        alt_ids.append(i[0])
    for i in sql.execute(f'SELECT part_ml_id FROM {table_name}'):
        ml_ids.append(i[0])
    if part_name not in names and part_id not in ids and part_alt_id not in alt_ids and part_ml_id not in ml_ids:
        sql.execute(f'INSERT INTO {table_name} VALUES (?, ?, ?, ?)', (part_name, part_id, part_alt_id, part_ml_id))
        print(f'Part {part_name} was added successfully')
    else:
        print('Something went wrong')
    db.commit()


def delete_row(table_name, part_name):
    try:
        sql.execute(f'DELETE FROM {table_name} WHERE part_name=?', (part_name,))
        print(f'Part {part_name} was deleted successfully')
    except Exception as error:
        print(f'Error - {error}')
    db.commit()


create_table('test')
# add_row('test', 'first', '1', 'A', '0')
delete_row('test', 'first')

db.close()