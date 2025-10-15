import time
import random
from collections import deque

class NoInformationProblem:
    def __init__(self, maze, initial_positions_count=2, goal_positions_count=10):  # Tăng lên 10
        self.maze = maze
        self.goal_pos = maze.calculate_stair()
        # GIẢM belief state ban đầu chỉ còn 2 vị trí
        self.initial_belief_state = self.get_limited_initial_positions(initial_positions_count)
        # TĂNG goal belief state lên 10 vị trí đích
        self.goal_belief_state = self.generate_goal_belief(goal_positions_count)

    def get_limited_initial_positions(self, count=2):
        """Trả về số lượng giới hạn vị trí có thể đi được trong maze"""
        all_positions = []
        for y in range(len(self.maze.map_data)):
            for x in range(len(self.maze.map_data[0])):
                if self.maze.is_passable(x, y):
                    all_positions.append((x, y))
        # Lấy ngẫu nhiên 'count' vị trí từ tất cả vị trí có thể
        if len(all_positions) <= count:
            return set(all_positions)
        else:
            return set(random.sample(all_positions, count))

    def generate_goal_belief(self, count=10):
        """Tạo tập goal belief gồm ngẫu nhiên 'count' vị trí có thể đi được trong maze"""
        all_positions = []
        for y in range(len(self.maze.map_data)):
            for x in range(len(self.maze.map_data[0])):
                if self.maze.is_passable(x, y):
                    all_positions.append((x, y))
        
        # Nếu số ô passable ít hơn count thì lấy hết
        if len(all_positions) <= count:
            goal_belief = all_positions
        else:
            goal_belief = random.sample(all_positions, count)

        return frozenset(goal_belief)


    def get_init_state(self):
        return frozenset(self.initial_belief_state)

    def is_goal_state(self, belief_state):
        """Đạt goal khi belief state là tập con của goal belief state"""
        return belief_state.issubset(self.goal_belief_state)

    def get_successors(self, belief_state):
        """Tính các belief state kế tiếp"""
        possible_actions = ["UP", "DOWN", "LEFT", "RIGHT"]
        successors = []
        for action in possible_actions:
            new_belief_state = set()
            dx, dy = 0, 0
            if action == "UP":
                dy = -2
            elif action == "DOWN":
                dy = 2
            elif action == "LEFT":
                dx = -2
            elif action == "RIGHT":
                dx = 2
            for x, y in belief_state:
                # Thử di chuyển từ vị trí (x,y)
                new_x, new_y = x + dx, y + dy
                if self.maze.is_passable(new_x, new_y):
                    new_belief_state.add((new_x, new_y))
                else:
                    new_belief_state.add((x, y))
            frozen_state = frozenset(new_belief_state)
            successors.append((frozen_state, action, 1))
        return successors

# Phiên bản BFS với giới hạn chặt hơn
def BFS_NoInformation_Limited(problem, max_path_length=50, logger=None):
    """BFS với giới hạn đường đi ngắn hơn"""
    start_time = time.perf_counter()
    start_node = problem.get_init_state()
    
    if logger:
        logger.log(f"Bắt đầu BFS Limited với {len(start_node)} vị trí, max_path={max_path_length}")
        logger.log(f"Goal belief state ({len(problem.goal_belief_state)} vị trí): {problem.goal_belief_state}")

    queue = deque([(start_node, [])])
    explored = set([start_node])
    iteration = 0

    while queue and iteration < 1000000:
        iteration += 1
        current_state, path_so_far = queue.popleft()

        if iteration % 1000 == 0 and logger:
            logger.log(f"BFS Limited - Iter {iteration}: Belief size={len(current_state)}, Path length={len(path_so_far)}")

        if problem.is_goal_state(current_state):
            end_time = time.perf_counter()
            if logger:
                logger.log(f"🎯 Tìm thấy goal sau {iteration} iterations!")
            return {
                "path": path_so_far,
                "nodes_expanded": iteration,
                "time_taken": end_time - start_time,
                "path_length": len(path_so_far)
            }

        # Giới hạn độ dài đường đi chặt hơn
        if len(path_so_far) < max_path_length:
            successors = problem.get_successors(current_state)
            for next_state, action, _ in successors:
                if next_state not in explored:
                    explored.add(next_state)
                    new_path = path_so_far + [action]
                    queue.append((next_state, new_path))

    if logger:
        logger.log(f"BFS Limited không tìm thấy đường đi sau {iteration} bước")
        
    end_time = time.perf_counter()
    return {
        "path": None,
        "nodes_expanded": iteration,
        "time_taken": end_time - start_time,
        "path_length": 0
    }