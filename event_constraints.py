import events
import users
import event_users
import database


class EventUserConstraints:
    def __init__(self, db_filename, events_table, users_table, db_name):
        self.database = database.DatabaseWrapper(db_filename)
        self.db_name = db_name
        self.database.execute('CREATE TABLE IF NOT EXISTS ' + db_name + ' ('
            'event_id INTEGER NOT NULL, '
            'user_id INTEGER NOT NULL, '
            'constraint_user_id INTEGER NOT NULL, '
            'FOREIGN KEY (event_id) REFERENCES ' + events_table.get_database_name() + '(event_id), '
            'FOREIGN KEY (user_id) REFERENCES ' + users_table.get_database_name() + '(user_id), '
            'FOREIGN KEY (constraint_user_id) REFERENCES ' + users_table.get_database_name() + '(user_id), '
            'PRIMARY KEY (event_id, user_id, constraint_user_id))')

    def get_database_wrapper(self):
        return self.database

    def get_database_name(self):
        return self.db_name

    def add_constraint(self, event_id, user_id, constraint_user_id):
        self.database.execute('INSERT INTO ' + self.db_name +
                              ' (event_id, user_id, constraint_user_id) VALUES (?, ?, ?)',
                              (event_id, user_id, constraint_user_id))

    def delete_constraint(self, event_id, user_id, constraint_user_id):
        self.database.execute('DELETE FROM ' + self.db_name +
                              ' WHERE (event_id, user_id, constraint_user_id) = (?, ?, ?)',
                              (event_id, user_id, constraint_user_id))

    def get_all_rejected_users_per_event_user_pair(self, event_id, user_id):
        return self.database.execute_and_fetch('SELECT constraint_user_id FROM ' + self.db_name +
                                        ' WHERE (event_id, user_id) = (?, ?)', (event_id, user_id))[0]

    def constraint_exists(self, event_id, user_id, constraint_user_id):
        res = self.database.execute_and_fetch('SELECT event_id FROM ' + self.db_name +
                                              ' WHERE (event_id, user_id, constraint_user_id) = (?, ?, ?)',
                                              (event_id, user_id, constraint_user_id))
        return ((not res) == False)


def test_event_user_constraints():
    import numpy as np

    db_filename = '../databases/santaDb.db'
    db_name_events = 'events'
    db_name_users = 'santaUsers'
    db_name_event_user_constraints = 'eventUserConstraints'
    events_table = events.Events(db_filename, db_name_events)
    users_table = users.Users(db_filename, db_name_users)

    event_user_constraints_table = EventUserConstraints(db_filename, events_table, users_table,
                                                        db_name_event_user_constraints)

    user_names = np.array(['Katya', 'Jenya', 'Aliska'])
    logins = np.array(['kitekat', 'meow', 'purr'])
    psw_hashes = np.array([123, 456, 789])
    emails = np.array(['abc@dot.com', 'def@dot.com', 'nyaha@mew.com'])
    for i in np.arange(0, user_names.size):
        users_table.add_user(user_names[i], logins[i], int(psw_hashes[i]), emails[i])
        database.print_all_database(users_table.get_database_wrapper(), db_name_users,
                                    '\nusers database after adding a user:')
    print('\n')

    user_ids = np.array([])
    for login in logins:
        user_id = users_table.get_user_id(login)
        print('id for login ' + str(login) + ' is ' + str(user_id))
        user_ids = np.append(user_ids, user_id)

    event_names = np.array(['NY2019', 'NY2020'])
    for event_name in event_names:
        events_table.add_event(event_name)
        database.print_all_database(events_table.get_database_wrapper(), db_name_events,
                                    '\nevents database after adding an event:')
    print('\n')

    event_ids = np.array([])
    for event_name in event_names:
        event_id = events_table.get_event_id(event_name)
        print('id for event name ' + str(event_name) + ' is ' + str(event_id))
        event_ids = np.append(event_ids, event_id)

    event_user_constraints_table.add_constraint(event_ids[0], user_ids[0], user_ids[1])
    database.print_all_database(event_user_constraints_table.get_database_wrapper(), db_name_event_user_constraints,
                                '\neventConstraints database with first added constraint:')

    event_user_constraints_table.add_constraint(event_ids[1], user_ids[1], user_ids[2])
    database.print_all_database(event_user_constraints_table.get_database_wrapper(), db_name_event_user_constraints,
                                '\neventConstraints database with second added constraint:')

    print('\nprint all constraints for event ID ' + str(event_ids[1]) + ' and user ID ' + str(user_ids[1]) + ':')
    print(event_user_constraints_table.get_all_rejected_users_per_event_user_pair(event_ids[1], user_ids[1]))

    print('\nDoes event ID ' + str(event_ids[1]) + ', user ID ' + str(user_ids[1]) + ', constraint user ID ' + str(
        user_ids[2]) + ' exist?')
    print(str(event_user_constraints_table.constraint_exists(event_ids[0], user_ids[0], user_ids[1])))

    event_user_constraints_table.delete_constraint(event_ids[1], user_ids[1], user_ids[2])
    database.print_all_database(event_user_constraints_table.get_database_wrapper(), db_name_event_user_constraints,
                                '\neventConstraints database with second deleted constraint:')

    print('\nDoes event ID ' + str(event_ids[1]) + ', user ID ' + str(user_ids[1]) + ', constraint user ID ' + str(
        user_ids[2]) + ' exist?')
    print(str(event_user_constraints_table.constraint_exists(event_ids[1], user_ids[1], user_ids[2])))

    event_user_constraints_table.delete_constraint(event_ids[0], user_ids[0], user_ids[1])
    database.print_all_database(event_user_constraints_table.get_database_wrapper(), db_name_event_user_constraints,
                                '\neventConstraints database with first deleted constraint:')

    for user_id in user_ids:
        users_table.delete_user(int(user_id))
    database.print_all_database(users_table.get_database_wrapper(), db_name_users,
                                'users database after deleting the user:')
    for event_id in event_ids:
        events_table.delete_event(int(event_id))
    database.print_all_database(events_table.get_database_wrapper(), db_name_events,
                                'events database after deleting the event:')


if __name__ == '__main__':
    test_event_user_constraints()
