import pygame
from src.settings import *
from src.maze import *
from src.character import Player, Mummy
from src.ui import Panel , Button
from src.mazeproblem import MazeProblem
from src.algorithms.bfs import BFS

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("MummyGame - Vinh Say Gex")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.maze = Maze("map6_1.txt")
        cell_size = self.maze.cell_size
        self.player = Player(1,1,self.maze.maze_size, cell_size)
        self.mummy = Mummy(3,11, self.maze.maze_size, cell_size)

        self.panel = Panel(MAZE_PANEL_WIDTH, 0, CONTROL_PANEL_WIDTH, SCREEN_HEIGHT)
        self.set_buttons()
        
        self.solution_paths = []
        self.ai_running = False
        
        self.mummy_path = []
        self.mummy_calculate = False
    
    def set_buttons(self):
        btn_w, btn_h = 220, 40
        btn_x = MAZE_PANEL_WIDTH + (CONTROL_PANEL_WIDTH - btn_w) / 2
        
        def player_bfs():
            print("Player bfs")
        def mummy_bfs():
            print("Mummy bfs")
        def change_map():
            print("change map")
        def start_ai():
            self.start_ai_search()
            
        btn_player_algo = Button(btn_x, 100, btn_w, btn_h, "Player: BFS", player_bfs)
        btn_mummy_alogo = Button(btn_x, 150, btn_w, btn_h, "Mummy: BFS", mummy_bfs)
        btn_change_map = Button(btn_x, 250, btn_w, btn_h, "Map6_1", change_map)
        btn_start = Button(btn_x, 350, btn_w, btn_h, "Start", start_ai)
        
        self.panel.add_widget(btn_player_algo)
        self.panel.add_widget(btn_mummy_alogo)
        self.panel.add_widget(btn_change_map)
        self.panel.add_widget(btn_start)
        
    def start_ai_search(self):
        if self.ai_running:
            return
        
        sx, sy = self.maze.stair_pos
        gx, gy = 0, 0
        if self.maze.stair_pos[0] == 0: # LEFT
            gx = 1
            gy = sy
        elif self.maze.stair_pos[0] >= self.maze.maze_size * 2: # RIGHT
            gx = sx - 1
            gy = sy
        elif self.maze.stair_pos[1] >= self.maze.maze_size: # DOWN
            gx = sx
            gy = sy + 1
        else:
            gx = sx
            gy = sy - 1
        
        
        problem = MazeProblem(self.maze, 
                              (self.player.grid_x, self.player.grid_y),
                              (gx, gy))
        path = BFS(problem)
        if path:
            self.solution_paths = path
            self.ai_running = True
        
        
    def run(self): 
        while self.running:
            self.events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        
        
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            self.panel.handle_event(event) # chuyển sự kiện cho panel xử lý
            
            if not self.ai_running and event.type == pygame.KEYDOWN and not self.player.is_moving and not self.mummy.is_moving:
                cell_size = self.maze.cell_size
                moved = False
                if event.key == pygame.K_UP:
                    self.player.move(dy=-2, maze = self.maze, cell_size = cell_size)
                    moved = True
                elif event.key == pygame.K_DOWN:
                    self.player.move(dy = 2, maze=self.maze, cell_size = cell_size)
                    moved = True
                elif event.key == pygame.K_LEFT:
                    self.player.move(dx= -2, maze=self.maze, cell_size = cell_size)
                    moved = True
                elif event.key == pygame.K_RIGHT:
                    self.player.move(dx = 2, maze=self.maze, cell_size = cell_size)
                    moved = True
                
                if moved:
                    self.mummy.is_moving = False
                    self.mummy_calculate = True
                
                
        
    def update(self): 
        if self.ai_running and self.solution_paths and not self.player.is_moving:
            action = self.solution_paths.pop(0)
            dx, dy = 0, 0
            if action == "UP":
                dy = -2
            elif action == "DOWN":
                dy = 2
            elif action == "RIGHT":
                dx = 2
            elif action == "LEFT":
                dx = -2
            pygame.time.delay(1000)
            self.player.move(dx, dy, self.maze, self.maze.cell_size)
        
        if self.ai_running and not self.solution_paths and not self.player.is_moving:
            self.ai_running = False
            print("AI đã chạy xong!")
        
        
        
        if self.mummy_calculate and not self.player.is_moving: 
            problem = MazeProblem(
                maze=self.maze,
                start_pos=(self.mummy.grid_x, self.mummy.grid_y),
                goal_pos=(self.player.grid_x, self.player.grid_y)
                )
            path = BFS(problem)
            if path:
                self.mummy_path = path
                self.mummy.move_turns = min(2, len(self.mummy_path))
            
            self.mummy_calculate = False
            
        if self.mummy_path and not self.mummy.is_moving and self.mummy.move_turns > 0:
            action = self.mummy_path.pop(0)
            dx, dy = 0, 0
            if action == "UP": dy = -2
            elif action == "DOWN": dy = 2
            elif action == "LEFT": dx = -2
            elif action == "RIGHT": dx = 2
            
            self.mummy.move(dx, dy, self.maze, self.maze.cell_size)
            # Giảm bộ đếm sau khi ra lệnh
            self.mummy.move_turns -= 1
            
            
           
        self.player.update()
        self.mummy.update()
        
        if (self.player.grid_x == self.mummy.grid_x and self.player.grid_y == self.mummy.grid_y):
                print("Game Over")
                jumpscare_path = os.path.join(IMAGES_PATH, "j97.jpeg")
                jumpscare_image = pygame.image.load(jumpscare_path).convert()
                jumpscare_image = pygame.transform.scale(jumpscare_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.screen.blit(jumpscare_image, (0, 0))
                pygame.display.flip()
                pygame.time.delay(2000)
                
                self.running = False
    
    def draw(self):
        self.screen.fill(COLOR_BLACK)
        self.maze.draw(self.screen)
        
        
        self.player.draw(self.screen)
        self.mummy.draw(self.screen)
        
        self.panel.draw(self.screen)
        pygame.display.flip() # hiển thị những gì đã vẽ
    
    def draw_control_panel(self):
        panel_rect = pygame.Rect(MAZE_PANEL_WIDTH, 0, CONTROL_PANEL_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, panel_rect)
        
    
