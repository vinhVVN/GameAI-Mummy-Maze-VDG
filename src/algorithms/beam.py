import heapq
import time

def Beam(problem, beam_width=3, logger = None):
    start_time = time.perf_counter()
    nodes_counter = 0
    
    start = problem.get_init_state()
    start_h = problem.heuristic(start)
    
    if logger:
        logger.log(f"Bắt đầu với beam_width = {beam_width}")
        logger.log(f"Trạng thái ban đầu: {start}, h={start_h:.1f}")
    
    if problem.is_goal_state(start):
        return []

    frontier = [(start_h, start)]
    paths = {start: None}
    visited = set()
    iteration = 0
    while frontier:
        iteration += 1
        # Giữ lại beam_width trạng thái tốt nhất
        candidates = []
        
        if logger:
            logger.log(f"Bước {iteration}: Mở rộng {len(frontier)} trạng thái")
            for h, s in frontier:
                logger.log(f"  - State: {s}, h={h:.1f}")
            
        
        for _ in range(min(beam_width, len(frontier))):
            h, state = heapq.heappop(frontier)
            nodes_counter += 1
            
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
                return {
                    "path": path, "nodes_expanded": nodes_counter, 
                    "time_taken": time.perf_counter() - start_time, "path_length": len(path)
                }

            for next_state, action, _ in problem.get_move(state):
                if next_state not in visited:
                    heapq.heappush(candidates, (problem.heuristic(next_state), next_state))
                    if next_state not in paths:
                        paths[next_state] = (state, action)

        # chỉ giữ lại beam_width ứng viên tốt nhất cho vòng sau
        if logger:
            logger.log(f"  -> Chọn ra {beam_width} trạng thái tốt nhất trong {len(candidates)} trạng thái")
        frontier = heapq.nsmallest(beam_width, candidates)

        if logger:
            for h, s in frontier:
                logger.log(f"    - State: {s}, h={h:.1f}")
            
        
    return {"path": None, "nodes_expanded": nodes_counter, "time_taken": time.perf_counter() - start_time}
