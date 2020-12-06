import random

import database
import event_constraints
import event_users
import events
import users


class EventUsersHandler:
    def __init__(self, event_users_table, event_constraints_table):
        self.event_users = event_users_table
        self.event_user_constraints = event_constraints_table

    def get_event_users(self):
        return self.event_users

    def get_event_constraints(self):
        return self.event_user_constraints

    def assign_receivers(self, event_id):
        user_ids = [event_user.user_id for event_user in self.event_users.get_event_users(event_id)]
        constraints = {}
        for constraint in self.event_user_constraints.get_user_constraints_for_event(event_id):
            if constraint.user_id not in constraints:
                constraints[constraint.user_id] = []
            constraints[constraint.user_id].append(constraint.constraint_user_id)

        all_allowed_users = []
        for user_id in user_ids:
            constraint_user_ids = constraints.get(user_id, [])
            allowed_users = []
            for allowed_candidate_id in user_ids:
                if allowed_candidate_id != user_id and allowed_candidate_id not in constraint_user_ids:
                    allowed_users.append(allowed_candidate_id)
            all_allowed_users.append(allowed_users)

        # sort allowed users by the amount of such users, sorted_order is the index of a sorted list
        sorted_order = sorted(range(len(all_allowed_users)), key=lambda k: len(all_allowed_users[k]))

        assigned_user_ids = []
        for i in sorted_order:
            # remove all already assigned users since they're not allowed anymore
            updated_allowed_users = [x for x in all_allowed_users[i] if x not in assigned_user_ids]
            if len(updated_allowed_users) == 0:
                return False
            assigned_user_id = random.choice(updated_allowed_users)
            assigned_user_ids.append(assigned_user_id)

        # not in the previous cycle not to spoil database with incorrect data
        # (what if we return False in the middle of it?)
        for user_id in user_ids:
            index_in_a_sorted_list = sorted_order.index(user_ids.index(user_id))
            self.event_users.set_receiver(event_id, user_id, assigned_user_ids[index_in_a_sorted_list])

        return True


def test_assignation():
    db_filename = '../databases/santaDb.db'
    db_name_events = 'events'
    db_name_users = 'santaUsers'
    db_name_event_users = 'eventUsers'
    db_name_event_user_constraints = 'eventUserConstraints'

    user_names = ['Katya', 'Jenya', 'Aliska', 'User1', 'User2', 'User3', 'User4']
    logins = ['kitekat', 'fckrsns', 'meow', 'login1', 'login2', 'login3', 'login4']
    psws = [123, 456, 789, 1, 2, 3, 4]
    emails = ['abc@dot.com', 'def@dot.com', 'meow@purr.nyaha', 'test1@dot.com', 'test2@dot.com', 'test3@dot.com', 'test4@dot.com']

    event_names = ['NY2020', 'NY2021']

    database.delete_table(db_filename, db_name_users)
    database.delete_table(db_filename, db_name_events)
    database.delete_table(db_filename, db_name_event_users)
    database.delete_table(db_filename, db_name_event_user_constraints)

    user_ids = [0 for _ in range(len(user_names))]
    event_ids = [0 for _ in range(len(event_names))]
    for i in range(len(event_names)):
        event_ids[i] = events.add_event_test(db_filename, db_name_events, event_names[i])
    for i in range(len(user_names)):
        user_ids[i] = users.add_user_test(db_filename, db_name_users, user_names[i], logins[i], psws[i], emails[i])

    users.print_all_users_database(db_filename, db_name_users, '\nusers database:')
    events.print_all_events_database(db_filename, db_name_events, '\nevents database:')

    users_table = users.Users(db_filename, db_name_users)
    events_table = events.Events(db_filename, db_name_events)

    for user_id in user_ids:
        for event_id in event_ids:
            event_users.add_event_user_pair_test(db_filename, events_table, users_table, db_name_event_users,
                                                 event_id, user_id)
    event_users.print_all_event_users_database(db_filename, events_table, users_table, db_name_event_users,
                                               '\nevent_users database:')

    event_users_table = event_users.EventUsers(db_filename, events_table, users_table, db_name_event_users)

    event_constraints.add_constraint_test(db_filename, events_table, users_table, db_name_event_user_constraints,
                        event_ids[0], user_ids[0], user_ids[1])
    event_constraints.add_constraint_test(db_filename, events_table, users_table, db_name_event_user_constraints,
                        event_ids[0], user_ids[0], user_ids[2])
    event_constraints.add_constraint_test(db_filename, events_table, users_table, db_name_event_user_constraints,
                        event_ids[1], user_ids[0], user_ids[3])
    event_constraints.add_constraint_test(db_filename, events_table, users_table, db_name_event_user_constraints,
                        event_ids[1], user_ids[1], user_ids[4])
    event_constraints.add_constraint_test(db_filename, events_table, users_table, db_name_event_user_constraints,
                        event_ids[1], user_ids[6], user_ids[0])

    event_constraints.print_all_event_user_constraints(db_filename, events_table, users_table,
                                                       db_name_event_user_constraints, '\nevent constraints database:')

    event_constraints_table = event_constraints.EventUserConstraints(db_filename, events_table, users_table,
                                                                     db_name_event_user_constraints)

    handler = EventUsersHandler(db_filename, events_table, users_table, event_users_table, event_constraints_table)
    for event_id in event_ids:
        print('result of assignation for event ID ' + str(event_id) + ' is: ' + str(handler.assign_receivers(event_id)))

    event_users.print_all_event_users_database(db_filename, events_table, users_table, db_name_event_users,
                                               '\nevent_users database after receiver assignation:')


if __name__ == '__main__':
    test_assignation()
