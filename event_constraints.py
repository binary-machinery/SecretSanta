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
        res = self.database.execute_and_fetch('SELECT constraint_user_id FROM ' + self.db_name +
                                        ' WHERE (event_id, user_id) = (?, ?)', (event_id, user_id))
        if not len(res):
            return []
        else:
            return [i[0] for i in res]

    def constraint_exists(self, event_id, user_id, constraint_user_id):
        res = self.database.execute_and_fetch('SELECT event_id FROM ' + self.db_name +
                                              ' WHERE (event_id, user_id, constraint_user_id) = (?, ?, ?)',
                                              (event_id, user_id, constraint_user_id))
        return (not res) == False

# --------------------------------------------------------------------------------


def add_constraint_test(db_filename, events_table, users_table, event_user_constraint_db_name,
                                    event_id, user_id, constraint_user_id):
    if events_table.get_name(event_id) == '':
        print('add_constraint_test: event ID is not a member of Events table!')
        return False
    if users_table.get_user(user_id)['login'] == '':
        print('add_constraint_test: user ID is not a member of Users table!')
        return False
    if users_table.get_user(constraint_user_id)['login'] == '':
        print('add_constraint_test: constraint user ID is not a member of Users table!')
        return False

    event_user_constraint_table = \
        EventUserConstraints(db_filename, events_table, users_table, event_user_constraint_db_name)
    if constraint_user_id in event_user_constraint_table.get_all_rejected_users_per_event_user_pair(event_id, user_id):
        print('add_constraint_test: such event-user pair already exists in the table, choose another one!')
        return False

    event_user_constraint_table.add_constraint(event_id, user_id, constraint_user_id)

    if not event_user_constraint_table.constraint_exists(event_id, user_id, constraint_user_id):
        print('add_constraint_test: addition was done incorrectly!')
        return False
    return True


def get_all_rejected_users_per_event_user_pair_test(db_filename,
                                                    events_table, users_table, event_user_constraint_db_name,
                                                    event_id, user_id, expected_constraint_user_ids):
    if events_table.get_name(event_id) == '':
        print('get_all_rejected_users_per_event_user_pair_test: event ID is not a member of Events table!')
        return False
    if users_table.get_user(user_id)['login'] == '':
        print('get_all_rejected_users_per_event_user_pair_test: user ID is not a member of Users table!')
        return False
    for constraint_user_id in expected_constraint_user_ids:
        if users_table.get_user(constraint_user_id)['login'] == '':
            print('get_all_rejected_users_per_event_user_pair_test: constraint user ID is not a member of Users table!')
            return False

    event_user_constraint_table = \
        EventUserConstraints(db_filename, events_table, users_table, event_user_constraint_db_name)
    all_constraint_users_per_pair = event_user_constraint_table.get_all_rejected_users_per_event_user_pair(event_id,
                                                                                                           user_id)
    for constraint_user_id in expected_constraint_user_ids:
        if not constraint_user_id in all_constraint_users_per_pair:
            print('get_all_rejected_users_per_event_user_pair_test: expected constraint user ID ' +
                  str(constraint_user_id) + ' is not found in the list of constraint users!')
            return False
    return True


def constraint_exists_test(db_filename, events_table, users_table, event_user_constraint_db_name,
                           event_id, user_id, constraint_user_id, constraint_exisist):
    if events_table.get_name(event_id) == '':
        print('constraint_exists_test: event ID is not a member of Events table!')
        return False
    if users_table.get_user(user_id)['login'] == '':
        print('constraint_exists_test: user ID is not a member of Users table!')
        return False
    if users_table.get_user(constraint_user_id)['login'] == '':
        print('constraint_exists_test: constraint user ID is not a member of Users table!')
        return False

    event_user_constraint_table = \
        EventUserConstraints(db_filename, events_table, users_table, event_user_constraint_db_name)

    return event_user_constraint_table.constraint_exists(event_id, user_id, constraint_user_id) == constraint_exisist


def delete_constraint_test(db_filename, events_table, users_table, event_user_constraint_db_name,
                        event_id, user_id, constraint_user_id):
    if events_table.get_name(event_id) == '':
        print('delete_constraint_test: event ID is not a member of Events table!')
        return False
    if users_table.get_user(user_id)['login'] == '':
        print('delete_constraint_test: user ID is not a member of Users table!')
        return False
    if users_table.get_user(constraint_user_id)['login'] == '':
        print('delete_constraint_test: constraint user ID is not a member of Users table!')
        return False

    event_user_constraint_table = \
        EventUserConstraints(db_filename, events_table, users_table, event_user_constraint_db_name)

    if not (constraint_user_id in
            event_user_constraint_table.get_all_rejected_users_per_event_user_pair(event_id, user_id)):
        print('delete_constraint_test: such event-user pair doesn\'t exist in the table, choose another one!')
        return False

    event_user_constraint_table.delete_constraint(event_id, user_id, constraint_user_id)

    if event_user_constraint_table.constraint_exists(event_id, user_id, constraint_user_id):
        print('delete_constraint_test: deletion was done incorrectly!')
        return False
    return True


def print_all_event_user_constraints(db_filename, events_table, users_table, db_name_event_user_constraints, prefix):
    events_users_table = EventUserConstraints(db_filename, events_table, users_table, db_name_event_user_constraints)
    database_wrapper = events_users_table.get_database_wrapper()
    database.print_all_database(database_wrapper, db_name_event_user_constraints, prefix)


def run_all_event_user_constraints_tests():
    db_filename = '../databases/santaDb.db'
    db_name_events = 'events'
    db_name_users = 'santaUsers'
    db_name_event_user_constraints = 'eventUserConstraints'

    #database.delete_table(db_filename, db_name_users)
    #database.delete_table(db_filename, db_name_events)
    #database.delete_table(db_filename, db_name_event_user_constraints)

    user_name = 'Katya'
    login = 'kitekat'
    psw_hash = 123
    email = 'abc@dot.com'

    user_name_constraints = ['Jenya', 'Aliska']
    login_constraints = ['fckrsns', 'meow']
    psw_hash_constraints = [456, 789]
    email_constraints = ['def@dot.com', 'meow@purr.nyaha']

    non_existed_user_name_constraint = 'Vasya Pipkin'
    non_existed_login_constraint = 'konechnovasya'
    non_existed_psw_hash_constraint = 333
    non_existed_email_constraint = 'vasya.pipkin@dot.com'

    event_name = 'NY2020'

    user_id = users.add_user_test(db_filename, db_name_users, user_name, login, psw_hash, email)

    user_id_constraints = []
    for i in range(len(user_name_constraints)):
        user_id_constraint = users.add_user_test(db_filename, db_name_users, user_name_constraints[i],
                                                 login_constraints[i], psw_hash_constraints[i], email_constraints[i])
        user_id_constraints.append(user_id_constraint)

    non_existed_user_id_constraint = users.add_user_test(db_filename, db_name_users,
                                                         non_existed_user_name_constraint, non_existed_login_constraint,
                                                         non_existed_psw_hash_constraint, non_existed_email_constraint)

    event_id = events.add_event_test(db_filename, db_name_events, event_name)

    users.print_all_users_database(db_filename, db_name_users, '\nusers database:')
    events.print_all_events_database(db_filename, db_name_events, '\nevents database:')

    users_table = users.Users(db_filename, db_name_users)
    events_table = events.Events(db_filename, db_name_events)

    for user_id_constraint in user_id_constraints:
        result = add_constraint_test(db_filename, events_table, users_table, db_name_event_user_constraints,
                                     event_id, user_id, user_id_constraint)
        if not result:
            print('error in adding constraint user ID' + str(user_id_constraint))
            for user_id_constraint_to_delete in user_id_constraints:
                delete_constraint_test(db_filename, events_table, users_table, db_name_event_user_constraints, event_id,
                                       user_id, user_id_constraint_to_delete)  # the result is not important now
            users.delete_user_test(db_filename, db_name_users, user_id)
            users.delete_user_test(db_filename, db_name_users, non_existed_user_id_constraint)
            for user_id_constraint_to_delete in user_id_constraints:
                users.delete_user_test(db_filename, db_name_users, user_id_constraint_to_delete)
            events.delete_event_test(db_filename, db_name_events, event_id)
            return
    print_all_event_user_constraints(db_filename, events_table, users_table, db_name_event_user_constraints,
                                     '\ndatabase after adding all constraints:')

    result = get_all_rejected_users_per_event_user_pair_test(db_filename,
                                                             events_table, users_table, db_name_event_user_constraints,
                                                             event_id, user_id, user_id_constraints)
    if not result:
        print('error in getting all constraint users!')
        for user_id_constraint_to_delete in user_id_constraints:
            delete_constraint_test(db_filename, events_table, users_table, db_name_event_user_constraints, event_id,
                                   user_id, user_id_constraint_to_delete)  # the result is not important now
        users.delete_user_test(db_filename, db_name_users, user_id)
        users.delete_user_test(db_filename, db_name_users, non_existed_user_id_constraint)
        for user_id_constraint_to_delete in user_id_constraints:
            users.delete_user_test(db_filename, db_name_users, user_id_constraint_to_delete)
        events.delete_event_test(db_filename, db_name_events, event_id)
        return
    print_all_event_user_constraints(db_filename, events_table, users_table, db_name_event_user_constraints,
                                     '\ndatabase after getting all constraint users:')

    for user_id_constraint in user_id_constraints:
        result = constraint_exists_test(db_filename, events_table, users_table, db_name_event_user_constraints,
                                        event_id, user_id, user_id_constraint, True)
        if not result:
            print('error in checking if constraint user ID' + str(user_id_constraint) + ' exists!')
            for user_id_constraint_to_delete in user_id_constraints:
                delete_constraint_test(db_filename, events_table, users_table, db_name_event_user_constraints, event_id,
                                       user_id, user_id_constraint_to_delete)  # the result is not important now
            users.delete_user_test(db_filename, db_name_users, user_id)
            users.delete_user_test(db_filename, db_name_users, non_existed_user_id_constraint)
            for user_id_constraint_to_delete in user_id_constraints:
                users.delete_user_test(db_filename, db_name_users, user_id_constraint_to_delete)
            events.delete_event_test(db_filename, db_name_events, event_id)
            return

    result = constraint_exists_test(db_filename, events_table, users_table, db_name_event_user_constraints,
                                    event_id, user_id, non_existed_user_id_constraint, False)
    if not result:
        print('error in checking if constraint user ID' + str(user_id_constraint) + ' exists!')
        for user_id_constraint_to_delete in user_id_constraints:
            delete_constraint_test(db_filename, events_table, users_table, db_name_event_user_constraints, event_id,
                                   user_id, user_id_constraint_to_delete)  # the result is not important now
        users.delete_user_test(db_filename, db_name_users, user_id)
        users.delete_user_test(db_filename, db_name_users, non_existed_user_id_constraint)
        for user_id_constraint_to_delete in user_id_constraints:
            users.delete_user_test(db_filename, db_name_users, user_id_constraint_to_delete)
        events.delete_event_test(db_filename, db_name_events, event_id)
        return

    print_all_event_user_constraints(db_filename, events_table, users_table, db_name_event_user_constraints,
                                     '\ndatabase after checking if all constraint users exist:')

    for user_id_constraint in user_id_constraints:
        result = delete_constraint_test(db_filename, events_table, users_table, db_name_event_user_constraints,
                                        event_id, user_id, user_id_constraint)
        if not result:
            print('error in deleting constraint with ID' + str(user_id_constraint))
            for user_id_constraint_to_delete in user_id_constraints:
                delete_constraint_test(db_filename, events_table, users_table, db_name_event_user_constraints, event_id,
                                       user_id, user_id_constraint_to_delete)  # the result is not important now
            users.delete_user_test(db_filename, db_name_users, user_id)
            users.delete_user_test(db_filename, db_name_users, non_existed_user_id_constraint)
            for user_id_constraint_to_delete in user_id_constraints:
                users.delete_user_test(db_filename, db_name_users, user_id_constraint_to_delete)
            events.delete_event_test(db_filename, db_name_events, event_id)
            return
    print_all_event_user_constraints(db_filename, events_table, users_table, db_name_event_user_constraints,
                                     '\ndatabase after deleting all constraints:')

    users.delete_user_test(db_filename, db_name_users, user_id)
    users.delete_user_test(db_filename, db_name_users, non_existed_user_id_constraint)
    for user_id_constraint in user_id_constraints:
        users.delete_user_test(db_filename, db_name_users, user_id_constraint)
    events.delete_event_test(db_filename, db_name_events, event_id)


if __name__ == '__main__':
    run_all_event_user_constraints_tests()
