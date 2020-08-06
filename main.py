import database
import users
import events
import event_users
import event_constraints
import random

class EventUsersHandler:
    def __init__(self, db_filename, events_table, users_table, event_users_table, event_constraints_table):
        self.events = events.Events(db_filename, events_table)
        self.users = users.Users(db_filename, users_table)
        self.event_users = event_users.EventUsers(db_filename, events_table, users_table, event_users_table)
        self.event_constraints = event_constraints.EventUserConstraints(db_filename, events_table, users_table,
                                                                        event_constraints_table)

    def get_users(self):
        return self.users

    def get_events(self):
        return self.events

    def get_event_users(self):
        return self.event_users

    def get_event_constraints(self):
        return self.event_constraints

    def assign_receiver(self, event_id):
        user_ids = self.event_users.get_all_users_per_event(event_id)

        all_allowed_users = []
        for user_id in user_ids:
            constraint_user_ids = self.event_constraints.get_all_rejected_users_per_event_user_pair(event_id, user_id)
            allowed_users = []
            for allowed_candidate in user_ids:
                if (constraint_user_ids.count(allowed_candidate) == 0) and (allowed_candidate != user_id):
                    allowed_users.append(allowed_candidate)
            all_allowed_users.append(allowed_users)

        # sort allowed users by the amount of such users, sorted_order is the index of a sorted list
        sorted_order = sorted(range(len(all_allowed_users)), key=lambda k: len(all_allowed_users[k]))
        assigned_user_ids = []

        for i in sorted_order:
            # remove all already assigned users since they're not allowed anymore
            updated_allowed_users = [x for x in all_allowed_users[i] if x not in assigned_user_ids[i]]
            if len(updated_allowed_users) == 0:
                return False
            assigned_user_id = random.choice(updated_allowed_users)
            assigned_user_ids.append(assigned_user_id)

        # not in the previous cycle not to spoil database with incorrect data (what if we return False in the middle of it?)
        for user_id in user_ids:
            index_in_a_sorted_list = sorted_order.index(user_id)
            self.event_users.assign_receiver(event_id, user_id, assigned_user_ids[index_in_a_sorted_list])

        return True


def test_assignation():
    #todo


if __name__ == '__main__':
    test_assignation()
