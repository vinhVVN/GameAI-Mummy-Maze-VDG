import heapq
import time

def Greedy(problem, logger = None):
    start_time = time.perf_counter()
    start = problem.get_init_state()
    frontier = [(problem.heuristic(start), start)]
    visited = set()
    paths = {start : None}
    iteration = 0
    while frontier:
        iteration += 1
        cost, cur_state = heapq.heappop(frontier)

        if cur_state in visited:
            continue
        visited.add(cur_state)
        
        if logger:
            logger.log(f"Bước {iteration}: cur state= {cur_state}, h={cost:.1f}")
        
        if problem.is_goal_state(cur_state):
            path = []
            state = cur_state
            while paths[state]:
                prev_state, action = paths[state]
                path.insert(0, action)
                state = prev_state
            
            if logger:
                logger.log(f"SUCCESS! Tìm thấy đường đi sau {iteration} bước")
            return {"path": path, "nodes_expanded": iteration, "time_taken": time.perf_counter() - start_time, "path_length": len(path)}

        for next_state, action, _ in problem.get_move(cur_state):
            if next_state in visited:
                continue
            
            h_cost = problem.heuristic(next_state)
            heapq.heappush(frontier, (h_cost, next_state))
            if next_state not in paths:
                paths[next_state] = (cur_state, action)
                if logger:
                    logger.log(f"-> Check neighbor {next_state}, {action}, h={h_cost:.1f}")

    return None




