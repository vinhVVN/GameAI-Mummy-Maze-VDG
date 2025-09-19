import heapq

def Greedy(problem):
    start = problem.get_init_state()
    frontier = [(problem.heuristic(start), start)]
    visited = set()
    paths = {start : None}

    while frontier:
        cost, cur_state = heapq.heappop(frontier)

        if cur_state in visited:
            continue
        visited.add(cur_state)

        if problem.is_goal_state(cur_state):
            path = []
            state = cur_state
            while paths[state]:
                prev_state, action = paths[state]
                path.insert(0, action)
                state = prev_state
            return path

        for next_state, action, _ in problem.get_move(cur_state):
            if next_state in visited:
                continue

            h_cost = problem.heuristic(next_state)
            heapq.heappush(frontier, (h_cost, next_state))
            if next_state not in paths:
                paths[next_state] = (cur_state, action)

    return None




