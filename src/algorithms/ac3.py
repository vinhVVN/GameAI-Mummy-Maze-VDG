from collections import deque
import time


class CSP:
    """Constraint Satisfaction Problem"""
    def __init__(self, variables, domains, neighbors, constraint_func):
        self.variables = variables
        self.domains = domains  # var -> tập giá trị
        self.neighbors = neighbors  # var -> các biến kề
        self.constraint = constraint_func  # (Xi, x, Xj, y) -> bool


def REVISE(csp, Xi, Xj, logger=None):
    """Xóa các giá trị không consistent từ domain của Xi"""
    revised = False
    to_remove = set()
    
    for x in csp.domains[Xi]:
        satisfies = False
        for y in csp.domains[Xj]:
            if csp.constraint(Xi, x, Xj, y):
                satisfies = True
                break
        if not satisfies:
            to_remove.add(x)
    
    if to_remove:
        csp.domains[Xi] -= to_remove
        revised = True
        if logger:
            removed_list = ", ".join(str(v) for v in sorted(to_remove))
            logger.log(f"AC3: Xóa khỏi D[{Xi}] -> {removed_list}")
    
    return revised


def AC3(csp, logger=None):
    """Thuật toán AC-3 để kiểm tra arc consistency"""
    start_time = time.perf_counter()
    queue = deque()
    
    # Khởi tạo queue với tất cả arcs
    for Xi in csp.variables:
        for Xj in csp.neighbors.get(Xi, []):
            queue.append((Xi, Xj))

    steps = 0
    while queue:
        Xi, Xj = queue.popleft()
        steps += 1
        
        if REVISE(csp, Xi, Xj, logger=logger):
            if logger:
                logger.log(f"AC3: REVISE({Xi}, {Xj}) -> cắt, |D[{Xi}]|={len(csp.domains[Xi])}")
            
            # Nếu domain rỗng -> inconsistent
            if len(csp.domains[Xi]) == 0:
                end_time = time.perf_counter()
                return {"consistent": False, "steps": steps, "time_taken": end_time - start_time}
            
            # Thêm các arcs mới vào queue
            for Xk in csp.neighbors.get(Xi, []):
                if Xk != Xj:
                    queue.append((Xk, Xi))

    end_time = time.perf_counter()
    return {"consistent": True, "steps": steps, "time_taken": end_time - start_time}

# CSP FUNCTIONS

def build_path_csp_timeexpanded(maze, start_pos, goal_pos, horizon_steps):
    """Xây dựng CSP cho bài toán tìm đường đi với time-expanded variables"""
    variables = [("X", t) for t in range(horizon_steps + 1)]
    domains = {}
    neighbors = {var: [] for var in variables}

    # Tìm tất cả các ô có thể đi được
    passable_cells = _get_passable_cells(maze)
    
    # Thiết lập domains cho từng biến thời gian
    for t in range(horizon_steps + 1):
        var = ("X", t)
        if t == 0:
            domains[var] = {start_pos}  # Bắt đầu từ start
        elif t == horizon_steps:
            domains[var] = {goal_pos}   # Kết thúc tại goal
        else:
            domains[var] = set(passable_cells)  # Có thể ở bất kỳ ô nào

    # Thiết lập neighbors (các biến liên tiếp)
    for t in range(horizon_steps + 1):
        if t - 1 >= 0:
            neighbors[("X", t)].append(("X", t - 1))
        if t + 1 <= horizon_steps:
            neighbors[("X", t)].append(("X", t + 1))

    return CSP(variables, domains, neighbors, _consecutive_constraint(maze))


def _get_passable_cells(maze):
    """Lấy danh sách các ô có thể đi được trong maze"""
    passable_cells = []
    h = len(maze.map_data)
    w = len(maze.map_data[0]) if h > 0 else 0
    
    for r in range(1, h, 2):
        for c in range(1, w, 2):
            if maze.is_passable(c, r):
                passable_cells.append((c, r))
    
    return passable_cells


def _consecutive_constraint(maze):
    """Tạo constraint function cho các bước đi liên tiếp"""
    def consecutive_constraint(Xi, x, Xj, y):
        # Chỉ áp dụng cho biến X
        if Xi[0] != "X" or Xj[0] != "X":
            return True
        
        # Lấy thời điểm
        ti, tj = Xi[1], Xj[1]
        
        # Chỉ áp dụng cho thời điểm liên tiếp
        if abs(ti - tj) != 1:
            return True
            
        cx, cy = x
        nx, ny = y
        dx, dy = nx - cx, ny - cy
        
        # Đứng yên
        if dx == 0 and dy == 0:
            return True
            
        # Di chuyển 1 bước (2 đơn vị theo 1 hướng)
        if (abs(dx) == 2 and dy == 0) or (dx == 0 and abs(dy) == 2):
            # Kiểm tra tường ở giữa
            mx, my = cx + dx // 2, cy + dy // 2
            return maze.is_passable(mx, my)
        
        return False

    return consecutive_constraint

# BACKTRACKING FUNCTIONS

def backtracking_on_filtered_domains(csp, assignment, logger=None):
    """Backtracking search trên miền đã được AC-3 lọc"""
    if len(assignment) == len(csp.variables):
        return assignment
    
    # Chọn biến chưa được gán
    unassigned_vars = [var for var in csp.variables if var not in assignment]
    if not unassigned_vars:
        return assignment
    
    var = unassigned_vars[0]
    
    # Thử từng giá trị trong domain đã được lọc
    for value in list(csp.domains[var]):
        if _is_consistent(csp, var, value, assignment):
            # Gán giá trị
            assignment[var] = value
            
            if logger and len(assignment) < 10:
                logger.log(f"Gán {var} = {value}")
            
            # Tiếp tục backtracking
            result = backtracking_on_filtered_domains(csp, assignment, logger)
            if result is not None:
                return result
            
            # Quay lui
            if logger and len(assignment) < 10:
                logger.log(f"Quay lui từ {var} = {value}")
            del assignment[var]
    
    return None


def backtracking_with_shortest_path_priority(csp, assignment, goal_pos, logger=None):
    """Backtracking với ưu tiên đường đi ngắn nhất"""
    if len(assignment) == len(csp.variables):
        return assignment
    
    # Chọn biến chưa được gán
    unassigned_vars = [var for var in csp.variables if var not in assignment]
    if not unassigned_vars:
        return assignment
    
    var = unassigned_vars[0]
    
    # Sắp xếp values theo khoảng cách đến goal (ưu tiên gần goal hơn)
    values = list(csp.domains[var])
    values.sort(key=lambda pos: abs(pos[0] - goal_pos[0]) + abs(pos[1] - goal_pos[1]))
    
    for value in values:
        if _is_consistent(csp, var, value, assignment):
            # Gán giá trị
            assignment[var] = value
            
            # Tiếp tục backtracking
            result = backtracking_with_shortest_path_priority(csp, assignment, goal_pos, logger)
            if result is not None:
                return result
            
            # Quay lui
            del assignment[var]
    
    return None


def _is_consistent(csp, var, value, assignment):
    """Kiểm tra consistency của một giá trị với assignment hiện tại"""
    for neighbor in csp.neighbors.get(var, []):
        if neighbor in assignment:
            if not csp.constraint(var, value, neighbor, assignment[neighbor]):
                return False
    return True


# MAIN ALGORITHM: AC-3 + BACKTRACKING

def AC3_with_backtracking(maze, start_pos, goal_pos, horizon_steps, logger=None):
    """
    AC-3 kết hợp backtracking: AC-3 trước để lọc miền, sau đó backtracking
    Tối ưu để tìm đường đi ngắn nhất
    """
    start_time = time.perf_counter()
    
    # Thử với horizon ngắn hơn trước để tìm đường đi ngắn nhất
    for horizon in range(max(1, horizon_steps // 2), horizon_steps + 1, 2):
        if logger:
            logger.log(f"Thử horizon = {horizon}")
        
        result = _try_solve_with_horizon(maze, start_pos, goal_pos, horizon, logger)
        if result is not None:
            end_time = time.perf_counter()
            result["time_taken"] = end_time - start_time
            return result
    
    # Nếu không tìm thấy với horizon ngắn, thử horizon gốc
    if logger:
        logger.log(f"Không tìm thấy với horizon ngắn, thử horizon gốc = {horizon_steps}")
    
    result = _try_solve_with_horizon(maze, start_pos, goal_pos, horizon_steps, logger)
    if result is not None:
        end_time = time.perf_counter()
        result["time_taken"] = end_time - start_time
        return result
    
    return {"path": None, "nodes_expanded": 0, "time_taken": time.perf_counter() - start_time, "path_length": 0}


def _try_solve_with_horizon(maze, start_pos, goal_pos, horizon, logger):
    """Thử giải với một horizon cụ thể"""
    # Xây dựng CSP
    csp = build_path_csp_timeexpanded(maze, start_pos, goal_pos, horizon)
    
    # BƯỚC 1: Chạy AC-3 để lọc miền giá trị
    ac3_result = AC3(csp, logger)
    if not ac3_result["consistent"]:
        if logger:
            logger.log(f"AC-3 với horizon {horizon}: Không consistent")
        return None
    
    if logger:
        logger.log(f"AC-3 với horizon {horizon}: Miền đã được lọc")
    
    # BƯỚC 2: Backtracking với ưu tiên đường đi ngắn
    assignment = {("X", 0): start_pos}
    result = backtracking_with_shortest_path_priority(csp, assignment, goal_pos, logger)
    
    if result is not None:
        # Chuyển đổi assignment thành path
        path = _assignment_to_path(result, goal_pos, horizon)
        if logger:
            logger.log(f"Tìm thấy solution với horizon {horizon}, path length = {len(path)}")
        return {"path": path, "nodes_expanded": ac3_result["steps"], "path_length": len(path)}
    
    return None


# UTILITY FUNCTIONS

def _assignment_to_path(assignment, goal_pos, horizon):
    """Chuyển đổi assignment thành danh sách actions"""
    path = []
    for t in range(horizon):
        if ("X", t) in assignment and ("X", t+1) in assignment:
            current = assignment[("X", t)]
            next_pos = assignment[("X", t+1)]
            
            action = _get_action_from_move(current, next_pos)
            if action:
                path.append(action)
            
            # Dừng sớm nếu đã đến goal
            if next_pos == goal_pos:
                break
    
    return path


def _get_action_from_move(current, next_pos):
    """Chuyển đổi di chuyển thành action"""
    dx = next_pos[0] - current[0]
    dy = next_pos[1] - current[1]
    
    if dx == 0 and dy == -2:
        return "UP"
    elif dx == 0 and dy == 2:
        return "DOWN"
    elif dx == -2 and dy == 0:
        return "LEFT"
    elif dx == 2 and dy == 0:
        return "RIGHT"
    else:
        return None  # Đứng yên hoặc di chuyển không hợp lệ




