
class MazeProblem2:
    def __init__(self, maze, start_state, goal_pos):
        self.maze = maze
        # start_state bao gồm ((player_x, player_y), (mummy_x, mummy_y))
        self.start_state = start_state
        self.goal_pos = goal_pos
        self.FEAR_FACTOR = 500

        
        
    def get_init_state(self):
        return self.start_state
    
    def is_goal_state(self, state):
        player_pos, mummy_pos = state
        return player_pos == self.goal_pos
    
    def get_move(self, state):
        moves = []
        player_pos, mummy_pos = state
        
        # Các hành động có thể của Player
        possible_actions = [(0, -2, "UP"), (0, 2, "DOWN"), (-2, 0, "LEFT"), (2, 0, "RIGHT")]

        for dx, dy, action in possible_actions:
            px, py = player_pos
            wall_x = px + dx // 2
            wall_y = py + dy // 2
            
            if self.maze.is_passable(wall_x, wall_y):
                # Player thực hiện bước đi giả định
                new_player_pos = (px + dx, py + dy)
                
                # Tính toán vị trí cuối cùng của mummy sau lượt đi của nó
                mx, my = mummy_pos
                
                new_mummy_pos = (mx, my)

                next_state = (new_player_pos, new_mummy_pos)
                
                dist_to_mummy = abs(new_player_pos[0] - new_mummy_pos[0]) + abs(new_player_pos[1] - new_mummy_pos[1])
                cost = 1 + (self.FEAR_FACTOR / (dist_to_mummy + 0.1))
                
                # Nếu bước đi này dẫn đến thua, đặt chi phí cực lớn
                if new_player_pos == new_mummy_pos:
                    cost = float('inf')
                
                moves.append((next_state, action, cost))
        
        return moves
    
    def heuristic(self, state): 
        player_pos, mummy_pos = state
        # chi phí dựa trên khoảng cách của Player tới cầu thang
        return abs(player_pos[0] - self.goal_pos[0]) + abs(player_pos[1] - self.goal_pos[1])