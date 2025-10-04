import heapq
import time

def AStar_Belief(problem, logger = None):
    start_time = time.perf_counter()
    start_node = problem.get_init_state()

    frontier = [(problem.heuristic(start_node), start_node)] 
    paths = {start_node: None}
    cost_so_far = {start_node: 0}
    
    iteration = 0

    while frontier:
        iteration += 1
        f_cost, current_state = heapq.heappop(frontier)
        
        if logger:
            h_cost = f_cost - 0
            logger.log(
                f"Bước {iteration}: Belief state size ={len(current_state):<3} | "
                f"g={0:<3.0f} | h={h_cost:<3.0f} | f={f_cost:<3.0f}"
            )

        if problem.is_goal_state(current_state):
            end_time = time.perf_counter()
            
            path = []
            state = current_state
            while paths[state] is not None:
                prev_state, action = paths[state]
                path.insert(0, action)
                state = prev_state
            
            if logger:
                logger.log(f"SUCCESS! Tìm thấy đường đi sau {iteration} bước")
            return {
                "path": path, "nodes_expanded": iteration, 
                "time_taken": end_time - start_time, "path_length": len(path)
            }
            

        for next_state, action, cost in problem.get_successors(current_state):
            new_g_cost = cost_so_far[current_state] + cost
            if next_state not in cost_so_far or new_g_cost < cost_so_far[next_state]:
                cost_so_far[next_state] = new_g_cost
                new_f_cost = new_g_cost + problem.heuristic(next_state)
                heapq.heappush(frontier, (new_f_cost, next_state))
                paths[next_state] = (current_state, action)
                if logger:
                    logger.log(f"-> Check when {action}, g={new_g_cost:.1f}, h = {(new_f_cost - new_g_cost):.1f}, f = {new_f_cost:.1f}")
    
    end_time = time.perf_counter()
    return {"path": None, "nodes_expanded": iteration, "time_taken": end_time - start_time}