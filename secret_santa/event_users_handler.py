import random

from common import database
from secret_santa import events, event_users, event_constraints, users


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
