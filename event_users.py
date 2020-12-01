from dataclasses import dataclass

import database
import events
import users


@dataclass
class EventUser:
    event_id: int
    user_id: int
    is_admin: bool
    receiver_id: int


class EventUsers:
    def __init__(self, db_filename):
        self.database = database.DatabaseWrapper(db_filename)
        self.database.execute('CREATE TABLE IF NOT EXISTS event_users ('
                              'event_id INTEGER NOT NULL, '
                              'user_id INTEGER NOT NULL, '
                              'is_admin INTEGER NOT NULL DEFAULT 0, '
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
            'SELECT event_id, user_id, is_admin, receiver_id FROM event_users WHERE (event_id, user_id) = (?, ?)',
            (event_id, user_id)
        )
        return EventUser(res[0], res[1], res[2], res[3])

    def set_receiver(self, event_id, user_id, receiver_id):
        self.database.execute(
            'UPDATE event_users SET receiver_id = ? WHERE (event_id, user_id) = (?, ?)',
            (receiver_id, event_id, user_id)
        )

    def get_all_users_per_event(self, event_id):
        res = self.database.execute_and_fetch('SELECT user_id FROM event_users WHERE event_id = ?',
                                              (event_id,))
        return [i[0] for i in res]

    def get_all_events_per_user(self, user_id):
        res = self.database.execute_and_fetch('SELECT event_id FROM event_users WHERE user_id = ?',
                                              (user_id,))
        return [i[0] for i in res]

    def delete_event_user_pair(self, event_id, user_id):
        self.database.execute('DELETE FROM event_users WHERE (event_id, user_id) = (?, ?)', (event_id, user_id))


# --------------------------------------------------------------------------------


def add_event_user_pair_test(db_filename, events_table, users_table, events_users_db_name, event_id, user_id,
                             is_admin=False):
    if events_table.get_name(event_id) == '':
        print('add_event_user_pair_test: event ID is not a member of Events table!')
        return False
    if users_table.get_user(user_id)['login'] == '':
        print('add_event_user_pair_test: user ID is not a member of Users table!')
        return False

    events_users_table = EventUsers(db_filename, events_table, users_table, events_users_db_name)
    if user_id in events_users_table.get_all_users_per_event(event_id):
        print('add_event_user_pair_test: such event-user pair already exists in the table, choose another one!')
        return False

    events_users_table.add_event_user_pair(event_id, user_id, is_admin)

    is_ok = True
    if not (user_id in events_users_table.get_all_users_per_event(event_id)):
        is_ok = False
        print('add_event_user_pair_test: user ID is retrieved incorrectly!')
    if not (event_id in events_users_table.get_all_events_per_user(user_id)):
        is_ok = False
        print('add_event_user_pair_test: event ID is retrieved incorrectly!')
    return is_ok


def update_user_admin_rights_test(db_filename, events_table, users_table, events_users_db_name, event_id, user_id):
    if events_table.get_name(event_id) == '':
        print('add_event_user_pair_test: event ID is not a member of Events table!')
        return False
    if users_table.get_user(user_id)['login'] == '':
        print('add_event_user_pair_test: user ID is not a member of Users table!')
        return False

    events_users_table = EventUsers(db_filename, events_table, users_table, events_users_db_name)
    if not (user_id in events_users_table.get_all_users_per_event(event_id)):
        print('update_user_admin_rights_test: such event-user pair does not exist in the table!')
        return False
    old_admin_rights = events_users_table.get_user_admin_rights(event_id, user_id)
    if old_admin_rights == -1:
        print('update_user_admin_rights_test: an error occurred while executing get_user_admin_rights!')
        return False
    new_admin_rights = not old_admin_rights
    events_users_table.update_user_admin_rights(event_id, user_id, new_admin_rights)
    return events_users_table.get_user_admin_rights(event_id, user_id) == new_admin_rights


def assign_receiver_test(db_filename, events_table, users_table, events_users_db_name, event_id, user_id,
                         receiver_user_id):
    if events_table.get_name(event_id) == '':
        print('add_event_user_pair_test: event ID is not a member of Events table!')
        return False
    if users_table.get_user(user_id)['login'] == '':
        print('add_event_user_pair_test: user ID is not a member of Users table!')
        return False
    if users_table.get_user(receiver_user_id)['login'] == '':
        print('assign_receiver_test: receiver user ID is not a member of Users table!')
        return False

    events_users_table = EventUsers(db_filename, events_table, users_table, events_users_db_name)
    if not (user_id in events_users_table.get_all_users_per_event(event_id)):
        print('assign_receiver_test: such event-user pair does not exist in the table!')
        return False
    if events_users_table.get_receiver(event_id, user_id) == receiver_user_id:
        print('assign_receiver_test: the receiver is already the chosen one, choose another one!')
        return False

    events_users_table.assign_receiver(event_id, user_id, receiver_user_id)
    return events_users_table.get_receiver(event_id, user_id) == receiver_user_id


def delete_event_user_pair_test(db_filename, events_table, users_table, events_users_db_name, event_id, user_id):
    if events_table.get_name(event_id) == '':
        print('add_event_user_pair_test: event ID is not a member of Events table!')
        return False
    if users_table.get_user(user_id)['login'] == '':
        print('add_event_user_pair_test: user ID is not a member of Users table!')
        return False

    events_users_table = EventUsers(db_filename, events_table, users_table, events_users_db_name)
    if not (user_id in events_users_table.get_all_users_per_event(event_id)):
        print('delete_event_user_pair_test: such event-user pair does not exist in the table!')
        return False

    events_users_table.delete_event_user_pair(event_id, user_id)

    is_ok = True
    if user_id in events_users_table.get_all_users_per_event(event_id):
        is_ok = False
        print('delete_event_user_pair_test: user ID is not deleted for this event ID!')
    if event_id in events_users_table.get_all_events_per_user(user_id):
        is_ok = False
        print('delete_event_user_pair_test: event ID is not deleted for this user ID!')
    return is_ok


def print_all_event_users_database(db_filename, events_table, users_table, events_users_db_name, prefix):
    events_users_table = EventUsers(db_filename, events_table, users_table, events_users_db_name)
    database_wrapper = events_users_table.get_database_wrapper()
    database.print_all_database(database_wrapper, events_users_db_name, prefix)


def run_all_event_users_tests():
    db_filename = '../databases/santaDb.db'
    db_name_events = 'events'
    db_name_users = 'santaUsers'
    db_name_event_users = 'eventUsers'

    # database.delete_table(db_filename, db_name_users)
    # database.delete_table(db_filename, db_name_events)
    # database.delete_table(db_filename, db_name_event_users)

    user_name = 'Katya'
    login = 'kitekat'
    psw_hash = 123
    email = 'abc@dot.com'

    user_name_receiver = 'Jenya'
    login_receiver = 'fckrsns'
    psw_hash_receiver = 456
    email_receiver = 'def@dot.com'

    event_name = 'NY2020'

    user_id = users.add_user_test(db_filename, db_name_users, user_name, login, psw_hash, email)
    user_id_receiver = users.add_user_test(db_filename, db_name_users, user_name_receiver, login_receiver,
                                           psw_hash_receiver, email_receiver)

    event_id = events.add_event_test(db_filename, db_name_events, event_name)

    users.print_all_users_database(db_filename, db_name_users, '\nusers database:')
    events.print_all_events_database(db_filename, db_name_events, '\nevents database:')

    users_table = users.Users(db_filename, db_name_users)
    events_table = events.Events(db_filename, db_name_events)

    result = add_event_user_pair_test(db_filename, events_table, users_table, db_name_event_users, event_id, user_id)
    if not result:
        print('error in adding first event-user pair!')
        delete_event_user_pair_test(db_filename, events_table, users_table, db_name_event_users, event_id,
                                    user_id)  # the result is not important now
        users.delete_user_test(db_filename, db_name_users, user_id)
        users.delete_user_test(db_filename, db_name_users, user_id_receiver)
        events.delete_event_test(db_filename, db_name_events, event_id)
        return
    print_all_event_users_database(db_filename, events_table, users_table, db_name_event_users,
                                   '\ndatabase after adding first event-user pair:')

    result = add_event_user_pair_test(db_filename, events_table, users_table, db_name_event_users, event_id,
                                      user_id_receiver)
    if not result:
        print('error in adding second event-user pair!')
        delete_event_user_pair_test(db_filename, events_table, users_table, db_name_event_users, event_id,
                                    user_id)  # the result is not important now
        delete_event_user_pair_test(db_filename, events_table, users_table, db_name_event_users, event_id,
                                    user_id_receiver)  # the result is not important now
        users.delete_user_test(db_filename, db_name_users, user_id)
        users.delete_user_test(db_filename, db_name_users, user_id_receiver)
        events.delete_event_test(db_filename, db_name_events, event_id)
        return
    print_all_event_users_database(db_filename, events_table, users_table, db_name_event_users,
                                   '\ndatabase after adding second event-user pair:')

    result = update_user_admin_rights_test(db_filename, events_table, users_table, db_name_event_users, event_id,
                                           user_id)
    if not result:
        print('error in updating admin rights!')
        delete_event_user_pair_test(db_filename, events_table, users_table, db_name_event_users, event_id,
                                    user_id)  # the result is not important now
        delete_event_user_pair_test(db_filename, events_table, users_table, db_name_event_users, event_id,
                                    user_id_receiver)  # the result is not important now
        users.delete_user_test(db_filename, db_name_users, user_id)
        users.delete_user_test(db_filename, db_name_users, user_id_receiver)
        events.delete_event_test(db_filename, db_name_events, event_id)
        return
    print_all_event_users_database(db_filename, events_table, users_table, db_name_event_users,
                                   '\ndatabase after updating admin rights:')

    result = assign_receiver_test(db_filename, events_table, users_table, db_name_event_users, event_id, user_id,
                                  user_id_receiver)
    if not result:
        print('error in assigning receiver!')
        delete_event_user_pair_test(db_filename, events_table, users_table, db_name_event_users, event_id,
                                    user_id)  # the result is not important now
        delete_event_user_pair_test(db_filename, events_table, users_table, db_name_event_users, event_id,
                                    user_id_receiver)  # the result is not important now
        users.delete_user_test(db_filename, db_name_users, user_id)
        users.delete_user_test(db_filename, db_name_users, user_id_receiver)
        events.delete_event_test(db_filename, db_name_events, event_id)
        return
    print_all_event_users_database(db_filename, events_table, users_table, db_name_event_users,
                                   '\ndatabase after assigning receiver:')

    result = delete_event_user_pair_test(db_filename, events_table, users_table, db_name_event_users, event_id, user_id)
    if not result:
        print('error in deleting first event-user pair!')
        delete_event_user_pair_test(db_filename, events_table, users_table, db_name_event_users, event_id,
                                    user_id)  # the result is not important now
        delete_event_user_pair_test(db_filename, events_table, users_table, db_name_event_users, event_id,
                                    user_id_receiver)  # the result is not important now
        users.delete_user_test(db_filename, db_name_users, user_id)
        users.delete_user_test(db_filename, db_name_users, user_id_receiver)
        events.delete_event_test(db_filename, db_name_events, event_id)
        return
    print_all_event_users_database(db_filename, events_table, users_table, db_name_event_users,
                                   '\ndatabase after deleting first event-user pair:')

    result = delete_event_user_pair_test(db_filename, events_table, users_table, db_name_event_users, event_id,
                                         user_id_receiver)
    if not result:
        print('error in deleting second event-user pair!')
        delete_event_user_pair_test(db_filename, events_table, users_table, db_name_event_users, event_id,
                                    user_id)  # the result is not important now
        delete_event_user_pair_test(db_filename, events_table, users_table, db_name_event_users, event_id,
                                    user_id_receiver)  # the result is not important now
        users.delete_user_test(db_filename, db_name_users, user_id)
        users.delete_user_test(db_filename, db_name_users, user_id_receiver)
        events.delete_event_test(db_filename, db_name_events, event_id)
        return
    print_all_event_users_database(db_filename, events_table, users_table, db_name_event_users,
                                   '\ndatabase after deleting second event-user pair:')

    users.delete_user_test(db_filename, db_name_users, user_id)
    users.delete_user_test(db_filename, db_name_users, user_id_receiver)
    events.delete_event_test(db_filename, db_name_events, event_id)


if __name__ == '__main__':
    run_all_event_users_tests()
