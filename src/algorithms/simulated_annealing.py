import random
import os
import math

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
    
    return total_cost

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
    

def get_a_neighbor(path):
    if not path:
        return None
    
    # Chọn ngẫu nhiên một trong các kỹ thuật đột biến
    mutation_technique = random.choice([swap_adjacent_moves, reverse_subpath])
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
    
    scores = [1.0 / (item[1] + 1) for item in neighbor_costs] # tính xác suất chọn
    paths = [item[0] for item in neighbor_costs]
    chosen_path = random.choices(paths, weights=scores, k=1)[0]
    
    return chosen_path

def random_path(problem):
    path = []
    current_state = problem.get_init_state()
    visited = {current_state}
    max_step = 67
    for _ in range(max_step):
        if problem.is_goal_state(current_state):
            return path
        moves = problem.get_move(current_state)
        unvisited = [move for move in moves if move[0] not in visited] # tránh chu trình
        if unvisited: # ưu tiên đi vào ô mới
            next_state, action, _ = random.choice(unvisited)
        elif moves:
            next_state, action, _ = random.choice(moves)
        else: # bị kẹt
            return path

        path.append(action)
        current_state = next_state
        visited.add(current_state)
    
    return path

def Simulated_Annealing(problem):
    current_path = random_path(problem)
    current_cost = cost_path(problem, current_path)
    
    temper = 1000
    alpha = 0.95
    mintemp = 0.0001
    
    while temper > mintemp:
        neighbor_path = get_neighbor(problem, current_path)
        if neighbor_path:
            neighbor_cost = cost_path(problem, neighbor_path)
            deltaE = neighbor_cost - current_cost
            if deltaE < 0:
                print('Tìm thấy E thấp hơn')
            if deltaE < 0 or random.random() < math.exp(-deltaE / temper):
                
                current_path = neighbor_path
                current_cost = neighbor_cost
        
        temper *= alpha
    
    return current_path
    