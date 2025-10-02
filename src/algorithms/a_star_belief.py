import heapq
import time

def AStar_Belief(problem):
    start_time = time.perf_counter()
    start_node = problem.get_init_state()

    frontier = [(problem.heuristic(start_node), start_node)] # (f_cost, state)
    paths = {start_node: None}
    cost_so_far = {start_node: 0}
    
    # Biến debug
    iteration = 0

    while frontier:
        iteration += 1
        f_cost, current_state = heapq.heappop(frontier)
        
        # In log debug
        if iteration % 20 == 0:
            print(f"Debug A* Belief: Iter {iteration}, Exploring belief state size: {len(current_state)}")

        if problem.is_goal_state(current_state):
            end_time = time.perf_counter()
            path = []
            state = current_state
            while paths[state] is not None:
                prev_state, action = paths[state]
                path.insert(0, action)
                state = prev_state
            
            # return {
            #     "path": path, "nodes_expanded": iteration, 
            #     "time_taken": end_time - start_time, "path_length": len(path)
            # }
            return path

        for next_state, action, cost in problem.get_successors(current_state):
            new_g_cost = cost_so_far[current_state] + cost
            if next_state not in cost_so_far or new_g_cost < cost_so_far[next_state]:
                cost_so_far[next_state] = new_g_cost
                new_f_cost = new_g_cost + problem.heuristic(next_state)
                heapq.heappush(frontier, (new_f_cost, next_state))
                paths[next_state] = (current_state, action)
    
    end_time = time.perf_counter()
    return None