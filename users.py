import database


class Users:
    def __init__(self, db_filename, db_name):
        self.database = database.DatabaseWrapper(db_filename)
        self.db_name = db_name
        self.database.execute('CREATE TABLE IF NOT EXISTS ' + db_name + ' ('
            'user_id INTEGER PRIMARY KEY, '
            'name TEXT, '
            'login TEXT, '
            'psw_hash INTEGER, '
            'email TEXT, '
            'is_verified INTEGER, '
            'wishes TEXT)')

    def get_database_wrapper(self):
        return self.database

    def get_database_name(self):
        return self.db_name

    def add_user(self, name, login, psw_hash, email, is_verified=False, wishes=''):
        if (name == '') or (login == '') or (psw_hash == 0) or (email == ''):
            print('Users::add_user: impossible to add a user with the empty parameter!')
            return
        self.database.execute('INSERT INTO ' + self.db_name +
                              ' (name, login, psw_hash, email, is_verified, wishes) VALUES (?, ?, ?, ?, ?, ?)',
                              (name, login, psw_hash, email, is_verified, wishes))

    def get_user(self, user_id):
        res = self.database.execute_and_fetch('SELECT * FROM ' + self.db_name + ' WHERE user_id = ?', (user_id,))
        user_dict = {'name': '', 'login': '', 'psw_hash': 0, 'email': '', 'is_verified': False, 'wishes': ''}
        if len(res):
            user_dict['name'] = res[0][1]
            user_dict['login'] = res[0][2]
            user_dict['psw_hash'] = res[0][3]
            user_dict['email'] = res[0][4]
            user_dict['is_verified'] = res[0][5]
            user_dict['wishes'] = res[0][6]
        return user_dict

    def get_user_id(self, login):
        res = self.database.execute_and_fetch('SELECT user_id FROM ' + self.db_name + ' WHERE login = ?', (login,))
        if not len(res):
            return -1
        else:
            return res[0][0]

    def set_verified(self, user_id, is_verified = True):
        self.__set_parameter__(user_id, 'is_verified', is_verified)

    def set_wish(self, user_id, wish):
        self.__set_parameter__(user_id, 'wishes', wish)

    def delete_user(self, user_id):
        self.database.execute('DELETE FROM ' + self.db_name + ' WHERE user_id = ?', (user_id,))

    def __set_parameter__(self, user_id, param_name, param_value):
        self.database.execute('UPDATE ' + self.db_name + ' SET ' + param_name + ' = ? WHERE user_id = ?',
                              (param_value, user_id))

# --------------------------------------------------------------------------------


def add_user_test(db_filename, db_name, name, login, psw_hash, email):
    users = Users(db_filename, db_name)
    users.add_user(name, login, psw_hash, email)
    return users.get_user_id(login)


def set_verified_test(db_filename, db_name, user_id):
    users = Users(db_filename, db_name)
    user_data = users.get_user(user_id)
    if user_data['is_verified']:
        print('set_verified_test: the user was already verified before the test, choose another one!')
        return False
    users.set_verified(user_id)
    user_data = users.get_user(user_id)
    return user_data['is_verified']


def set_wish_test(db_filename, db_name, user_id, wishes):
    users = Users(db_filename, db_name)
    user_data = users.get_user(user_id)
    if user_data['wishes'] == wishes:
        print('set_wish_test: the wish was already the one to be tested: choose another one!')
        return False
    users.set_wish(user_id, wishes)
    user_data = users.get_user(user_id)
    return user_data['wishes'] == wishes


def delete_user_test(db_filename, db_name, user_id):
    users = Users(db_filename, db_name)
    user_data = users.get_user(user_id)
    if user_data['login'] == '':
        print('delete_user_test: the user was already deleted before the test: choose another one!')
        return False
    users.delete_user(user_id)
    user_data = users.get_user(user_id)
    return user_data['login'] == ''


def print_all_users_database(db_filename, db_name, prefix):
    users = Users(db_filename, db_name)
    database_wrapper = users.get_database_wrapper()
    database.print_all_database(database_wrapper, db_name, prefix)


def run_all_user_tests():
    db_filename = '../databases/santaDb.db'
    db_name = 'santaUsers'

    #database.delete_table(db_filename, db_name)
    print_all_users_database(db_filename, db_name, 'initial database:')

    name = 'Katya'
    login = 'kitekat'
    psw_hash = 123
    email = 'abc@dot.com'

    user_id = add_user_test(db_filename, db_name, name, login, psw_hash, email)
    if user_id == -1:
        print('error in adding a user!')
        return
    print_all_users_database(db_filename, db_name, '\ndatabase after adding one user:')

    result = set_verified_test(db_filename, db_name, user_id)
    if not result:
        print('error in setting verification!')
        delete_user_test(db_filename, db_name, user_id)  # the result is not important now
        return
    print_all_users_database(db_filename, db_name, '\ndatabase after verification:')

    result = set_wish_test(db_filename, db_name, user_id, 'I wanna cat')
    if not result:
        print('error in updating a wish (first time)!')
        delete_user_test(db_filename, db_name, user_id)  # the result is not important now
        return
    print_all_users_database(db_filename, db_name, '\ndatabase after updating a wish:')

    result = set_wish_test(db_filename, db_name, user_id, 'I wanna two cats')
    if not result:
        print('error in updating a wish (second time)!')
        delete_user_test(db_filename, db_name, user_id)  # the result is not important now
        return
    print_all_users_database(db_filename, db_name, '\ndatabase after updating a wish for a second time:')

    result = delete_user_test(db_filename, db_name, user_id)
    if not result:
        print('error in deleting a user!')
        return
    print_all_users_database(db_filename, db_name, '\ndatabase after deleting the user:')


if __name__ == '__main__':
    run_all_user_tests()
