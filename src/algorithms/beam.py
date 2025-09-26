import heapq

def Beam(problem, beam_width=3):
    start = problem.get_init_state()
    if problem.is_goal_state(start):
        return []

    frontier = [(problem.heuristic(start), start)]
    paths = {start: None}
    visited = set()

    while frontier:
        # Giữ lại beam_width trạng thái tốt nhất
        candidates = []
        for _ in range(min(beam_width, len(frontier))):
            h, state = heapq.heappop(frontier)

            if state in visited:
                continue
            visited.add(state)

            if problem.is_goal_state(state):
                path = []
                cur = state
                while paths[cur] is not None:
                    prev, action = paths[cur]
                    path.insert(0, action)
                    cur = prev
                return path

            for next_state, action, _ in problem.get_move(state):
                if next_state not in visited:
                    heapq.heappush(candidates, (problem.heuristic(next_state), next_state))
                    if next_state not in paths:
                        paths[next_state] = (state, action)

        # chỉ giữ lại beam_width ứng viên tốt nhất cho vòng sau
        frontier = heapq.nsmallest(beam_width, candidates)

    return None
