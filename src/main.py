import pygame
from src.settings import *
from src.maze import *
from src.character import Player, Mummy
from src.ui import Panel , Button
from src.mazeproblem import MazeProblem
from src.algorithms.bfs import BFS
from src.algorithms.ucs import UCS
from src.algorithms.a_star import AStar
from src.mazeproblem2 import MazeProblem2 # test có cần suy luận trong đầu trước ko 

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("MummyGame - Vinh Say Gex")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.maze = Maze("map6_5.txt")
        cell_size = self.maze.cell_size
        self.player = Player(1,9,self.maze.maze_size, cell_size)
        self.mummy = Mummy(11,9, self.maze.maze_size, cell_size)

        self.panel = Panel(MAZE_PANEL_WIDTH, 0, CONTROL_PANEL_WIDTH, SCREEN_HEIGHT)
        self.set_buttons()
        
        self.solution_paths = []
        self.ai_mode_active = False
        self.is_player_turn = True
        
        self.mummy_path = []
        self.is_waiting = False  # Cờ báo hiệu game có đang trong trạng thái chờ không
        self.wait_start_time = 0 # Mốc thời gian bắt đầu chờ
        self.wait_duration = 1000 # Thời gian chờ
    
    def set_buttons(self):
        btn_w, btn_h = 220, 40
        btn_x = MAZE_PANEL_WIDTH + (CONTROL_PANEL_WIDTH - btn_w) / 2
        
        def player_ucs():
            print("Player ucs")
        def mummy_bfs():
            print("Mummy bfs")
        def change_map():
            print("change map")
        def start_ai():
            self.start_ai_search()
            
        btn_player_algo = Button(btn_x, 100, btn_w, btn_h, "Player: UCS", player_ucs)
        btn_mummy_alogo = Button(btn_x, 150, btn_w, btn_h, "Mummy: BFS", mummy_bfs)
        btn_change_map = Button(btn_x, 250, btn_w, btn_h, "Map6_1", change_map)
        btn_start = Button(btn_x, 350, btn_w, btn_h, "Start", start_ai)
        
        self.panel.add_widget(btn_player_algo)
        self.panel.add_widget(btn_mummy_alogo)
        self.panel.add_widget(btn_change_map)
        self.panel.add_widget(btn_start)
    
    
    def find_path(self):
        gx, gy = self.maze.calculate_stair()
        
        initial_state = ((self.player.grid_x, self.player.grid_y), 
                         (self.mummy.grid_x, self.mummy.grid_y))
        
        problem = MazeProblem(self.maze, 
                              initial_state,
                              (gx, gy))
        path = BFS(problem)
        print(f"Player path: {path}")
        if path:
            self.solution_paths = path
            
        else:
            self.solution_paths = []
        
        
        
    def start_ai_search(self):
        if not self.is_player_turn or self.ai_mode_active:
            return
        self.solution_paths = []
        self.ai_mode_active = True
        
        
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
            
            if not self.ai_mode_active and event.type == pygame.KEYDOWN and not self.player.is_moving and self.is_player_turn:
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
                elif event.key == pygame.K_SPACE: # bỏ lượt
                    moved = True
                
                if moved:
                    self.start_wait()
                    self.is_player_turn = False
                
                
        
    def update(self): 
        
        self.player.update()
        self.mummy.update()
        
        
        if self.is_waiting:
            if pygame.time.get_ticks() - self.wait_start_time >= self.wait_duration:
                self.is_waiting = False # Hết giờ chờ, lượt đi tiếp theo có thể bắt đầu
            else:
                return # Vẫn đang trong thời gian chờ, không làm gì cả
        
        
        
        if self.player.is_moving or self.mummy.is_moving:
            return
        
        
        
        # AI người chơi
        if self.is_player_turn:
            if self.ai_mode_active:
                self.find_path()
                if self.solution_paths:
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
                    
                    if self.player.move(dx, dy, self.maze, self.maze.cell_size):
                        print("Người đi")
                        self.start_wait()
                        self.is_player_turn = False
                    else:
                        self.start_wait()
                        self.is_player_turn = False
                        
                    
                else:
                    self.ai_mode_active = False
                    print("AI đã chạy xong!")
        
        # di chuyển mummy
        if not self.is_player_turn and not self.player.is_moving:
            # self.start_wait()
            if not self.mummy_path:
            
                player_pos = (self.player.grid_x, self.player.grid_y)
                actions = self.mummy.classic_move(player_pos, self.maze)
                
                if actions:
                    self.mummy_path = actions
                    # self.mummy.move_turns = len(self.mummy_path)
                else:
                    self.is_player_turn = True
                
                print(actions)
            
            if self.mummy_path:
                action = self.mummy_path.pop(0)
                dx, dy = 0, 0
                if action == "UP": dy = -2
                elif action == "DOWN": dy = 2
                elif action == "LEFT": dx = -2
                elif action == "RIGHT": dx = 2
                
                print("mummy đi")
                self.mummy.move(dx, dy, self.maze, self.maze.cell_size)
                # Giảm bộ đếm sau khi ra lệnh
                if not self.mummy_path:
                    self.is_player_turn = True
                    
            
        
        if ((self.player.grid_x, self.player.grid_y) == self.maze.calculate_stair()):
                print("WINNNN")
                congratulate_path = os.path.join(IMAGES_PATH, "j97_win.jpg")
                congratulate_image = pygame.image.load(congratulate_path).convert()
                congratulate_image = pygame.transform.scale(congratulate_image, (MAZE_PANEL_WIDTH,SCREEN_HEIGHT))
                self.screen.blit(congratulate_image, (0, 0))
                pygame.display.flip()
                pygame.time.delay(2000)
                
                self.running = False
        
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
        
    def start_wait(self):
        self.is_waiting = True
        self.wait_start_time = pygame.time.get_ticks()
