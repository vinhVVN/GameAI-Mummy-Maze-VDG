from collections import deque
import time

def BFS(problem,logger=None):
    start_time = time.perf_counter()
    
    queue = deque([problem.get_init_state()])
    visited = {problem.get_init_state()}
    paths = {problem.get_init_state() : None}
    iteration = 0
    while queue:
        iteration += 1
        cur_state = queue.popleft()
        
        if logger:
            logger.log(f"Bước {iteration}: cur state= {cur_state}")
        
        if problem.is_goal_state(cur_state):
            print("Tìm được đường đi!")
            state = cur_state
            path = []
            while paths[state] is not None:
                prev_state, action = paths[state]
                path.insert(0, action)
                state = prev_state
            print(path)
            if logger:
                logger.log(f"SUCCESS! Tìm thấy đường đi sau {iteration} bước")
            return {"path": path, "nodes_expanded": iteration, "time_taken": time.perf_counter() - start_time, "path_length": len(path)}
        
        for next_state, action,_ in problem.get_move(cur_state):
            if next_state not in visited:
                visited.add(next_state)
                paths[next_state] = (cur_state, action)
                queue.append(next_state)
                if logger:
                    logger.log(f"-> Check neighbor {next_state}, {action}")
                
    print("Hết cứu")
    return None

                