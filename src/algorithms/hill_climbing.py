import time

def HillClimbing(problem, logger = None):
    start_time = time.perf_counter()
    current = problem.get_init_state()
    if problem.is_goal_state(current):
        return []

    paths = {current: None}
    iteration = 0
    while True:
        neighbors = problem.get_move(current)  # [(next_state, action, cost), ...]
        iteration += 1
        if not neighbors:
            end_time = time.perf_counter()
            return {"path":None, "nodes_expanded":iteration,
                "time_taken": end_time-start_time, "path_length": len(paths)}  # không có bước đi nào

        # chọn neighbor tốt nhất (theo heuristic nhỏ nhất)
        next_state, action, _ = min(
            neighbors, key=lambda x: problem.heuristic(x[0])
        )

        # nếu next_state không tốt hơn current → dừng lại
        if problem.heuristic(next_state) >= problem.heuristic(current):
            end_time = time.perf_counter()
            return {"path":None, "nodes_expanded":iteration,
                "time_taken": end_time-start_time, "path_length": len(paths)}  # local optimum

        # cập nhật path
        if next_state not in paths:
            paths[next_state] = (current, action)

        # move sang state mới
        current = next_state

        # kiểm tra goal
        if problem.is_goal_state(current):
            end_time = time.perf_counter()
            path = []
            cur = current
            while paths[cur] is not None:
                prev, action = paths[cur]
                path.insert(0, action)
                cur = prev
            return {"path":path, "nodes_expanded":iteration,
                "time_taken": end_time-start_time, "path_length": len(path)}
