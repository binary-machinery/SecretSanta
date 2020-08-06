import sqlite3


class DatabaseWrapper:
    def __init__(self, filename):
        self.connection = sqlite3.Connection(filename)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.commit()
        self.connection.close()

    def execute(self, *args, **kwargs):
        self.cursor.execute(*args, **kwargs)
        self.connection.commit()

    def execute_and_fetch(self, *args, **kwargs):
        self.cursor.execute(*args, **kwargs)
        return self.cursor.fetchall()


def print_all_database(db, db_name, text=''):
    print(text)
    for row in db.execute_and_fetch('SELECT * FROM ' + db_name):
        print(row)


def delete_table(filename, db_name):
    connection = sqlite3.Connection(filename)
    cursor = connection.cursor()
    cursor.execute('DROP TABLE IF EXISTS ' + db_name)
    connection.commit()
    connection.close()


def test_database_wrapper():
    db = DatabaseWrapper('../databases/santaDb.db')

    name = 'Katya'
    email = 'abc@dot.com'
    wish = 'I wanna cat'
    db_name = 'santaUsers'

    print_all_database(db, db_name, 'initial database:')

    db.execute('INSERT INTO ' + db_name + ' (name, email, wishes) VALUES (?, ?, ?)', (name, email, wish))

    print_all_database(db, db_name, '\ndatabase after adding a string:')

    db.execute('UPDATE ' + db_name + ' SET wishes = ? WHERE email = ?', ('I want two cats', email,))

    print_all_database(db, db_name, '\ndatabase after updating this string:')

    for id in db.execute_and_fetch('SELECT user_id FROM ' + db_name + ' WHERE email = ?', (email,)):
        db.execute('DELETE FROM ' + db_name + ' WHERE user_id = ?', (id[0],))

    print_all_database(db, db_name, '\ndatabase after deleting this string:')


if __name__ == '__main__':
    test_database_wrapper()
