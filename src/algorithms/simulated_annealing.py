import random
import os
import math
import time

def cost_path(problem, path):
    total_cost = 0
    current_state = problem.get_init_state()
    
    for action in path:
        player_pos, mummy_pos = current_state
        moves = problem.get_move(current_state)
        found_move = False # kiểm tra nếu một nước đi trong path ko hợp lệ (đi vô tường)
        for next_state, action_sim, cost_sim in moves:
            if action_sim == action:
                total_cost += cost_sim
                current_state = next_state
                found_move = True
                break
        
        if not found_move:
            return float('inf')
    
    if not problem.is_goal_state(current_state):
        return float('inf')
    
    return total_cost + problem.heuristic(current_state)

def swap_adjacent_moves(path):
    #Hoán đổi hai hành động liền kề
    if len(path) < 2:
        return path
    new_path = list(path)
    i = random.randint(0, len(new_path) - 2)
    new_path[i], new_path[i+1] = new_path[i+1], new_path[i]
    return new_path
    

def reverse_subpath(path):
    # Đảo ngược một đoạn ngẫu nhiên của con đường
    if len(path) < 2:
        return path
    new_path = list(path)
    i, j = sorted(random.sample(range(len(new_path)),2))
    subpath = new_path[i:j+1]
    subpath.reverse()
    new_path[i:j+1] = subpath
    return new_path
    

def remove_redundancy(path):
    # Tìm và xóa các bước đi thừa (vd: UP rồi DOWN)
    if len(path) < 2: 
        return path
    new_path = list(path)
    opposites = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}
    
    i = 0
    while i < len(new_path) - 1:
        if new_path[i+1] == opposites.get(new_path[i]):
            new_path.pop(i)
            new_path.pop(i)
            # Quay lại để kiểm tra lại từ đầu nếu có sự thay đổi
            i = 0 
        else:
            i += 1
    return new_path

def insert_detour(path):
    # Chèn một bước đi và bước đi ngược lại
    if not path: 
        return ["UP", "DOWN"] 
    new_path = list(path)
    index = random.randint(0, len(new_path))
    action = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
    opposite = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}[action]
    
    new_path.insert(index, action)
    new_path.insert(index + 1, opposite)
    return new_path

def get_a_neighbor(path):
    if not path:
        return None
    
    # Chọn ngẫu nhiên một trong các kỹ thuật đột biến
    mutation_technique = random.choice([swap_adjacent_moves,
                                        reverse_subpath,
                                        insert_detour] + [remove_redundancy]*3)
    return mutation_technique(path)

def get_neighbor(problem, path):
    num_neighbor = 3
    neighbors = []
    
    for _ in range(num_neighbor):
        neighbor_path = get_a_neighbor(path)
        if neighbor_path:
            neighbors.append(neighbor_path)
    
    if not neighbors:
        return None
    
    neighbor_costs = []
    for neighbor in neighbors:
        cost = cost_path(problem, neighbor)
        if cost != float('inf'):
            neighbor_costs.append((neighbor, cost))
    
    if not neighbor_costs:
        return get_a_neighbor(path)
    
    min_cost = min(cost for _, cost in neighbor_costs)
    best_paths = [neighbor for neighbor, cost in neighbor_costs if cost == min_cost]
    chosen_path = random.choice(best_paths)
    
    return chosen_path

def random_path(problem): # loang đường đi ngẫu nhiên
    path = []
    current_state = problem.get_init_state()
    visited_count = {current_state: 1} 
    max_steps = 100 

    for _ in range(max_steps):
        if problem.is_goal_state(current_state):
            return path
            
        moves = problem.get_move(current_state)
        if not moves: 
            continue # Bị kẹt

        # ưu tiên cho các ô ít được ghé thăm
        weights = []
        for next_state, action, cost in moves:
            weight = 1.0 / (visited_count.get(next_state, 0) + 1)
            weights.append(weight)
        
        next_state, action, _ = random.choices(moves, weights=weights, k=1)[0]

        path.append(action)
        current_state = next_state
        visited_count[current_state] = visited_count.get(current_state, 0) + 1
        
    return random_path(problem) # ráng tìm cho ra

def Simulated_Annealing(problem, logger = None):
    start_time = time.perf_counter()
    nodes_counter = 0
    
    current_path = random_path(problem)
    current_cost = cost_path(problem, current_path)
    start_cost = current_cost
    
    temper = 1000
    alpha = 0.99
    mintemp = 0.0001
    
    iteration = 0
    while temper > mintemp:
        iteration += 1
        nodes_counter += 1
        neighbor_path = get_neighbor(problem, current_path)
        if neighbor_path:
            neighbor_cost = cost_path(problem, neighbor_path)
            deltaE = neighbor_cost - current_cost
            status = "REJECT"
            p_string = "N/A"
            
            if deltaE < 0:
                status = "ACCEPT (Better)"
                current_path = neighbor_path
                current_cost = neighbor_cost
            else:
                p = math.exp(-deltaE / temper)
                p_string = f"{p:.3f}"
                if random.random() < p:
                    status = "ACCEPT (Worse)"
                    current_path = neighbor_path
                    current_cost = neighbor_cost
        
        if logger and iteration % 10 == 0:
            log_message = (
                f"Iter {iteration}: T={temper:.1f}, "
                + f"E ={current_cost:.2f}, "
                + f"E'={neighbor_cost:.2f}, "
                + f"dE ={deltaE:.2f}, "
                + f"p ={p_string:}, "
                + f"Status: {status}"
            )
            logger.log(log_message)
        
        temper *= alpha
    
    
    end_time = time.perf_counter()
    return {
        "path": current_path,
        "nodes_expanded": nodes_counter,
        "time_taken": end_time - start_time,
        "initial_cost": start_cost,
        "final_cost": current_cost
    }
    

def optimize_path(problem, path): # Loại bỏ chu trình
    if not path:
        return []

    # lấy ra danh sách các trạng thái 
    states_along_path = [problem.get_init_state()]
    current_state = problem.get_init_state()
    
    for action in path:
        moves = problem.get_move(current_state)
        found_move = False
        for next_state_sim, action_sim, _ in moves:
            if action_sim == action:
                current_state = next_state_sim
                states_along_path.append(next_state_sim)
                found_move = True
                break
        if not found_move:
            break 
    
    # loại bỏ chu trình 
    optimized_states = []
    visited_set = set()
    for state in states_along_path:
        if state in visited_set:
            # quay lại vị trí lần đầu ghé thăm
            first_visit_index = optimized_states.index(state)
            
            # xóa các trạng thái thừa 
            states_to_remove = optimized_states[first_visit_index + 1:]
            for s in states_to_remove:
                visited_set.remove(s)
            optimized_states = optimized_states[:first_visit_index + 1]
        else:
            optimized_states.append(state)
            visited_set.add(state)
            
    # chuyển đổi thành chuỗi hành động
    final_path = []
    for i in range(len(optimized_states) - 1):
        state1 = optimized_states[i]
        state2 = optimized_states[i+1]
    
        moves = problem.get_move(state1)
        action_found = False
        for next_state, action, _ in moves:
            if next_state == state2:
                final_path.append(action)
                action_found = True
                break
        if not action_found:
            return states_along_path # Trả về phần đã có
            
    return final_path
    