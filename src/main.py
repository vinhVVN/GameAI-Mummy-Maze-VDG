import pygame
from src.settings import *
from src.maze import *
from src.character import Player, Mummy
from src.ui import Panel , Button
from src.mazeproblem import MazeProblem, SimpleMazeProblem
from src.algorithms.bfs import BFS
from src.algorithms.ucs import UCS
from src.algorithms.ids import IDS
from src.algorithms.greedy import Greedy

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("MummyGame - Vinh Say Gex")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.maze = Maze("map6_2.txt")
        cell_size = self.maze.cell_size
        self.player = Player(5,9,self.maze.maze_size, cell_size)
        self.mummy = Mummy(7,3, self.maze.maze_size, cell_size)

        self.player_algo = "BFS"  # hoặc BFS/IDS…
        self.mummy_algo = "classic"  # classic = di chuyển greedy

        self.panel = Panel(MAZE_PANEL_WIDTH, 0, CONTROL_PANEL_WIDTH, SCREEN_HEIGHT)
        self.set_buttons()
        
        self.solution_paths = []
        self.ai_mode_active = False
        self.is_player_turn = True
        
        self.mummy_path = []
        self.is_waiting = False  # Cờ báo hiệu game có đang trong trạng thái chờ không
        self.wait_start_time = 0 # Mốc thời gian bắt đầu chờ
        self.wait_duration = 1000 # Thời gian chờ


    def load_new_map(self, map_name):
        self.maze = Maze(map_name)
        cell_size = self.maze.cell_size
        self.player = Player(1, 15, self.maze.maze_size, cell_size)
        self.mummy = Mummy(9, 13, self.maze.maze_size, cell_size)

    def set_buttons(self):
        btn_w, btn_h = 220, 40
        btn_x = MAZE_PANEL_WIDTH + (CONTROL_PANEL_WIDTH - btn_w) / 2

        def toggle_player_algo():
            algos = ["BFS", "IDS", "DFS", "UCS", "Greedy"]  # thêm vào các thuật toán ở đây
            current_index = algos.index(self.player_algo)
            new_index = (current_index + 1) % len(algos)
            self.player_algo = algos[new_index]
            btn_player_algo.text = f"Player: {self.player_algo}"

        def toggle_mummy_algo():
            if self.mummy_algo == "classic":
                self.mummy_algo = "BFS"
            else:
                self.mummy_algo = "classic"
            btn_mummy_algo.text = f"Mummy: {self.mummy_algo}"

        def change_map():
            # đổi giữa các map có sẵn
            maps = ["map6_1.txt", "map6_2.txt", "map6_3.txt", "map6_4.txt","map8_1.txt"]
            current = maps.index(self.maze.map_name)
            new_map = maps[(current + 1) % len(maps)]
            print(f"Đổi sang {new_map}")
            self.load_new_map(new_map)
            btn_change_map.text = str(new_map)

        def start_ai():
            self.start_ai_search()

        def reset_game_btn():
            self.reset_game()

        btn_reset = Button(btn_x, 400, btn_w, btn_h, "Reset", reset_game_btn)

        btn_player_algo = Button(btn_x, 100, btn_w, btn_h, f"Player: {self.player_algo}", toggle_player_algo)
        btn_mummy_algo = Button(btn_x, 150, btn_w, btn_h, f"Mummy: {self.mummy_algo}", toggle_mummy_algo)
        btn_change_map = Button(btn_x, 250, btn_w, btn_h, self.maze.map_name, change_map)
        btn_start = Button(btn_x, 350, btn_w, btn_h, "Start", start_ai)

        self.panel.add_widget(btn_player_algo)
        self.panel.add_widget(btn_mummy_algo)
        self.panel.add_widget(btn_change_map)
        self.panel.add_widget(btn_start)
        self.panel.add_widget(btn_reset)

    def find_path(self):
        gx, gy = self.maze.calculate_stair()
        if self.player_algo in ["BFS", "IDS", "DFS"]:
            initial_state = (self.player.grid_x, self.player.grid_y)
            problem = SimpleMazeProblem(self.maze, initial_state, (gx, gy))
        else:
            initial_state = ((self.player.grid_x, self.player.grid_y),
                             (self.mummy.grid_x, self.mummy.grid_y))
            problem = MazeProblem(self.maze, initial_state, (gx, gy), self.maze.trap_pos)

        algo_map = {
            "BFS": BFS,
            "UCS": UCS,
            "IDS": lambda prob: IDS(prob, max_depth=100),  # ví dụ truyền thêm tham số
            "Greedy": Greedy,
            # "DFS": DFS,
        }

        if self.player_algo in algo_map:
            path = algo_map[self.player_algo](problem)
        else:
            print(f"Thuật toán {self.player_algo} chưa được hỗ trợ!")
            path = None

        print(f"Player path ({self.player_algo}): {path}")
        self.solution_paths = path or []

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
                # chỉ gọi find_path khi solution_paths đang rỗng
                if not self.solution_paths:
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
                        if self.player_algo in ["BFS", "IDS", "DFS"]:
                            self.is_player_turn = True  # 🔑 giữ lượt Player luôn
                        else:
                            self.is_player_turn = False
                    else:
                        self.start_wait()
                        if self.player_algo in ["BFS", "IDS", "DFS"]:
                            self.is_player_turn = True
                        else:
                            self.is_player_turn = False

                else:
                    self.ai_mode_active = False
                    print("AI đã chạy xong!")

        # di chuyển mummy
        if self.player_algo not in ["BFS", "IDS", "DFS"]:
            if not self.is_player_turn and not self.player.is_moving:
                if not self.mummy_path:
                    player_pos = (self.player.grid_x, self.player.grid_y)

                    if self.mummy_algo == "classic":
                        actions = self.mummy.classic_move(player_pos, self.maze)
                    else:
                        # BFS để mummy tìm tới Player
                        problem = MazeProblem(self.maze,
                                              ((self.mummy.grid_x, self.mummy.grid_y),
                                               (self.player.grid_x, self.player.grid_y)),
                                              player_pos,
                                              self.maze.trap_pos)
                        actions = BFS(problem)

                    if actions:
                        self.mummy_path = actions
                    else:
                        self.is_player_turn = True

                    print(actions)

                if self.mummy_path:
                    action = self.mummy_path.pop(0)
                    dx, dy = 0, 0
                    if action == "UP":
                        dy = -2
                    elif action == "DOWN":
                        dy = 2
                    elif action == "LEFT":
                        dx = -2
                    elif action == "RIGHT":
                        dx = 2

                    print("mummy đi")
                    self.mummy.move(dx, dy, self.maze, self.maze.cell_size)
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

                    # self.running = False
                    self.reset_game()
            
            if self.maze.trap_pos and (self.player.grid_x, self.player.grid_y) == self.maze.trap_pos:
                    print("Game Over - Đậm phải trap")
                    jumpscare_path = os.path.join(IMAGES_PATH, "dinhbay.jpg")
                    jumpscare_image = pygame.image.load(jumpscare_path).convert()
                    jumpscare_image = pygame.transform.scale(jumpscare_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
                    self.screen.blit(jumpscare_image, (0, 0))
                    pygame.display.flip()
                    pygame.time.delay(2000)
                    # self.running = False
                    self.reset_game()

        # uninformed search
        if self.player_algo not in ["BFS", "IDS", "DFS"]:
            if (self.player.grid_x == self.mummy.grid_x and self.player.grid_y == self.mummy.grid_y):
                print("Game Over - bị ma bắt")
                jumpscare_path = os.path.join(IMAGES_PATH, "j97.jpeg")
                jumpscare_image = pygame.image.load(jumpscare_path).convert()
                jumpscare_image = pygame.transform.scale(jumpscare_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.screen.blit(jumpscare_image, (0, 0))
                pygame.display.flip()
                pygame.time.delay(2000)
                # self.running = False
                self.reset_game()

    def draw(self):
        self.screen.fill(COLOR_BLACK)
        self.maze.draw(self.screen)
        
        
        self.player.draw(self.screen)
        if self.player_algo not in ["BFS", "IDS", "DFS"]:
            self.mummy.draw(self.screen)
        
        self.panel.draw(self.screen)
        pygame.display.flip() # hiển thị những gì đã vẽ
    
    def draw_control_panel(self):
        panel_rect = pygame.Rect(MAZE_PANEL_WIDTH, 0, CONTROL_PANEL_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, panel_rect)
        
    def start_wait(self):
        self.is_waiting = True
        self.wait_start_time = pygame.time.get_ticks()

    def reset_game(self):
        # load lại map hiện tại
        current_map = self.maze.map_name
        self.maze = Maze(current_map)

        # reset player & mummy về vị trí gốc
        cell_size = self.maze.cell_size
        self.player = Player(3, 7, self.maze.maze_size, cell_size)
        self.mummy = Mummy(11, 5, self.maze.maze_size, cell_size)

        # reset trạng thái
        self.solution_paths = []
        self.ai_mode_active = False
        self.is_player_turn = True
        self.mummy_path = []
        self.is_waiting = False
        self.wait_start_time = 0
        self.wait_duration = 1000

        print("Game đã reset về trạng thái ban đầu!")

