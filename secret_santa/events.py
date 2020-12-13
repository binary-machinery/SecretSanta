from dataclasses import dataclass
from datetime import datetime

from common import database


@dataclass
class Event:
    event_id: int
    creation_time: int
    name: str
    description: str
    invite_code: str


class Events:
    def __init__(self, db_filename):
        self.database = database.DatabaseWrapper(db_filename)
        self.database.execute('CREATE TABLE IF NOT EXISTS events ('
                              'id INTEGER PRIMARY KEY, '
                              'creation_time INTEGER NOT NULL, '
                              'name TEXT, '
                              'description TEXT, '
                              'invite_code TEXT)')

    def get_database_wrapper(self):
        return self.database

    def add_event(self, name, description, invite_code):
        if name == '':
            print('Events::add_event: impossible to add an event with the empty name!')
            return

        creation_time = int(datetime.now().timestamp())
        return self.database.execute_and_get_inserted_id(
            'INSERT INTO events (creation_time, name, description, invite_code) VALUES (?, ?, ?, ?)',
            (creation_time, name, description, invite_code)
        )

    def get_event_by_id(self, event_id):
        res = self.database.execute_and_fetch_one(
            'SELECT id, creation_time, name, description, invite_code FROM events WHERE id = ?',
            (event_id,)
        )
        return Event(res[0], res[1], res[2], res[3], res[4])

    def get_event_by_invite_code(self, invite_code):
        res = self.database.execute_and_fetch_one(
            'SELECT id, creation_time, name, description, invite_code FROM events WHERE invite_code = ?',
            (invite_code,)
        )
        return Event(res[0], res[1], res[2], res[3], res[4])

    def get_all_events_for_user(self, user_id):
        res = self.database.execute_and_fetch(
            'SELECT events.id, events.creation_time, events.name, events.description, events.invite_code '
            'FROM events '
            'LEFT JOIN event_users '
            '    ON event_users.event_id = events.id '
            'WHERE user_id = ? '
            'ORDER BY creation_time DESC ',
            (user_id,)
        )
        return [Event(row[0], row[1], row[2], row[3], row[4]) for row in res]

    def set_name(self, event_id, name):
        self.database.execute('UPDATE events SET name = ? WHERE id = ?',
                              (name, event_id))

    def set_description(self, event_id, description):
        self.database.execute('UPDATE events SET description = ? WHERE id = ?',
                              (description, event_id))

    def delete_event(self, event_id):
        self.database.execute('DELETE FROM events WHERE id = ?', (event_id,))
