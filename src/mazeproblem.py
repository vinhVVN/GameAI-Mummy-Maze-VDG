from src.character import Mummy

class MazeProblem:
    def __init__(self, maze, start_state, goal_pos, trap_pos):
        self.maze = maze
        # start_state bao gồm ((player_x, player_y), (mummy_x, mummy_y))
        self.start_state = start_state
        self.goal_pos = goal_pos
        self.FEAR_FACTOR = 50

        # Tạo một đối tượng Mummy tạm thời để mô phỏng
        self.sim_mummy = Mummy(1, 1, maze.maze_size, maze.cell_size)
        
        self.trap_pos = trap_pos
        
    def get_init_state(self):
        return self.start_state
    
    def is_goal_state(self, state):
        player_pos, mummies_pos = state
        return player_pos == self.goal_pos
    
    def get_move(self, state):
        moves = []
        player_pos, mummies_pos_tuple = state
        mummies_pos = list(mummies_pos_tuple)
        
        # Các hành động có thể của Player
        possible_actions = [(0, -2, "UP"), (0, 2, "DOWN"), (-2, 0, "LEFT"), (2, 0, "RIGHT")]

        for dx, dy, action in possible_actions:
            px, py = player_pos
            wall_x = px + dx // 2
            wall_y = py + dy // 2
            
            if self.maze.is_passable(wall_x, wall_y):
                # Player thực hiện bước đi giả định
                new_player_pos = (px + dx, py + dy)
                
                # Cập nhật vị trí của mummy mô phỏng
                new_mummies_pos = []
                for mummy_pos in mummies_pos:
                    self.sim_mummy.grid_x, self.sim_mummy.grid_y = mummy_pos
                    # Dự đoán các bước đi của mummy
                    mummy_actions = self.sim_mummy.classic_move(new_player_pos, self.maze)
                    
                    # Tính toán vị trí cuối cùng của mummy sau lượt đi của nó
                    mx, my = mummy_pos
                    for m_action in mummy_actions:
                        if m_action == "UP": 
                            my -= 2
                        elif m_action == "DOWN":
                            my += 2
                        elif m_action == "LEFT": 
                            mx -= 2
                        elif m_action == "RIGHT": 
                            mx += 2
                    new_mummies_pos.append((mx,my))

                next_state = (new_player_pos, tuple(sorted(new_mummies_pos)))
                
                min_dist_to_mummy = self.min_dist(new_mummies_pos, new_player_pos)
                
                
                # Nếu bước đi này dẫn đến thua, đặt chi phí lớn
                if min_dist_to_mummy == 0:
                    cost = float(self.FEAR_FACTOR * 5)
                
                elif self.trap_pos and new_player_pos == self.trap_pos:
                    cost = float('inf')
                    
                else:
                    cost = 1 + (self.FEAR_FACTOR / (min_dist_to_mummy + 0.1))
                    
                moves.append((next_state, action, cost))
        
        return moves
    

    def min_dist(self, mummies_pos, player_pos):
        min_dist_to_mummy = float('inf')
        for mummy_pos in mummies_pos: # tính chi phí dựa trên mummy gần nhất
            if player_pos == mummy_pos:
                return 0
            dist = abs(player_pos[0]-mummy_pos[0]) + abs(player_pos[1] - mummy_pos[1])
            if dist < min_dist_to_mummy:
                min_dist_to_mummy = dist
                
        return min_dist_to_mummy
    
    def heuristic(self, state):
        player_pos, mummies_pos = state
        # chi phí dựa trên khoảng cách của Player tới cầu thang
        dist_goal = abs(player_pos[0] - self.goal_pos[0]) + abs(player_pos[1] - self.goal_pos[1])
        # dist_mummy = self.min_dist(mummies_pos, player_pos)

        # fear = self.FEAR_FACTOR / (dist_mummy + 1)  # FEAR_FACTOR là hằng số (ví dụ 50-200)
        return dist_goal

class SimpleMazeProblem:
    def __init__(self, maze, start, goal):
        self.maze = maze
        self.start_state = start
        self.goal = goal

    def get_init_state(self):
        return self.start_state

    def is_goal_state(self, state):
        return state == self.goal

    def get_move(self, state):
        moves = []
        px, py = state
        actions = [(0, -2, "UP"), (0, 2, "DOWN"), (-2, 0, "LEFT"), (2, 0, "RIGHT")]
        for dx, dy, action in actions:
            wall_x = px + dx // 2
            wall_y = py + dy // 2
            if self.maze.is_passable(wall_x, wall_y):
                new_pos = (px + dx, py + dy)
                moves.append((new_pos, action, 0))  # cost = 1
        return moves



class CSPMazeProblem:
    def __init__(self, maze, start_pos, goal_pos, path_length):
        self.maze = maze
        self.start_pos = start_pos
        self.goal_pos = goal_pos
        self.path_length = path_length
        
        self.variables = [f"X_{i}" for i in range(path_length + 1)]
        domain = set()
        for r in range(-1, len(maze.map_data), 2):
            for c in range(-1, len(maze.map_data[0]),2):
                if self.maze.is_passable(c, r):
                    domain.add((c,r))
        self.domain = {var: domain for var in self.variables}
        
    def consistent(self, var, value, assignment):
        if value in assignment.values():
            return False
        
        var_index = int(var.split('_')[1])
        if var_index > 0:
            prev_var = f"X_{var_index - 1}"
            if prev_var in assignment:
                prev_pos = assignment[prev_var]
                px, py = prev_pos
                vx, vy = value
                dx, dy = vx-px, vy-py
                if not (abs(dx)== 2 and dy == 0) and not (abs(dy)==2 and dx==0):
                    return False
                
                wall_x, wall_y = px + dx//2, py + dy//2
                if not self.maze.is_passable(wall_x, wall_y):
                    return False
                
        return True
    
    