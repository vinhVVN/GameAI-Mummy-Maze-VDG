def IDS(problem, max_depth=110):
    start = problem.get_init_state()
    if problem.is_goal_state(start):
        return []

    for depth in range(max_depth+1):
        result = _dls(problem, start, depth, path_set={start})
        if result is not None:
            return result
    return None


def _dls(problem, state, limit, path_set):
    if problem.is_goal_state(state):
        return []

    if limit == 0:
        return None

    for next_state, action, _ in problem.get_move(state):
        if next_state in path_set:
            continue
        path_set.add(next_state)
        subpath = _dls(problem, next_state, limit-1, path_set)
        path_set.remove(next_state)
        if subpath is not None:
            return [action] + subpath
    return None