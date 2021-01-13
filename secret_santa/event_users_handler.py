import random


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
                constraints[constraint.user_id] = set()
            constraints[constraint.user_id].add(constraint.constraint_user_id)

        result = EventUsersHandler.run_search(user_ids, constraints)
        if result is None:
            return False

        for index, user_id in enumerate(result):
            next_index = (index + 1) % len(result)
            self.event_users.set_receiver(event_id, user_id, result[next_index])

        return True

    # Caution: the method modifies the user_ids arg
    @staticmethod
    def run_search(user_ids, constraints):
        class ResTreeNode:
            def __init__(self, user_id):
                self.used_ids = set()
                self.cur_id = user_id

            def __str__(self):
                return str(self.cur_id) + " (" + str(self.used_ids) + ")"

        res = []
        iteration = 0
        while True:
            iteration += 1
            constraints_len = 0
            if len(res) > 0:
                cur_user_id_node = res[-1]
                constraint_user_ids = constraints.get(cur_user_id_node.cur_id, set())

                if len(constraint_user_ids) or len(cur_user_id_node.used_ids):
                    # move constrained and used ids to the end of the list
                    index = 0
                    scan_max = len(user_ids)
                    while index < scan_max:
                        if user_ids[index] in constraint_user_ids or user_ids[index] in cur_user_id_node.used_ids:
                            user_ids.append(user_ids.pop(index))
                            scan_max -= 1
                            constraints_len += 1
                        else:
                            index += 1

            max_index = len(user_ids) - constraints_len
            need_go_back = max_index == 0
            if not need_go_back:
                index = random.randint(0, max_index - 1)
                user_id = user_ids.pop(index)
                res.append(ResTreeNode(user_id))

                if len(user_ids) == 0:
                    cur_user_id_node = res[-1]
                    constraint_user_ids = constraints.get(cur_user_id_node.cur_id, set())
                    if res[0].cur_id in constraint_user_ids:
                        need_go_back = True
                    else:
                        break

            if need_go_back:
                # return one step back
                if len(res) == 1:
                    # no way to go back anymore, there is no solution
                    print(iteration)
                    return None

                cur_node = res.pop()
                user_ids.append(cur_node.cur_id)
                res[-1].used_ids.add(cur_node.cur_id)

        print(iteration)
        return [node.cur_id for node in res]


if __name__ == "__main__":
    for iteration in range(1, 101):
        max_id = 10000
        user_ids = []
        for i in range(1, max_id):
            user_ids.append(i)

        constraints = {}
        for i in range(1, max_id):
            constraints[i] = set()
            for j in range(1, 4):
                constraints[i].add((i + j) % max_id + int((i + j) / max_id))

        EventUsersHandler.run_search(user_ids, constraints)
