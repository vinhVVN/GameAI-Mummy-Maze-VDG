from collections import deque
import time


class CSP:
    def __init__(self, variables, domains, neighbors, constraint_func):
        self.variables = variables
        self.domains = domains  # var -> tập giá trị
        self.neighbors = neighbors  # var -> các biến kề
        self.constraint = constraint_func  # (Xi, x, Xj, y) -> bool


def REVISE(csp, Xi, Xj, logger=None):
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
    start_time = time.perf_counter()
    queue = deque()
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
            if len(csp.domains[Xi]) == 0:
                end_time = time.perf_counter()
                return {"consistent": False, "steps": steps, "time_taken": end_time - start_time}
            for Xk in csp.neighbors.get(Xi, []):
                if Xk != Xj:
                    queue.append((Xk, Xi))

    end_time = time.perf_counter()
    return {"consistent": True, "steps": steps, "time_taken": end_time - start_time}

def build_path_csp_timeexpanded(maze, start_pos, goal_pos, horizon_steps):
    # Biến theo thời gian: ("X", t)
    variables = [("X", t) for t in range(horizon_steps + 1)]
    domains = {}
    neighbors = {var: [] for var in variables}

    # Miền: các ô đi được; X0=start, XT=goal
    passable_cells = []
    h = len(maze.map_data)
    w = len(maze.map_data[0]) if h > 0 else 0
    for r in range(1, h, 2):
        for c in range(1, w, 2):
            if maze.is_passable(c, r):
                passable_cells.append((c, r))

    for t in range(horizon_steps + 1):
        var = ("X", t)
        if t == 0:
            domains[var] = {start_pos}
        elif t == horizon_steps:
            domains[var] = {goal_pos}
        else:
            domains[var] = set(passable_cells)

    # Láng giềng: Xt nối Xt-1 và Xt+1
    for t in range(horizon_steps + 1):
        if t - 1 >= 0:
            neighbors[("X", t)].append(("X", t - 1))
        if t + 1 <= horizon_steps:
            neighbors[("X", t)].append(("X", t + 1))

    def consecutive_constraint(Xi, x, Xj, y):
        # Hai thời điểm liên tiếp: đứng yên hoặc đi 1 bước hợp lệ (dịch 2 đơn vị)
        if Xi[0] != "X" or Xj[0] != "X":
            return True
        cx, cy = x
        nx, ny = y
        dx = abs(cx - nx)
        dy = abs(cy - ny)
        if dx == 0 and dy == 0:
            return True
        if (dx == 2 and dy == 0) or (dx == 0 and dy == 2):
            # Ô giữa phải đi được
            mx = (cx + nx) // 2
            my = (cy + ny) // 2
            return maze.is_passable(mx, my)
        return False

    return CSP(variables, domains, neighbors, consecutive_constraint)


