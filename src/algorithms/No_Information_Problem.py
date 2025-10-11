import time
import random
from collections import deque

class NoInformationProblem:
    def __init__(self, maze, initial_positions_count=3):
        self.maze = maze
        self.goal_pos = maze.calculate_stair()
        
        # GIỚI HẠN belief state ban đầu chỉ khoảng 3 vị trí
        self.initial_belief_state = self.get_limited_initial_positions(initial_positions_count)

    def get_limited_initial_positions(self, count=3):
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

    def get_init_state(self):
        return frozenset(self.initial_belief_state)

    def is_goal_state(self, belief_state):
        """Đạt goal khi biết chắc vị trí và đang ở goal"""
        return len(belief_state) == 1 and self.goal_pos in belief_state

    def get_successors(self, belief_state):
        """Tính các belief state kế tiếp"""
        possible_actions = ["UP", "DOWN", "LEFT", "RIGHT"]
        successors = []

        for action in possible_actions:
            new_belief_state = set()
            dx, dy = 0, 0
            if action == "UP": 
                dy = -1
            elif action == "DOWN": 
                dy = 1
            elif action == "LEFT": 
                dx = -1
            elif action == "RIGHT": 
                dx = 1

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

def BFS_NoInformation(problem, logger = None):
    """BFS đơn giản cho bài toán không có thông tin"""
    start_time = time.perf_counter()
    start_node = problem.get_init_state()
    
    if logger:
        logger.log(f"Bắt đầu BFS No Information với {len(start_node)} vị trí có thể")
        logger.log(f"Các vị trí ban đầu: {start_node}")
        logger.log(f"Vị trí goal: {problem.goal_pos}")
    
    # Queue: (belief_state, path_so_far)
    queue = deque([(start_node, [])])
    explored = set([start_node])
    iteration = 0
    max_iterations = 500000
    
    while queue and iteration < max_iterations:
        iteration += 1
        current_state, path_so_far = queue.popleft()
        
        # Debug mỗi 100 bước
        if logger and iteration % 100 == 0:
            logger.log(f"BFS - Iter {iteration}: Belief size={len(current_state)}, Path length={len(path_so_far)}, Queue size={len(queue)}")
        
        # Kiểm tra goal state
        if problem.is_goal_state(current_state):
            end_time = time.perf_counter()
            return {
                "path": path_so_far, "nodes_expanded": iteration, 
                "time_taken": end_time - start_time, "path_length": len(path_so_far)
            }
        
        
        # Giới hạn độ dài đường đi để tránh quá sâu
        if len(path_so_far) < 100:  # Tăng giới hạn đường đi
            successors = problem.get_successors(current_state)
            
            for next_state, action, _ in successors:
                if next_state not in explored:
                    explored.add(next_state)
                    new_path = path_so_far + [action]
                    queue.append((next_state, new_path))
                    
                    # Debug cho các belief state nhỏ
                    if len(next_state) < len(current_state):
                        logger.log(f"  -> Belief state giảm: {len(current_state)} -> {len(next_state)}")
    
    end_time = time.perf_counter()
    
    return {
                "path": None, "nodes_expanded": len(explored), 
                "time_taken": end_time - start_time, "path_length": len(queue)
            }


# Phiên bản BFS với giới hạn chặt hơn
def BFS_NoInformation_Limited(problem, max_path_length=50, logger = None):
    """BFS với giới hạn đường đi ngắn hơn"""
    start_time = time.perf_counter()
    start_node = problem.get_init_state()
    
    if logger:
        logger.log(f"Bắt đầu BFS Limited với {len(start_node)} vị trí, max_path={max_path_length}")
    
    queue = deque([(start_node, [])])
    explored = set([start_node])
    iteration = 0
    
    while queue and iteration < 1000000:
        iteration += 1
        current_state, path_so_far = queue.popleft()
        
        if iteration % 1000 == 0:
            logger.log(f"BFS Limited - Iter {iteration}: Belief size={len(current_state)}, Path length={len(path_so_far)}")
        
        if problem.is_goal_state(current_state):
            end_time = time.perf_counter()
            return {
                "path": path_so_far, "nodes_expanded": iteration, 
                "time_taken": end_time - start_time, "path_length": len(path_so_far)
            }
        
        # Giới hạn độ dài đường đi chặt hơn
        if len(path_so_far) < max_path_length:
            successors = problem.get_successors(current_state)
            
            for next_state, action, _ in successors:
                if next_state not in explored:
                    explored.add(next_state)
                    new_path = path_so_far + [action]
                    queue.append((next_state, new_path))
    
    print(f"BFS Limited không tìm thấy đường đi sau {iteration} bước")
    end_time = time.perf_counter()
    return {
                "path": None, "nodes_expanded": len(explored), 
                "time_taken": end_time - start_time, "path_length": len(queue)
            }