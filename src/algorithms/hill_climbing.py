import time

def HillClimbing(problem, logger=None):
    start_time = time.perf_counter()
    current = problem.get_init_state()

    if problem.is_goal_state(current):
        if logger:
            logger.log("Trạng thái ban đầu đã là goal!")
        return {"path": [], "nodes_expanded": 0, "time_taken": 0, "path_length": 0}

    paths = {current: None}
    iteration = 0

    while True:
        iteration += 1
        if logger:
            logger.log(f"Bước {iteration}: current = {current}, h = {problem.heuristic(current)}")

        neighbors = problem.get_move(current)  # [(next_state, action, cost), ...]

        if not neighbors:
            if logger:
                logger.log(f"Không có neighbor nào — dừng lại tại {current}")
            break  # kết thúc vòng lặp, trả về đường đi đã có

        # chọn neighbor có heuristic nhỏ nhất
        next_state, action, _ = min(neighbors, key=lambda x: problem.heuristic(x[0]))

        if logger:
            logger.log(f"-> Chọn neighbor {next_state}, action={action}, h={problem.heuristic(next_state)}")

        # nếu không cải thiện → dừng (local optimum)
        if problem.heuristic(next_state) >= problem.heuristic(current):
            if logger:
                logger.log("Heuristic không giảm — local optimum!")
            break

        # lưu đường đi
        paths[next_state] = (current, action)
        current = next_state

        # kiểm tra goal
        if problem.is_goal_state(current):
            if logger:
                logger.log(f"SUCCESS! Đạt goal tại {current} sau {iteration} bước.")
            break

    # ---- tái tạo đường đi đã leo được ----
    end_time = time.perf_counter()
    path = []
    cur = current
    while paths[cur] is not None:
        prev, act = paths[cur]
        path.insert(0, act)
        cur = prev

    if logger:
        logger.log(f"Đường đi đạt được ({len(path)} bước): {path}")

    print("Đường đi đạt được:")
    print("→".join(map(str, path)))

    # trả về kết quả dù không đạt goal
    return {
        "path": path,
        "nodes_expanded": iteration,
        "time_taken": end_time - start_time,
        "path_length": len(path)
    }