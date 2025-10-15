import time

def HillClimbing(problem, logger=None):
    start_time = time.perf_counter()
    current = problem.get_init_state()

    # Nếu trạng thái ban đầu đã là goal
    if problem.is_goal_state(current):
        if logger:
            logger.log("Trạng thái ban đầu đã là goal!")
        return {
            "path": [],
            "nodes_expanded": 0,
            "time_taken": 0,
            "path_length": 0
        }

    paths = {current: None}
    iteration = 0

    while True:
        iteration += 1
        if logger:
            logger.log(f"Bước {iteration}: current = {current}, h = {problem.heuristic(current)}")

        # Lấy danh sách neighbor [(next_state, action, cost), ...]
        neighbors = problem.get_move(current)

        if not neighbors:
            if logger:
                logger.log(f"Không có neighbor nào — dừng lại tại {current}")
            break  # hết đường leo

        # chọn neighbor tốt nhất theo heuristic nhỏ nhất
        next_state, action, _ = min(neighbors, key=lambda x: problem.heuristic(x[0]))

        if logger:
            logger.log(f"-> Chọn neighbor {next_state}, action={action}, h={problem.heuristic(next_state)}")

        # nếu neighbor không tốt hơn (heuristic không giảm) → local optimum
        if problem.heuristic(next_state) >= problem.heuristic(current):
            if logger:
                logger.log("Heuristic không giảm — local optimum!")
            break

        # cập nhật đường đi
        paths[next_state] = (current, action)
        current = next_state

        # kiểm tra goal
        if problem.is_goal_state(current):
            if logger:
                logger.log(f"SUCCESS! Đạt goal tại {current} sau {iteration} bước.")
            break

    # ---- tái tạo đường đi ----
    end_time = time.perf_counter()
    path = []
    cur = current
    while paths[cur] is not None:
        prev, act = paths[cur]
        path.insert(0, act)
        cur = prev

    # Log kết quả
    if logger:
        if problem.is_goal_state(current):
            logger.log(f"Đạt goal! Đường đi ({len(path)} bước): {path}")
        else:
            logger.log(f"Dừng tại local optimum sau {iteration} bước. Đường đi tạm thời ({len(path)} bước): {path}")

    # In ra nếu cần
    print("Đường đi đạt được:")
    print(" → ".join(map(str, path)) if path else "(Trống)")

    # ---- trả về kết quả ----
    return {
        "path": path,  #  Luôn trả lại đường đi dù chưa tới goal
        "nodes_expanded": iteration,
        "time_taken": end_time - start_time,
        "path_length": len(path),
        "reached_goal": problem.is_goal_state(current)
    }
