import sqlite3


class DatabaseWrapper:
    def __init__(self, filename):
        self.filename = filename
        self.connection = sqlite3.Connection(filename)
        self.cursor = self.connection.cursor()

    def execute(self, *args, **kwargs):
        with sqlite3.Connection(self.filename) as connection:
            cursor = connection.cursor()
            cursor.execute(*args, **kwargs)
            connection.commit()

    def execute_and_fetch(self, *args, **kwargs):
        with sqlite3.Connection(self.filename) as connection:
            cursor = connection.cursor()
            cursor.execute(*args, **kwargs)
            return cursor.fetchall()

    def execute_and_fetch_one(self, *args, **kwargs):
        with sqlite3.Connection(self.filename) as connection:
            cursor = connection.cursor()
            cursor.execute(*args, **kwargs)
            return cursor.fetchone()

    def execute_and_get_inserted_id(self, *args, **kwargs):
        with sqlite3.Connection(self.filename) as connection:
            cursor = connection.cursor()
            cursor.execute(*args, **kwargs)
            connection.commit()
            return cursor.lastrowid
