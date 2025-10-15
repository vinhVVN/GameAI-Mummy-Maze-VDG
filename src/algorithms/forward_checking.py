import time
from copy import deepcopy
from src.mazeproblem import CSPMazeProblem


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def forward_checking_RECURSIVE(assignment, problem, logger, nodes_counter):
    nodes_counter[0] += 1

    last_var = f"X_{len(assignment) - 1}"
    if assignment[last_var] == problem.goal_pos:
        return assignment

    if len(assignment) >= len(problem.variables):
        return None

    # --- MRV chọn biến có domain nhỏ nhất ---
    unassigned_vars = [v for v in problem.variables if v not in assignment]
    if not unassigned_vars:
        return None
    var = min(unassigned_vars, key=lambda v: len(problem.domain[v]))

    goal = problem.goal_pos
    sorted_values = sorted(
        problem.domain[var],
        key=lambda val: manhattan(val, goal)
    )

    for value in sorted_values:
        # --- Tránh quay lại ô cũ ---
        if value in assignment.values():
            continue

        # --- Cắt tỉa: nếu không thể tới goal trong số bước còn lại ---
        remaining_steps = len(problem.variables) - len(assignment)
        if manhattan(value, goal) > remaining_steps * 2:
            continue

        if problem.consistent(var, value, assignment):
            assignment[var] = value

            # --- Forward Checking cục bộ ---
            changed_domains = {}
            consistent = True
            for v_k in problem.variables:
                if v_k not in assignment:
                    old_domain = problem.domain[v_k]
                    new_domain = [val for val in old_domain if problem.consistent(v_k, val, assignment)]
                    if len(new_domain) < len(old_domain):
                        changed_domains[v_k] = old_domain
                        problem.domain[v_k] = new_domain
                    if not new_domain:
                        consistent = False
                        break

            if consistent:
                result = forward_checking_RECURSIVE(assignment, problem, logger, nodes_counter)
                if result is not None:
                    return result

            # --- Quay lui: khôi phục domain đã thay đổi ---
            for v_k, old_domain in changed_domains.items():
                problem.domain[v_k] = old_domain
            del assignment[var]

    return None


def ForwardChecking(problem, logger=None, min_safe_dist=None, debug=False):
    """
    Forward Checking cho bài toán Maze CSP.
    Tối ưu với MRV + LCV + pruning.
    """
    start_time = time.perf_counter()
    nodes_counter = [0]

    # --- Xác định điểm bắt đầu và kết thúc ---
    start_pos = getattr(problem, "start_pos", None) or getattr(problem, "start_state", None)
    goal_pos = getattr(problem, "goal_pos", None) or getattr(problem, "goal", None)

    if start_pos is None or goal_pos is None:
        raise ValueError("Problem không có start_pos / goal_pos hoặc start_state / goal")

    path_length = getattr(problem, "path_length", 40)

    if not hasattr(problem, "variables"):
        problem = CSPMazeProblem(problem.maze, start_pos, goal_pos, path_length)

    assignment = {f"X_0": problem.start_pos}
    result = forward_checking_RECURSIVE(assignment, problem, logger, nodes_counter)
    end_time = time.perf_counter()

    if result:
        path = []
        for i in range(len(result) - 1):
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
            logger.log(f"✅ SUCCESS! Tìm được đường đi ({len(path)} bước, {nodes_counter[0]} nút mở rộng)")
        return {
            "path": path,
            "nodes_expanded": nodes_counter[0],
            "time_taken": end_time - start_time,
            "path_length": len(path)
        }

    if logger:
        logger.log(f"❌ Không tìm thấy đường đi sau {nodes_counter[0]} nút.")
    return {
        "path": None,
        "nodes_expanded": nodes_counter[0],
        "time_taken": end_time - start_time,
        "path_length": path_length
    }