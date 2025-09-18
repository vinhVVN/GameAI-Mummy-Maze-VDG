import heapq # Thư viện cho hàng đợi ưu tiên

def AStar(problem):
    # Hàng đợi ưu tiên chứa: (f_cost, g_cost, state)
    # g_cost là chi phí thực tế từ đầu đến state
    frontier = [(0, 0, problem.get_init_state())] 
    
    visited = set()
    paths = {problem.get_init_state(): None}
    cost_so_far = {problem.get_init_state(): 0}

    print("Starting A* search...")

    while frontier:
        # Lấy ra nút có f_cost thấp nhất
        f_cost, g_cost, current_state = heapq.heappop(frontier)

        if current_state in visited:
            continue
        
        visited.add(current_state)

        if problem.is_goal_state(current_state):
            print("A* found a path!")
            # Tái tạo đường đi (tương tự BFS)
            path = []
            state = current_state
            while paths[state] is not None:
                prev_state, action = paths[state]
                path.insert(0, action)
                state = prev_state
            return path

        for next_state, action, cost in problem.get_move(current_state):
            new_g_cost = g_cost + cost
            
            if next_state not in cost_so_far or new_g_cost < cost_so_far[next_state]:
                cost_so_far[next_state] = new_g_cost
                h_cost = problem.heuristic(next_state)
                new_f_cost = new_g_cost + h_cost * 12.5
                
                heapq.heappush(frontier, (new_f_cost, new_g_cost, next_state))
                paths[next_state] = (current_state, action)
    
    print("A* found no solution.")
    return None