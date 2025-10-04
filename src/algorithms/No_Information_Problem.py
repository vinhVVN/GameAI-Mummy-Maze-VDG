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

def BFS_NoInformation(problem):
    """BFS đơn giản cho bài toán không có thông tin"""
    start_time = time.perf_counter()
    start_node = problem.get_init_state()
    
    print(f"Bắt đầu BFS No Information với {len(start_node)} vị trí có thể")
    print(f"Các vị trí ban đầu: {start_node}")
    print(f"Vị trí goal: {problem.goal_pos}")
    
    # Queue: (belief_state, path_so_far)
    queue = deque([(start_node, [])])
    explored = set([start_node])
    iteration = 0
    max_iterations = 500000
    
    while queue and iteration < max_iterations:
        iteration += 1
        current_state, path_so_far = queue.popleft()
        
        # Debug mỗi 100 bước
        if iteration % 100 == 0:
            print(f"BFS - Iter {iteration}: Belief size={len(current_state)}, Path length={len(path_so_far)}, Queue size={len(queue)}")
        
        # Kiểm tra goal state
        if problem.is_goal_state(current_state):
            end_time = time.perf_counter()
            print(f"🎯 TÌM THẤY ĐƯỜNG ĐI!")
            print(f"Độ dài đường đi: {len(path_so_far)}")
            print(f"Số bước tìm kiếm: {iteration}")
            print(f"Thời gian: {end_time - start_time:.2f}s")
            print(f"Kích thước belief state cuối: {len(current_state)}")
            return path_so_far
        
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
                        print(f"  -> Belief state giảm: {len(current_state)} -> {len(next_state)}")
    
    end_time = time.perf_counter()
    print(f"❌ KHÔNG TÌM THẤY ĐƯỜNG ĐI sau {iteration} bước")
    print(f"Thời gian: {end_time - start_time:.2f}s")
    print(f"Số trạng thái đã duyệt: {len(explored)}")
    print(f"Kích thước queue cuối: {len(queue)}")
    return None

# Phiên bản BFS với giới hạn chặt hơn
def BFS_NoInformation_Limited(problem, max_path_length=50):
    """BFS với giới hạn đường đi ngắn hơn"""
    start_time = time.perf_counter()
    start_node = problem.get_init_state()
    
    print(f"Bắt đầu BFS Limited với {len(start_node)} vị trí, max_path={max_path_length}")
    
    queue = deque([(start_node, [])])
    explored = set([start_node])
    iteration = 0
    
    while queue and iteration < 1000000:
        iteration += 1
        current_state, path_so_far = queue.popleft()
        
        if iteration % 50 == 0:
            print(f"BFS Limited - Iter {iteration}: Belief size={len(current_state)}, Path length={len(path_so_far)}")
        
        if problem.is_goal_state(current_state):
            end_time = time.perf_counter()
            print(f"🎯 TÌM THẤY ĐƯỜNG ĐI!")
            print(f"Độ dài đường đi: {len(path_so_far)}")
            return path_so_far
        
        # Giới hạn độ dài đường đi chặt hơn
        if len(path_so_far) < max_path_length:
            successors = problem.get_successors(current_state)
            
            for next_state, action, _ in successors:
                if next_state not in explored:
                    explored.add(next_state)
                    new_path = path_so_far + [action]
                    queue.append((next_state, new_path))
    
    print(f"❌ BFS Limited không tìm thấy đường đi sau {iteration} bước")
    return None