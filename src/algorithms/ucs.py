import heapq
import time

def UCS(problem,logger = None):
    start_time = time.perf_counter()
    
    frontier = [(0, problem.get_init_state())]
    
    visited = set()
    paths = {problem.get_init_state() : None}
    costs = {problem.get_init_state() : 0}
    iteration = 0
    while frontier:
        iteration += 1
        cost, cur_state = heapq.heappop(frontier)
        
        if cur_state in visited:
            continue
        visited.add(cur_state)
        
        if logger and iteration % 1 == 0:
            logger.log(f"Bước {iteration}: cur state= {cur_state}, g={cost:.1f}")
        
        if problem.is_goal_state(cur_state):
            path = []
            state = cur_state
            while paths[state]:
                prev, action = paths[state]
                path.insert(0, action)
                state = prev
            if logger:
                logger.log(f"SUCCESS! Tìm thấy đường đi sau {iteration} bước")
            return {"path": path, "nodes_expanded": iteration, "time_taken": time.perf_counter() - start_time, "path_length": len(path)}
        
        for next_state, action, move_cost in problem.get_move(cur_state):
            new_cost = costs[cur_state] + move_cost
            
            if next_state not in costs or new_cost < costs[next_state]:
                costs[next_state] = new_cost
                heapq.heappush(frontier, (new_cost, next_state))
                paths[next_state] = (cur_state, action)
                if logger and iteration % 1 == 0:
                    logger.log(f"-> Check neighbor {next_state}, {action}, g={new_cost:.1f}")
    
    return None
             
                
    