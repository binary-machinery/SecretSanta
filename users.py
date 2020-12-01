from dataclasses import dataclass

from flask_login import UserMixin

import database


@dataclass
class User(UserMixin):
    user_id: int
    email: str
    name: str

    def get_id(self):
        return self.user_id


class Users:
    def __init__(self, db_filename):
        self.database = database.DatabaseWrapper(db_filename)
        self.database.execute('CREATE TABLE IF NOT EXISTS users ('
                              'id INTEGER PRIMARY KEY, '
                              'email TEXT UNIQUE, '
                              'name TEXT, '
                              'password_hash TEXT)')

    def get_database_wrapper(self):
        return self.database

    def add_user(self, email, name, password_hash):
        if not email or not password_hash:
            print('Users::add_user: impossible to add a user with the empty parameter!')
            return

        return self.database.execute_and_get_inserted_id(
            'INSERT INTO users (email, name, password_hash) VALUES (?, ?, ?)',
            (email, name, password_hash)
        )

    def set_name(self, user_id, name):
        self.database.execute('UPDATE users SET name = ? WHERE id = ?', (name, user_id))

    def get_user_by_id(self, user_id):
        res = self.database.execute_and_fetch_one(
            'SELECT id, email, name FROM users WHERE id = ?',
            (user_id,)
        )
        return User(res[0], res[1], res[2])

    def get_user_by_email(self, email):
        res = self.database.execute_and_fetch_one(
            'SELECT id, email, name FROM users WHERE email = ?',
            (email,)
        )
        return User(res[0], res[1], res[2])

    def get_password_hash_by_email(self, email):
        res = self.database.execute_and_fetch_one(
            'SELECT password_hash FROM users WHERE email = ?',
            (email,)
        )
        return res[0]

    def delete_user(self, user_id):
        self.database.execute('DELETE FROM users WHERE id = ?', (user_id,))
