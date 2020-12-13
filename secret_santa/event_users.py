from dataclasses import dataclass

from common import database


@dataclass
class EventUserPublicData:
    event_id: int
    user_id: int
    user_name: str
    is_admin: bool


@dataclass
class EventUserPrivateData:
    event_id: int
    user_id: int
    user_name: str
    is_admin: bool
    wishes: str
    receiver_id: int
    receiver_name: str
    receiver_wishes: str


class EventUsers:
    def __init__(self, db_filename):
        self.database = database.DatabaseWrapper(db_filename)
        self.database.execute('CREATE TABLE IF NOT EXISTS event_users ('
                              'event_id INTEGER NOT NULL, '
                              'user_id INTEGER NOT NULL, '
                              'is_admin INTEGER NOT NULL DEFAULT 0, '
                              'wishes TEXT, '
                              'receiver_id INTEGER, '
                              'FOREIGN KEY (event_id) REFERENCES events (id), '
                              'FOREIGN KEY (user_id) REFERENCES users (id), '
                              'FOREIGN KEY (receiver_id) REFERENCES users (id), '
                              'PRIMARY KEY (event_id, user_id))')

    def get_database_wrapper(self):
        return self.database

    def add_event_user(self, event_id, user_id, is_admin=False):
        self.database.execute(
            'INSERT INTO event_users (event_id, user_id, is_admin) VALUES (?, ?, ?)',
            (event_id, user_id, is_admin)
        )

    def get_event_user(self, event_id, user_id):
        res = self.database.execute_and_fetch_one(
            'SELECT event_id, user_id, name, is_admin '
            'FROM event_users '
            'JOIN users '
            '    ON users.id = event_users.user_id '
            'WHERE (event_id, user_id) = (?, ?)',
            (event_id, user_id)
        )
        if res is None:
            return None

        return EventUserPublicData(res[0], res[1], res[2], res[3])

    def get_event_user_private_data(self, event_id, user_id):
        res = self.database.execute_and_fetch_one(
            'SELECT eu1.event_id, eu1.user_id, u1.name, eu1.is_admin, eu1.wishes, eu1.receiver_id, u2.name, eu2.wishes '
            'FROM event_users eu1 '
            'LEFT JOIN event_users eu2 '
            '    ON eu1.receiver_id = eu2.user_id '
            '         AND eu1.event_id = eu2.event_id '
            'JOIN users u1 '
            '    ON u1.id = eu1.user_id '
            'LEFT JOIN users u2 '
            '    ON u2.id = eu1.receiver_id '
            'WHERE (eu1.event_id, eu1.user_id) = (?, ?)',
            (event_id, user_id)
        )
        if res is None:
            return None

        return EventUserPrivateData(res[0], res[1], res[2], res[3], res[4], res[5], res[6], res[7])

    def get_event_users(self, event_id):
        res = self.database.execute_and_fetch(
            'SELECT event_id, user_id, name, is_admin '
            'FROM event_users '
            'JOIN users '
            '    ON users.id = event_users.user_id '
            'WHERE event_id = ?',
            (event_id,)
        )
        return [EventUserPublicData(row[0], row[1], row[2], row[3]) for row in res]

    def set_wishes(self, event_id, user_id, wishes):
        self.database.execute(
            'UPDATE event_users SET wishes = ? WHERE (event_id, user_id) = (?, ?)',
            (wishes, event_id, user_id)
        )

    def set_receiver(self, event_id, user_id, receiver_id):
        self.database.execute(
            'UPDATE event_users SET receiver_id = ? WHERE (event_id, user_id) = (?, ?)',
            (receiver_id, event_id, user_id)
        )

    def delete_event_user_pair(self, event_id, user_id):
        self.database.execute('DELETE FROM event_users WHERE (event_id, user_id) = (?, ?)', (event_id, user_id))
