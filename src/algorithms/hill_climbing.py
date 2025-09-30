def HillClimbing(problem):
    current = problem.get_init_state()
    if problem.is_goal_state(current):
        return []

    paths = {current: None}

    while True:
        neighbors = problem.get_move(current)  # [(next_state, action, cost), ...]

        if not neighbors:
            return None  # không có bước đi nào

        # chọn neighbor tốt nhất (theo heuristic nhỏ nhất)
        next_state, action, _ = min(
            neighbors, key=lambda x: problem.heuristic(x[0])
        )

        # nếu next_state không tốt hơn current → dừng lại
        if problem.heuristic(next_state) >= problem.heuristic(current):
            return None  # local optimum

        # cập nhật path
        if next_state not in paths:
            paths[next_state] = (current, action)

        # move sang state mới
        current = next_state

        # kiểm tra goal
        if problem.is_goal_state(current):
            path = []
            cur = current
            while paths[cur] is not None:
                prev, action = paths[cur]
                path.insert(0, action)
                cur = prev
            return path
