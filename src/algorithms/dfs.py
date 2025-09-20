from collections import deque

def DFS(problem):
    queue = deque([problem.get_init_state()])
    visited = {problem.get_init_state()}
    paths = {problem.get_init_state() : None}
    
    while queue:
        cur_state = queue.pop()
        
        if problem.is_goal_state(cur_state):
            print("Tìm được đường đi!")
            state = cur_state
            path = []
            while paths[state] is not None:
                prev_state, action = paths[state]
                path.insert(0, action)
                state = prev_state
            print(path)
            return path
        
        for next_state, action,_ in problem.get_move(cur_state):
            if next_state not in visited:
                visited.add(next_state)
                paths[next_state] = (cur_state, action)
                queue.append(next_state)
                
    print("Hết cứu")
    return None

                