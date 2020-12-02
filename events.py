from dataclasses import dataclass

import database


@dataclass
class Event:
    event_id: int
    name: str
    description: str
    invite_code: str


class Events:
    def __init__(self, db_filename):
        self.database = database.DatabaseWrapper(db_filename)
        self.database.execute('CREATE TABLE IF NOT EXISTS events ('
                              'id INTEGER PRIMARY KEY, '
                              'name TEXT, '
                              'description TEXT, '
                              'invite_code TEXT)')

    def get_database_wrapper(self):
        return self.database

    def add_event(self, name, description, invite_code):
        if name == '':
            print('Events::add_event: impossible to add an event with the empty name!')
            return
        return self.database.execute_and_get_inserted_id(
            'INSERT INTO events (name, description, invite_code) VALUES (?, ?, ?)',
            (name, description, invite_code)
        )

    def get_event_by_id(self, event_id):
        res = self.database.execute_and_fetch_one(
            'SELECT id, name, description, invite_code FROM events WHERE id = ?',
            (event_id,)
        )
        return Event(res[0], res[1], res[2], res[3])

    def get_event_by_invite_code(self, invite_code):
        res = self.database.execute_and_fetch_one(
            'SELECT id, name, description, invite_code FROM events WHERE invite_code = ?',
            (invite_code,)
        )
        return Event(res[0], res[1], res[2], res[3])

    def get_all_events_for_user(self, user_id):
        res = self.database.execute_and_fetch(
            'SELECT events.* '
            'FROM events '
            'LEFT JOIN event_users '
            '    ON event_users.event_id = events.id '
            'WHERE user_id = ?',
            (user_id,)
        )
        return [Event(row[0], row[1], row[2], row[3]) for row in res]

    def set_name(self, event_id, name):
        self.database.execute('UPDATE events SET name = ? WHERE id = ?',
                              (name, event_id))

    def set_description(self, event_id, description):
        self.database.execute('UPDATE events SET description = ? WHERE id = ?',
                              (description, event_id))

    def delete_event(self, event_id):
        self.database.execute('DELETE FROM events WHERE id = ?', (event_id,))


# --------------------------------------------------------------------------------


def add_event_test(db_filename, db_name, name):
    events = Events(db_filename, db_name)
    events.add_event(name)
    return events.get_event_id(name)


def update_name_test(db_filename, db_name, event_id, name):
    events = Events(db_filename, db_name)
    if events.get_name(event_id) == name:
        print('update_name_test: the name was already the one to be updated during the test: choose another one!')
        return False
    events.update_name(event_id, name)
    return events.get_name(event_id) == name


def delete_event_test(db_filename, db_name, event_id):
    events = Events(db_filename, db_name)
    if events.get_name(event_id) == '':
        print('delete_event_test: the event was already deleted before the test: choose another one!')
        return False
    events.delete_event(event_id)
    return events.get_name(event_id) == ''


def print_all_events_database(db_filename, db_name, prefix):
    events = Events(db_filename, db_name)
    database_wrapper = events.get_database_wrapper()
    database.print_all_database(database_wrapper, db_name, prefix)


def run_all_event_tests():
    db_filename = '../databases/santaDb.db'
    db_name = 'events'

    # database.delete_table(db_filename, db_name)

    print_all_events_database(db_filename, db_name, 'initial database:')

    name = 'NY2020'
    event_id = add_event_test(db_filename, db_name, name)
    if event_id == -1:
        print('error in adding an event!')
        return
    print_all_events_database(db_filename, db_name, '\ndatabase after adding the event:')

    res = update_name_test(db_filename, db_name, event_id, 'NY2020NaDache')
    if not res:
        print('error in updating a name!')
        delete_event_test(db_filename, db_name, event_id)  # the result is not important now
        return
    print_all_events_database(db_filename, db_name, '\ndatabase after updating the name:')

    res = delete_event_test(db_filename, db_name, event_id)
    if not res:
        print('error in deleting an event!')
        return
    print_all_events_database(db_filename, db_name, '\ndatabase after deleting the event:')


if __name__ == '__main__':
    run_all_event_tests()
