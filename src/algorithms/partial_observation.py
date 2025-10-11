import random

class PartialObservationProblem:
    def __init__(self, maze):
        self.maze = maze
        self.goal_pos = maze.calculate_stair() 

        self.initial_belief_state = set()
        for r in range(1, len(maze.map_data), 2):
            for c in range(1, len(maze.map_data[0]), 2):
                if maze.is_passable(c, r):
                    self.initial_belief_state.add((c, r))

    def get_init_state(self):
        return frozenset(self.initial_belief_state)

    def is_goal_state(self, belief_state):
        return len(belief_state) == 1 and self.goal_pos in belief_state

    def create_percept(self, pos, next_pos):
        bx, by = pos
        ax, ay = next_pos
        gx, gy = self.goal_pos
        dist_before = abs(bx - gx) + abs(by - gy)
        dist_after = abs(ax - gx) + abs(ay - gy)

        dx, dy = ax-bx, ay-by
        return dist_after < dist_before
    
    
    
    def get_successors(self, belief_state):
        possible_actions = ["UP", "DOWN", "LEFT", "RIGHT"]
        successors = []

        for action in possible_actions:
            dx, dy = 0, 0
            if action == "UP": dy = -2
            elif action == "DOWN": dy = 2
            elif action == "LEFT": dx = -2
            elif action == "RIGHT": dx = 2

            outcomes = {
                True: set(),  # tiến bộ
                False: set()  # không tiến bộ 
            }

            for x, y in belief_state:
                next_pos = (x, y) 
                if self.maze.is_passable(x + dx // 2, y + dy // 2):
                    next_pos = (x + dx, y + dy)

                percept = self.create_percept((x, y), next_pos)
                outcomes[percept].add(next_pos)

            # chọn ngẫu nhiên lân cận cho không tiến bộ
            if outcomes[False]:
                for x, y in belief_state:
                    candidates = [(2, 0), (-2, 0), (0, 2), (0, -2)]
                    random.shuffle(candidates)
                    for c in candidates:
                        if self.maze.is_passable(x + c[0]//2, y + c[1]//2):
                            outcomes[False].add((x+c[0], y + c[1]))
                            break  # mỗi state một lân cận
                        

            for percept, new_set in outcomes.items():
                if new_set:
                    new_belief = frozenset(new_set)
                    successors.append((new_belief, action, 0))  

        return successors

    def heuristic(self, belief_state):
        if not belief_state:
            return float('inf')

        max_dist = max(abs(s[0] - self.goal_pos[0]) + abs(s[1] - self.goal_pos[1]) for s in belief_state)
        return max_dist