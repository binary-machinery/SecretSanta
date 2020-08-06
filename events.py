import database


class Events:
    def __init__(self, db_filename, db_name):
        self.database = database.DatabaseWrapper(db_filename)
        self.db_name = db_name
        self.database.execute('CREATE TABLE IF NOT EXISTS ' + db_name + ' ('
            'event_id INTEGER PRIMARY KEY, '
            'event_name TEXT)')

    def get_database_wrapper(self):
        return self.database

    def get_database_name(self):
        return self.db_name

    def add_event(self, event_name):
        if event_name == '':
            print('Events::add_event: impossible to add an event with the empty name!')
            return
        self.database.execute('INSERT INTO ' + self.db_name + ' (event_name) VALUES (?)', (event_name,))

    def get_event_id(self, event_name):
        res = self.database.execute_and_fetch('SELECT event_id FROM ' + self.db_name +
                                              ' WHERE event_name = ?', (event_name,))
        if not len(res):
            return -1
        else:
            return res[0][0]

    def get_name(self, event_id):
        res = self.database.execute_and_fetch('SELECT event_name FROM ' + self.db_name +
                                              ' WHERE event_id = ?', (event_id,))
        if not len(res):
            return ''
        else:
            return res[0][0]

    def update_name(self, event_id, event_name):
        self.database.execute('UPDATE ' + self.db_name + ' SET event_name = ? WHERE event_id = ?',
                              (event_name, event_id))

    def delete_event(self, event_id):
        self.database.execute('DELETE FROM ' + self.db_name + ' WHERE event_id = ?', (event_id,))

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

    #database.delete_table(db_filename, db_name)

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
