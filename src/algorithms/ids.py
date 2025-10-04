import time

def IDS(problem, max_depth=110, logger = None):
    start_time = time.perf_counter()
    nodes_counter = [0] # dùng list để truyền tham chiếu
    
    start = problem.get_init_state()
    if problem.is_goal_state(start):
        return {"path": [], "nodes_expanded": 1, "time_taken": time.perf_counter() - start_time, "path_length": 0}

    for depth in range(max_depth+1):
        if logger:
            logger.log(f"Bắt đầu với độ sâu thứ {depth}")
        
        result = _dls(problem, start, depth, nodes_counter, logger, path_set={start})
        
        
        if result is not None:
            end_time = time.perf_counter()
            if logger:
                logger.log(f"SUCCESS! Tìm thấy đường đi ở độ sâu thứ {depth}.")
            return {
                "path": result,
                "nodes_expanded": nodes_counter[0],
                "time_taken": end_time - start_time,
                "path_length": len(result)
            }
            
    
    return {"path": None, "nodes_expanded": nodes_counter[0], "time_taken": end_time - start_time}



def _dls(problem, state, limit, nodes_counter, logger ,path_set):
    nodes_counter[0] += 1
    
    if logger:
        logger.log(f"  Depth {limit}: Visiting {state}")
    
    if problem.is_goal_state(state):
        if logger:
             logger.log(f"    -> Cutoff at {state}")
        return []

    if limit == 0:
        if logger:
             logger.log(f"    -> Cutoff at {state}")
        return None

    for next_state, action, _ in problem.get_move(state):
        if next_state in path_set:
            continue
        path_set.add(next_state)
        subpath = _dls(problem, next_state, limit-1, nodes_counter, logger, path_set)
        path_set.remove(next_state)
        if subpath is not None:
            return [action] + subpath
    return None