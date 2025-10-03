class PartialObservationProblem:
    def __init__(self, maze):
        self.maze = maze
        self.goal_pos = maze.calculate_stair() # (cột, hàng)

        self.initial_belief_state = set()
        for r in range(1, len(maze.map_data), 2):
            for c in range(1, len(maze.map_data[0]), 2):
                if maze.is_passable(c, r):
                    self.initial_belief_state.add((c, r))

    def get_init_state(self):
        return frozenset(self.initial_belief_state)

    def is_goal_state(self, belief_state):
        return len(belief_state) == 1 and self.goal_pos in belief_state

    def get_successors(self, belief_state):
        possible_actions = ["UP", "DOWN", "LEFT", "RIGHT"]
        successors = []

        for action in possible_actions:
            new_belief_state = set()
            dx, dy = 0, 0
            if action == "UP": dy = -2
            elif action == "DOWN": dy = 2
            elif action == "LEFT": dx = -2
            elif action == "RIGHT": dx = 2

            for x, y in belief_state:
                if self.maze.is_passable(x + dx // 2, y + dy // 2):
                    new_belief_state.add((x + dx, y + dy))
                else:
                    new_belief_state.add((x, y))
        
            successors.append((frozenset(new_belief_state), action, 0))
            
        return successors

    def heuristic(self, belief_state):
        """Heuristic là khoảng cách nhỏ nhất từ belief state đến đích."""
        if not belief_state:
            return float('inf')

        min_dist = min(abs(s[0] - self.goal_pos[0]) + abs(s[1] - self.goal_pos[1]) for s in belief_state)
        
        # Thêm một phần thưởng nhỏ cho việc giảm kích thước belief state
        # Điều này khuyến khích AI thực hiện các hành động thu thập thông tin
        return min_dist + len(belief_state)