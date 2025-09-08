

class MazeProblem:
    def __init__(self, maze, start_pos, goal_pos):
        self.maze = maze
        self.start_pos = start_pos
        self.goal_pos = goal_pos
        
    def get_init_state(self):
        return self.start_pos
    
    def is_goal_state(self, state):
        return state == self.goal_pos
    
    def get_move(self, state):
        moves = []
        px, py = state
        actions = [(0, -2, "UP"), (0, 2, "DOWN"), (2, 0, "RIGHT"), (-2, 0, "LEFT")]
        for dx, dy, action in actions:
            wall_x = px + dx//2
            wall_y = py + dy//2
            
            if self.maze.is_passable(wall_x, wall_y):
                next_state = (px+dx, py+dy)
                moves.append((next_state, action))
        
        return moves
    
    