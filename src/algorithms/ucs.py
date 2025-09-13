import heapq

def UCS(problem):
    frontier = [(0, problem.get_init_state())]
    
    visited = set()
    paths = {problem.get_init_state() : None}
    costs = {problem.get_init_state() : 0}
    
    while frontier:
        cost, cur_state = heapq.heappop(frontier)
        
        if cur_state in visited:
            continue
        visited.add(cur_state)
        
        if problem.is_goal_state(cur_state):
            path = []
            state = cur_state
            while paths[state]:
                prev, action = paths[state]
                path.insert(0, action)
                state = prev
            return path
        
        for next_state, action, move_cost in problem.get_move(cur_state):
            new_cost = costs[cur_state] + move_cost
            
            if next_state not in costs or new_cost < costs[next_state]:
                costs[next_state] = new_cost
                heapq.heappush(frontier, (new_cost, next_state))
                paths[next_state] = (cur_state, action)
    
    return None
             
                
    