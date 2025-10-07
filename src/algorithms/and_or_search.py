import time


def AND_OR_Search(problem, logger=None):
    """
    Kế hoạch AND-OR cho môi trường xác định, dùng get_move(state).
    """
    start_time = time.perf_counter()

    # Bộ nhớ đệm nước đi để tránh tính lại
    successor_cache = {}
    nodes_expanded = 0
    step_counter = 0

    def actions(state):
        # Lấy danh sách hành động từ get_move
        if state not in successor_cache:
            successor_cache[state] = problem.get_move(state)
        return [a for _, a, _ in successor_cache[state]]

    def results(state, action):
        # Trả về tập trạng thái kế; ở đây là 1 phần tử
        if state not in successor_cache:
            successor_cache[state] = problem.get_move(state)
        for nxt, a, _ in successor_cache[state]:
            if a == action:
                return [nxt]
        return []

    def or_search(state, path):
        nonlocal nodes_expanded, step_counter
        step_counter += 1
        nodes_expanded += 1
        if logger:
            logger.log(
                f"Bước {step_counter}: State=({state[0]}, {state[1]})"
            )
        if problem.is_goal_state(state):
            if logger:
                logger.log("-> Tới đích: trả kế hoạch rỗng")
            return []
        if state in path:
            if logger:
                logger.log("-> Vòng lặp: thất bại")
            return None
        for action in actions(state):
            if logger:
                logger.log(f"-> Thử hành động {action}")
            next_states = results(state, action)
            plan = and_search(next_states, path | {state})
            if plan is not None:
                return [action] + plan
        return None

    def and_search(states, path):
        overall_plan = []
        for s in states:
            plan_i = or_search(s, path)
            if plan_i is None:
                return None
            # Trường hợp xác định: các nhánh giống nhau; chọn kế hoạch dài nhất
            if len(plan_i) > len(overall_plan):
                overall_plan = plan_i
        return overall_plan

    if logger:
        logger.log("Bắt đầu AND-OR search")

    init_state = problem.get_init_state()
    plan = or_search(init_state, set())

    end_time = time.perf_counter()
    return {
        "path": plan,
        "nodes_expanded": nodes_expanded,
        "time_taken": end_time - start_time,
        "path_length": len(plan) if plan else 0,
    }



