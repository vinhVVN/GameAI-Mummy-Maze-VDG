import heapq

def AStar(problem):
    start = problem.get_init_state()
    frontier = [(problem.heuristic(start), 0, start)]  
    # (f = g + h, g, state)

    visited = set()
    paths = {start: None}
    costs = {start: 0}

    while frontier:
        f_cost, g_cost, cur_state = heapq.heappop(frontier)

        if cur_state in visited:
            continue
        visited.add(cur_state)

        if problem.is_goal_state(cur_state):
            # reconstruct path
            path = []
            state = cur_state
            while paths[state]:
                prev_state, action = paths[state]
                path.insert(0, action)
                state = prev_state
            return path

        for next_state, action, move_cost in problem.get_move(cur_state):
            new_g = g_cost + move_cost
            new_f = new_g + problem.heuristic(next_state)

            if next_state not in costs or new_g < costs[next_state]:
                costs[next_state] = new_g
                heapq.heappush(frontier, (new_f, new_g, next_state))
                paths[next_state] = (cur_state, action)

    return None
