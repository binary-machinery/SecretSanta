from dataclasses import dataclass

from common import database


@dataclass
class EventUserConstraint:
    event_id: int
    user_id: int
    constraint_user_id: int


class EventUserConstraints:
    def __init__(self, db_filename):
        self.database = database.DatabaseWrapper(db_filename)
        self.database.execute('CREATE TABLE IF NOT EXISTS event_user_constraints ('
                              'event_id INTEGER NOT NULL, '
                              'user_id INTEGER NOT NULL, '
                              'constraint_user_id INTEGER NOT NULL, '
                              'FOREIGN KEY (event_id) REFERENCES events (id), '
                              'FOREIGN KEY (user_id) REFERENCES users (id), '
                              'FOREIGN KEY (constraint_user_id) REFERENCES users (id), '
                              'PRIMARY KEY (event_id, user_id, constraint_user_id))')

    def get_database_wrapper(self):
        return self.database

    def add_constraint(self, event_id, user_id, constraint_user_id):
        self.database.execute('INSERT INTO event_user_constraints (event_id, user_id, constraint_user_id) '
                              'VALUES (?, ?, ?)',
                              (event_id, user_id, constraint_user_id))

    def delete_constraint(self, event_id, user_id, constraint_user_id):
        self.database.execute('DELETE FROM event_user_constraints '
                              'WHERE (event_id, user_id, constraint_user_id) = (?, ?, ?)',
                              (event_id, user_id, constraint_user_id))

    def get_user_constraints_for_event(self, event_id):
        res = self.database.execute_and_fetch(
            'SELECT event_id, user_id, constraint_user_id '
            'FROM event_user_constraints '
            'WHERE event_id = ?',
            (event_id,))
        return [EventUserConstraint(row[0], row[1], row[2]) for row in res]
