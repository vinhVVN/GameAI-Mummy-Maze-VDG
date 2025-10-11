import time
from src.mazeproblem import CSPMazeProblem



def backtracking_RECURSIVE(assignment, problem, logger, nodes_counter):
    nodes_counter[0] += 1
    
    # if len(assignment) == len(problem.variables): # nếu đã gán xong tất cả các biến
    if assignment[f"X_{len(assignment) - 1}"] == problem.goal_pos:
        return assignment
    
    
    var = f"X_{len(assignment)}"
    for value in problem.domain[var]:
        
        if logger and nodes_counter[0] % 10 == 0:
            logger.log(f"Với {var} = {value}")
        
        if problem.consistent(var, value, assignment):
            assignment[var] = value
            
            if logger and len(assignment) < 10:
                logger.log(f"{' '*len(assignment)} Gán {var} = {value} (Thoả)")
            
            result = backtracking_RECURSIVE(assignment, problem, logger, nodes_counter)
            if result is not None:
                return result
            
            if logger and len(assignment) < 10:
                logger.log(f"{' '*len(assignment)} Quay lui từ {var} = {value}")
            del assignment[var] # quay lui
            
    return None

def Backtracking(maze, start_pos, goal_pos, logger = None):
    start_time = time.perf_counter()
    nodes_counter = [0]
        
    k = 40
    problem = CSPMazeProblem(maze, start_pos, goal_pos, path_length = k)
    assignment = {f"X_0": start_pos}
    result = backtracking_RECURSIVE(assignment, problem, logger, nodes_counter)
    if result:
        end_time = time.perf_counter()
        path = []
        for i in range(len(assignment)-1):
            pos1 = result[f"X_{i}"]
            pos2 = result[f"X_{i+1}"]
            dx, dy = pos2[0] - pos1[0], pos2[1] - pos1[1]
            if dy == -2:
                path.append("UP")
            elif dy == 2:
                path.append("DOWN")
            elif dx == -2:
                path.append("LEFT")
            elif dx == 2:
                path.append("RIGHT")
            
        if logger:
            logger.log(f"SUCCESS! Tìm được đường đi")
        return {"path":path, "nodes_expanded":nodes_counter[0],
                "time_taken": end_time-start_time, "path_length": len(path)}
            
    end_time = time.perf_counter()
    return {"path": None, "nodes_expanded": nodes_counter[0],
            "time_taken": end_time - start_time, "path_length": k}