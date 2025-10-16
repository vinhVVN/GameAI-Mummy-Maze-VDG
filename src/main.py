import pygame
from src.logger import Logger
import threading
import queue
from src.settings import *
from src.maze import *
from src.character import Player, Mummy
from src.ui import *
from src.popup import AlgorithmPopup
from src.settings import SOUNDS_PATH
from src.mazeproblem import MazeProblem, SimpleMazeProblem, CSPMazeProblem
from src.algorithms.bfs import BFS
from src.algorithms.ucs import UCS
from src.algorithms.ids import IDS
from src.algorithms.greedy import Greedy
from src.algorithms.dfs import DFS
from src.algorithms.AStart import AStar
from src.algorithms.beam import Beam
from src.algorithms.hill_climbing import HillClimbing
from src.algorithms.simulated_annealing import Simulated_Annealing, optimize_path
from src.algorithms.a_star_belief import AStar_Belief
from src.algorithms.partial_observation import PartialObservationProblem
from src.algorithms.backtracking import Backtracking
from src.algorithms.and_or_search import AND_OR_Search
from src.algorithms.ac3 import AC3, build_path_csp_timeexpanded, AC3_with_backtracking
from src.algorithms.No_Information_Problem import NoInformationProblem, BFS_NoInformation_Limited
from src.algorithms.forward_checking import ForwardChecking
from src.map_editor import open_map_editor

class Game:
    def __init__(self):
        pygame.init()
        self.collapsed_width = MAZE_PANEL_WIDTH + CONTROL_PANEL_WIDTH
        self.expanded_width = self.collapsed_width + LOG_PANEL_WIDTH
        self.log_panel_expanded = False
        
        self.screen = pygame.display.set_mode((self.collapsed_width, SCREEN_HEIGHT))
        pygame.display.set_caption("MummyMaze - Thoát khỏi mộ đom đóm J97")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Nhạc nền game
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
            game_music = os.path.join(SOUNDS_PATH, "music_game.mp3")
            if os.path.exists(game_music):
                pygame.mixer.music.load(game_music)
                pygame.mixer.music.set_volume(0.6)
                pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"Khởi tạo nhạc game lỗi: {e}")
        
        self.maze = Maze("map6_1.txt")
        cell_size = self.maze.cell_size
        self.player = Player(1,1,self.maze.maze_size, cell_size)
        self.mummies = [
            Mummy(5,9, self.maze.maze_size, cell_size),
        ]    
        self.player_algo = "BFS"
        self.mummy_algo = "classic"
        self.mummy_enabled = True  # Trạng thái mummy: True = bật, False = tắt
        
        # Tự động tắt mummy cho thuật toán BFS (mặc định)
        self._auto_set_mummy_state()

        
        self.panel = Panel(MAZE_PANEL_WIDTH, 0, CONTROL_PANEL_WIDTH, SCREEN_HEIGHT)
        
        log_panel_x = MAZE_PANEL_WIDTH + CONTROL_PANEL_WIDTH
        self.log_panel = LogPanel(log_panel_x, 0, LOG_PANEL_WIDTH, SCREEN_HEIGHT)
        self.set_buttons()
        
        self.solution_paths = []
        self.ai_mode_active = False
        self.is_player_turn = True
        self.current_mummy_index = 0
        
        self.is_waiting = False
        self.wait_start_time = 0
        self.wait_duration = 1000
        
        self.arrow_images = {
            "UP": pygame.transform.scale(pygame.image.load(os.path.join(IMAGES_PATH, "up_arrow.png")).convert_alpha(), size=(self.maze.cell_size, self.maze.cell_size)),
            "DOWN": pygame.transform.scale(pygame.image.load(os.path.join(IMAGES_PATH, "down_arrow.png")).convert_alpha(), size= (self.maze.cell_size, self.maze.cell_size)),
            "LEFT": pygame.transform.scale(pygame.image.load(os.path.join(IMAGES_PATH, "left_arrow.png")).convert_alpha(), size = (self.maze.cell_size, self.maze.cell_size)),
            "RIGHT": pygame.transform.scale(pygame.image.load(os.path.join(IMAGES_PATH, "right_arrow.png")).convert_alpha(), size = (self.maze.cell_size, self.maze.cell_size))
        }
        
        self.logger = Logger("mummy_maze_log.txt")
        self.popup = AlgorithmPopup(self)
        self.popup.width = 400
        
        self.available_maps = sorted([f for f in os.listdir(MAPS_PATH) if not f.endswith('_agent.txt')]) 
        

    def choose_algorithm_popup(self):
        
        return self.popup.show()

    def load_new_map(self, map_name):
        print(f"Đang tải map: {map_name}")
        self.maze = Maze(map_name)
        cell_size = self.maze.cell_size

        # Lấy vị trí từ đối tượng maze (đã đọc từ file _agents.txt)
        player_x, player_y = self.maze.player_start_pos
        self.player = Player(player_x, player_y, self.maze.maze_size, cell_size)
        
        self.mummies = []
        for mummy_x, mummy_y in self.maze.mummy_start_pos:
            self.mummies.append(Mummy(mummy_x, mummy_y, self.maze.maze_size, cell_size))

        # Reset lại các trạng thái của game
        self.solution_paths = []
        self.ai_mode_active = False
        self.is_player_turn = True
        self.is_waiting = False
        self.current_mummy_index = 0
        self.mummy_enabled = True  # Reset trạng thái mummy về bật
        self.log_panel.clear()
        self.logger.clear()
        
        # Cập nhật lại kích thước mũi tên nếu cần
        if "map10" in map_name:
            self.scale_arrow_images(36)
        elif "map8" in map_name:
            self.scale_arrow_images(45)
        elif "map6" in map_name:
            self.scale_arrow_images(60)



    def set_buttons(self):
        btn_w, btn_h = 220, 40
        btn_x = MAZE_PANEL_WIDTH + (CONTROL_PANEL_WIDTH - btn_w) / 2

        
        
        def toggle_player_algo():
            new_algo = self.choose_algorithm_popup()
            if new_algo:
                self.player_algo = new_algo
                for widget in self.panel.widgets:
                    if hasattr(widget, 'text') and widget.text.startswith("Player:"):
                        widget.text = f"Player: {self.player_algo}"
                
                # Tự động tắt/bật mummy dựa trên thuật toán
                self._auto_set_mummy_state()
                print(f"Đã chọn thuật toán: {new_algo}")

        def toggle_mummy_algo():
            if self.mummy_algo == "classic":
                self.mummy_algo = "BFS"
            else:
                self.mummy_algo = "classic"
            for widget in self.panel.widgets:
                if hasattr(widget, 'text') and widget.text.startswith("Mummy:"):
                    widget.text = f"Mummy: {self.mummy_algo}"

        def change_map():
            try:
                current_index = self.available_maps.index(self.maze.map_name)
                next_index = (current_index + 1) % len(self.available_maps)
                new_map_name = self.available_maps[next_index]
                
                self.load_new_map(new_map_name)
                
                
                btn_change_map.text = new_map_name

            except (ValueError, IndexError) as e:
                print(f"Lỗi khi đổi map: {e}")

        def start_ai():
            self.start_ai_search()

        def reset_game_btn():
            self.reset_game()

        def toggle_mummy():
            self.mummy_enabled = not self.mummy_enabled
            for widget in self.panel.widgets:
                if hasattr(widget, 'text') and widget.text.startswith("Mummy:"):
                    widget.text = f"Mummy: {'ON' if self.mummy_enabled else 'OFF'}"
            print(f"Mummy {'bật' if self.mummy_enabled else 'tắt'}")


        
        btn_reset = Button(btn_x, 350, btn_w, btn_h, "Reset", reset_game_btn)
        btn_player_algo = Button(btn_x, 100, btn_w, btn_h, f"Player: {self.player_algo}", toggle_player_algo)
        btn_mummy_toggle = Button(btn_x, 150, btn_w, btn_h, f"Mummy: {'ON' if self.mummy_enabled else 'OFF'}", toggle_mummy)
        # compare_button = Button(btn_x, 150, btn_w, btn_h, "Compare", command=lambda: self.set_screen("COMPARISON"))
        btn_change_map = Button(btn_x, 200, btn_w, btn_h, self.maze.map_name, change_map)
        btn_start = Button(btn_x, 300, btn_w, btn_h, "Start", start_ai)
        
        
        self.panel.add_widget(btn_player_algo)
        self.panel.add_widget(btn_mummy_toggle)
        # self.panel.add_widget(compare_button)
        self.panel.add_widget(btn_change_map)
        self.panel.add_widget(btn_start)
        self.panel.add_widget(btn_reset)
        
        # Thêm nút Menu để bật/tắt Log Panel
        menu_button_path = os.path.join(IMAGES_PATH, "hamburger.png")
        # Đặt nút ở góc trên bên phải của Panel điều khiển
        menu_button_x = self.panel.rect.right - 42 
        menu_button_y = self.panel.rect.top + 10
        
        # Lambda function để gọi hàm toggle của log_panel
        menu_button = ImageButton(menu_button_x, menu_button_y, 32, 32, menu_button_path, 
                                  on_click_func=lambda: self.toggle_log_panel())
        self.panel.add_widget(menu_button)
        
        btn_create_map = Button(btn_x, 400, btn_w, btn_h, "Create Map", lambda: open_map_editor(self))
        self.panel.add_widget(btn_create_map)
        
    def find_path(self):
        gx, gy = self.maze.calculate_stair()
        mummy_positions = [(m.grid_x, m.grid_y) for m in self.mummies]
        initial_state = (self.player.grid_x, self.player.grid_y)
        if self.player_algo in ["BFS", "IDS", "DFS", "Forward Checking"]:
            
            problem = SimpleMazeProblem(self.maze, initial_state, (gx, gy))
        elif self.player_algo == "PO_search":
            problem = PartialObservationProblem(self.maze)
        elif self.player_algo == "Non_infor":
            problem = NoInformationProblem(self.maze)
        elif self.player_algo == "Backtracking":
            pass
        elif self.player_algo == "Forward Checking":
            initial_state = ((self.player.grid_x, self.player.grid_y),
                        tuple(sorted(mummy_positions)))
            problem = CSPMazeProblem(self.maze, 
                            initial_state,
                            (gx, gy), 
                            100)
            
        else:
            initial_state = ((self.player.grid_x, self.player.grid_y),
                            tuple(sorted(mummy_positions)))
            problem = MazeProblem(self.maze, 
                                initial_state,
                                (gx, gy), 
                                self.maze.trap_pos)

        algo_map = {
            "BFS": BFS,
            "UCS": UCS,
            "IDS": IDS,
            "Greedy": Greedy,
            "DFS": DFS,
            "AStar": AStar,
            "Hill climbing": HillClimbing,
            "Beam": Beam,
            "SA": Simulated_Annealing,
            "Non_infor": BFS_NoInformation_Limited,
            "Forward Checking": lambda prob, logger: ForwardChecking(prob, logger, min_safe_dist=2, debug=True)
        }

        
        if self.player_algo in algo_map:
            # SỬA: Gọi phương thức solve() để lấy kết quả, không gán object
            algorithm = algo_map[self.player_algo](problem, logger = self.logger)
            if hasattr(algorithm, 'solve'):
                result = algorithm.solve()  # Gọi solve() để lấy danh sách actions
            else:
                result = algorithm  # Các thuật toán khác trả về trực tiếp
        elif self.player_algo == "PO_search":
            result = AStar_Belief(problem, logger= self.logger)
        elif self.player_algo == "AND_OR":
            result = AND_OR_Search(problem, logger=self.logger)
        elif self.player_algo == "Backtracking":
            result = Backtracking(self.maze, initial_state,
                                  self.maze.calculate_stair(),logger = self.logger)

        elif self.player_algo == "AC3+BT":
            gx, gy = self.maze.calculate_stair()
            start = (self.player.grid_x, self.player.grid_y)
            goal = (gx, gy)
            # Simple upper bound: Manhattan distance in cell units (grid step=2), times a factor
            manh = abs(start[0]-goal[0]) + abs(start[1]-goal[1])
            horizon = max(1, manh // 2 + 8)
            result = AC3_with_backtracking(self.maze, start, goal, horizon, logger=self.logger)

        else:
            print(f"Thuật toán {self.player_algo} chưa được hỗ trợ!")
            result = None

        summary_data = {
            "Algorithm": self.player_algo,
            "Time (s)": f"{result.get('time_taken', 0):.4f}",
            "Nodes/Iter": f"{result.get('nodes_expanded', 'N/A')}",
        }
        if self.player_algo == "SA" and result["path"]:
            raw_path = result["path"]
            self.logger.log(f"Raw path length: {len(raw_path)}")
            good_path = optimize_path(problem, raw_path)
            self.logger.log(f"Optimized path length: {len(good_path)}")
            result["path"] = good_path
            
            
        if "path" in result and result["path"] is not None:
            summary_data["Path Length"] = len(result["path"])
        if "initial_cost" in result and result["initial_cost"] is not None:
            summary_data["Initial cost"] = result["initial_cost"]
        if "final_cost" in result and result["final_cost"] is not None:
            summary_data["Final_cost"] = result["final_cost"]
        
        
        for key, value in summary_data.items():
            self.logger.log(f"{key}: {value}")
        
        # Lưu toàn bộ log ra file
        self.logger.save_to_file()
        self.log_panel.update_summary(summary_data)
        
        print(f"Player path ({self.player_algo}): {result['path']}")
        self.solution_paths = result["path"] or []

    def start_ai_search(self):
        if not self.is_player_turn or self.ai_mode_active:
            return
        self.logger.clear()
        self.log_panel.clear() 
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

            self.panel.handle_event(event)
            self.log_panel.handle_event(event)
            
            if not self.ai_mode_active and event.type == pygame.KEYDOWN and not self.player.is_moving and self.is_player_turn:
                cell_size = self.maze.cell_size
                moved = False
                if event.key == pygame.K_UP:
                    self.player.move(dy=-2, maze=self.maze, cell_size=cell_size)
                    moved = True
                elif event.key == pygame.K_DOWN:
                    self.player.move(dy=2, maze=self.maze, cell_size=cell_size)
                    moved = True
                elif event.key == pygame.K_LEFT:
                    self.player.move(dx=-2, maze=self.maze, cell_size=cell_size)
                    moved = True
                elif event.key == pygame.K_RIGHT:
                    self.player.move(dx=2, maze=self.maze, cell_size=cell_size)
                    moved = True
                elif event.key == pygame.K_SPACE:
                    moved = True
                
                if moved:
                    self.start_wait()
                    self.is_player_turn = False
        
    def update(self):
        self.log_panel.update(self.log_panel_expanded)
        
        # Thu nhỏ cửa sổ SAU KHI panel đã co lại hoàn toàn
        if not self.log_panel_expanded and not self.log_panel.is_animating():
            if self.screen.get_width() != self.collapsed_width:
                self.screen = pygame.display.set_mode((self.collapsed_width, SCREEN_HEIGHT))
        
        self.player.update()
        for mummy in self.mummies:
            mummy.update()

        if self.is_waiting:
            if pygame.time.get_ticks() - self.wait_start_time >= self.wait_duration:
                self.is_waiting = False
            else:
                return
        
        any_mummy_moving = any(m.is_moving for m in self.mummies)
        if self.player.is_moving or any_mummy_moving:
            return
        
        # AI người chơi
        if self.is_player_turn:
            if self.ai_mode_active:
                if not self.solution_paths and (self.player.grid_x, self.player.grid_y) != self.maze.calculate_stair():
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
                        # Chuyển lượt dựa trên trạng thái mummy
                        if self.mummy_enabled:
                            self.is_player_turn = False  # Chuyển sang lượt mummy
                        else:
                            self.is_player_turn = True   # Tiếp tục lượt player
                    else:
                        self.start_wait()
                        if self.mummy_enabled:
                            self.is_player_turn = False  # Chuyển sang lượt mummy
                        else:
                            self.is_player_turn = True   # Tiếp tục lượt player
                else:
                    self.ai_mode_active = False
                    print("AI đã chạy xong!")

        # Xử lý di chuyển mummy cho tất cả thuật toán khi mummy được bật
        if self.mummy_enabled and not self.is_player_turn and not self.player.is_moving:
            if not self.mummies:
                self.is_player_turn = True
                return
            
            current_mummy = self.mummies[self.current_mummy_index]
            if not current_mummy.path:
                player_pos = (self.player.grid_x, self.player.grid_y)
                if self.mummy_algo == "classic":
                    actions = current_mummy.classic_move(player_pos, self.maze)
                else:
                    problem = MazeProblem(self.maze,
                                        ((current_mummy.grid_x, current_mummy.grid_y),
                                        (self.player.grid_x, self.player.grid_y)),
                                        player_pos,
                                        self.maze.trap_pos)
                    actions = BFS(problem)
                    
                if actions:
                    current_mummy.path = actions
                    print(actions)
            
            if current_mummy.path:
                action = current_mummy.path.pop(0)
                dx, dy = 0, 0
                if action == "UP":
                    dy = -2
                elif action == "DOWN":
                    dy = 2
                elif action == "LEFT":
                    dx = -2
                elif action == "RIGHT":
                    dx = 2

                print(f"Mummy {self.current_mummy_index + 1} at ({current_mummy.grid_x}, {current_mummy.grid_y}) moves {action}")
                current_mummy.move(dx, dy, self.maze, self.maze.cell_size)
                self.handle_mummy_collisions()
                    
            if not current_mummy.path:
                self.current_mummy_index += 1
                self.start_wait() 
                
                if self.current_mummy_index >= len(self.mummies):
                    self.current_mummy_index = 0
                    self.is_player_turn = True

        # Kiểm tra win condition
        if ((self.player.grid_x, self.player.grid_y) == self.maze.calculate_stair()):
                print("WINNNN")
                congratulate_path = os.path.join(IMAGES_PATH, "win.png")
                if os.path.exists(congratulate_path):
                    congratulate_image = pygame.image.load(congratulate_path).convert()
                    congratulate_image = pygame.transform.scale(congratulate_image, (MAZE_PANEL_WIDTH,SCREEN_HEIGHT))
                    self.screen.blit(congratulate_image, (0, 0))
                    pygame.display.flip()
                    pygame.time.delay(2000)
                self.reset_game()
        
        # Kiểm tra trap condition
        if self.maze.trap_pos and (self.player.grid_x, self.player.grid_y) == self.maze.trap_pos:
                print("Game Over - Đậm phải trap")
                jumpscare_path = os.path.join(IMAGES_PATH, "dinhbay.png")
                if os.path.exists(jumpscare_path):
                    jumpscare_image = pygame.image.load(jumpscare_path).convert()
                    jumpscare_image = pygame.transform.scale(jumpscare_image, (MAZE_PANEL_WIDTH, SCREEN_HEIGHT))
                    self.screen.blit(jumpscare_image, (0, 0))
                    pygame.display.flip()
                    pygame.time.delay(2000)
                self.reset_game()

        # Kiểm tra va chạm với mummy nếu mummy được bật (cho tất cả thuật toán)
        if self.mummy_enabled:
            for mummy in self.mummies:
                if (self.player.grid_x == mummy.grid_x and self.player.grid_y == mummy.grid_y):
                    print("Game Over - bị ma bắt")
                    jumpscare_path = os.path.join(IMAGES_PATH, "lose.png")
                    if os.path.exists(jumpscare_path):
                        jumpscare_image = pygame.image.load(jumpscare_path).convert()
                        jumpscare_image = pygame.transform.scale(jumpscare_image, (MAZE_PANEL_WIDTH, SCREEN_HEIGHT))
                        self.screen.blit(jumpscare_image, (0, 0))
                        pygame.display.flip()
                        pygame.time.delay(2000)
                    self.reset_game()
                    
    def draw(self):
        self.screen.fill(COLOR_BLACK)
        self.maze.draw(self.screen)
        self.draw_path(self.screen)
        self.player.draw(self.screen)
        
        # Vẽ mummy nếu được bật (cho tất cả thuật toán)
        if self.mummy_enabled:
            for mummy in self.mummies:
                mummy.draw(self.screen)
        
        self.panel.draw(self.screen)
        self.log_panel.draw(self.screen, self.logger)
        pygame.display.flip()
    
    def draw_path(self, surface):
        if not self.ai_mode_active:
            return
        
        if self.player.is_moving:
            start_x, start_y = self.player.target_grid_pos
        else:
            start_x, start_y = self.player.grid_x, self.player.grid_y
            
        if not self.solution_paths:
            return
        
        player_x, player_y = start_x, start_y
        
        for action in self.solution_paths:
            if action == "UP":
                player_y -= 2
            elif action == "DOWN":  # SỬA: elif thay vì if
                player_y += 2
            elif action == "RIGHT":
                player_x += 2
            elif action == "LEFT":
                player_x -= 2
        
            arrow_img = self.arrow_images.get(action)
            if arrow_img:
                x = MAZE_COORD_X + (player_x//2) * self.maze.cell_size
                y = MAZE_COORD_Y + (player_y//2) * self.maze.cell_size
                surface.blit(arrow_img, (x,y))
        
    def start_wait(self):
        self.is_waiting = True
        self.wait_start_time = pygame.time.get_ticks()

    def reset_game(self):
        # Tải lại map hiện tại
        current_map_name = self.maze.map_name
        self.maze = Maze(current_map_name)

        # Reset player & mummies về vị trí gốc
        cell_size = self.maze.cell_size

        player_x, player_y = self.maze.player_start_pos
        self.player = Player(player_x, player_y, self.maze.maze_size, cell_size)

        self.mummies = []
        for mummy_x, mummy_y in self.maze.mummy_start_pos:
            self.mummies.append(Mummy(mummy_x, mummy_y, self.maze.maze_size, cell_size))
        self.solution_paths = []
        self.ai_mode_active = False
        self.is_player_turn = True
        self.is_waiting = False
        self.wait_start_time = 0
        self.wait_duration = 1000
        self.current_mummy_index = 0
        

    def handle_mummy_collisions(self):
        i = 0
        while i < len(self.mummies):
            j = i + 1
            while j < len(self.mummies):
                mummy1 = self.mummies[i]
                mummy2 = self.mummies[j]
                if (mummy1.grid_x, mummy1.grid_y) == (mummy2.grid_x, mummy2.grid_y):
                    print("Hai con mummy chơi nhau !")
                    self.mummies.pop(j)
                    continue
                j += 1
            i += 1
    
    def scale_arrow_images(self, new_size):
        """Scale lại kích thước các ảnh mũi tên với xử lý lỗi"""
        try:
            scaled_arrow_images = {}
            arrow_directions = {
                "UP": "up_arrow.png",
                "DOWN": "down_arrow.png", 
                "LEFT": "left_arrow.png",
                "RIGHT": "right_arrow.png"
            }
            
            for direction, filename in arrow_directions.items():
                try:
                    image_path = os.path.join(IMAGES_PATH, filename)
                    if not os.path.exists(image_path):
                        print(f"Cảnh báo: Không tìm thấy file {image_path}")
                        fallback_surface = pygame.Surface((new_size, new_size), pygame.SRCALPHA)
                        colors = {
                            "UP": (255, 0, 0, 128),
                            "DOWN": (0, 255, 0, 128),
                            "LEFT": (0, 0, 255, 128),
                            "RIGHT": (255, 255, 0, 128)
                        }
                        fallback_surface.fill(colors[direction])
                        pygame.draw.polygon(fallback_surface, (255, 255, 255), [
                            (new_size//2, 5),
                            (5, new_size-5),
                            (new_size-5, new_size-5)
                        ] if direction == "UP" else [
                            (new_size//2, new_size-5),
                            (5, 5),
                            (new_size-5, 5)
                        ] if direction == "DOWN" else [
                            (5, new_size//2),
                            (new_size-5, 5),
                            (new_size-5, new_size-5)
                        ] if direction == "LEFT" else [
                            (new_size-5, new_size//2),
                            (5, 5),
                            (5, new_size-5)
                        ])
                        scaled_arrow_images[direction] = fallback_surface
                        continue
                    
                    original_image = pygame.image.load(image_path).convert_alpha()
                    scaled_image = pygame.transform.scale(original_image, (new_size, new_size))
                    scaled_arrow_images[direction] = scaled_image
                    
                except pygame.error as e:
                    print(f"Lỗi khi load ảnh {filename}: {e}")
                    default_surface = pygame.Surface((new_size, new_size), pygame.SRCALPHA)
                    default_surface.fill((128, 128, 128, 128))
                    scaled_arrow_images[direction] = default_surface
            
            self.arrow_images = scaled_arrow_images
            print("Đã hoàn thành scale tất cả ảnh mũi tên")
            
        except Exception as e:
            print(f"Lỗi không xác định trong scale_arrow_images: {e}")
            self.arrow_images = {
                "UP": pygame.Surface((new_size, new_size), pygame.SRCALPHA),
                "DOWN": pygame.Surface((new_size, new_size), pygame.SRCALPHA),
                "LEFT": pygame.Surface((new_size, new_size), pygame.SRCALPHA),
                "RIGHT": pygame.Surface((new_size, new_size), pygame.SRCALPHA)
            }
            
    def _auto_set_mummy_state(self):
        """Tự động tắt/bật mummy dựa trên thuật toán được chọn"""
        # Danh sách các thuật toán tìm đường (mummy mặc định TẮT)
        pathfinding_algorithms = [
            "BFS", "IDS", "DFS", "PO_search", "AND_OR", "Non_infor", 
            "Forward Checking", "Backtracking", "AC3+BT", "A*", "UCS", 
            "Greedy", "Hill Climbing", "Simulated Annealing", "Beam Search"
        ]
        
        # Tự động tắt mummy cho các thuật toán tìm đường
        if self.player_algo in pathfinding_algorithms:
            self.mummy_enabled = False
        else:
            self.mummy_enabled = True
        
        # Cập nhật text nút mummy (nếu panel đã được khởi tạo)
        if hasattr(self, 'panel') and self.panel:
            for widget in self.panel.widgets:
                if hasattr(widget, 'text') and widget.text.startswith("Mummy:"):
                    widget.text = f"Mummy: {'ON' if self.mummy_enabled else 'OFF'}"
        
        print(f"Tự động {'tắt' if not self.mummy_enabled else 'bật'} mummy cho thuật toán {self.player_algo}")

    def toggle_log_panel(self):
        self.log_panel_expanded = not self.log_panel_expanded
        
        if self.log_panel_expanded:
            # Mở rộng cửa sổ NGAY LẬP TỨC
            
            self.screen = pygame.display.set_mode((self.expanded_width, SCREEN_HEIGHT))
            self.popup.width = min(650, SCREEN_WIDTH - 40)
            
        else:
            self.screen = pygame.display.set_mode((self.collapsed_width, SCREEN_HEIGHT))
            self.popup.width = 400
            
    