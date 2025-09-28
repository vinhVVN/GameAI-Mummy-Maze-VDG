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
from src.algorithms.dfs import DFS
from src.algorithms.AStart import AStar
from src.algorithms.beam import Beam
from src.algorithms.simulated_annealing import Simulated_Annealing

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
        self.mummies = [
            Mummy(5,9, self.maze.maze_size, cell_size),
            # Mummy(9,13, self.maze.maze_size, cell_size)
        ]    
        self.player_algo = "BFS"  # hoặc BFS/IDS…
        self.mummy_algo = "classic"  # classic = di chuyển greedy

        self.panel = Panel(MAZE_PANEL_WIDTH, 0, CONTROL_PANEL_WIDTH, SCREEN_HEIGHT)
        self.set_buttons()
        
        self.solution_paths = []
        self.ai_mode_active = False
        self.is_player_turn = True
        self.current_mummy_index = 0
        
        self.is_waiting = False  # Cờ báo hiệu game có đang trong trạng thái chờ không
        self.wait_start_time = 0 # Mốc thời gian bắt đầu chờ
        self.wait_duration = 1000 # Thời gian chờ
        
        self.arrow_images = {
            "UP": pygame.transform.scale(pygame.image.load(os.path.join(IMAGES_PATH, "up_arrow.png")).convert_alpha(), size=(self.maze.cell_size, self.maze.cell_size)),
            "DOWN": pygame.transform.scale(pygame.image.load(os.path.join(IMAGES_PATH, "down_arrow.png")).convert_alpha(), size= (self.maze.cell_size, self.maze.cell_size)),
            "LEFT": pygame.transform.scale(pygame.image.load(os.path.join(IMAGES_PATH, "left_arrow.png")).convert_alpha(), size = (self.maze.cell_size, self.maze.cell_size)),
            "RIGHT": pygame.transform.scale(pygame.image.load(os.path.join(IMAGES_PATH, "right_arrow.png")).convert_alpha(), size = (self.maze.cell_size, self.maze.cell_size))
        }

    def choose_algorithm_popup(self):
        """Hiển thị popup chọn thuật toán và trả về thuật toán được chọn"""
        popup_width, popup_height = 720, 610
        
        # Danh sách thuật toán với tên ngắn gọn để sử dụng trong code
        algorithm_categories = {
            "TÌM KIẾM KHÔNG CÓ THÔNG TIN": [
                ("BFS", "Tìm đường ngắn nhất bằng cách duyệt theo chiều rộng", (34, 139, 34)),
                ("DFS", "Tìm đường bằng cách duyệt theo chiều sâu", (0, 191, 255)),
                ("IDS", "Tìm kiếm theo chiều sâu lặp", (70, 130, 180)),
            ],
            "TÌM KIẾM CÓ THÔNG TIN": [
                ("AStart", "Tìm đường thông minh kết hợp chi phí và heuristic", (255, 165, 0)),
                ("Greedy", "Tìm đường dựa trên heuristic", (255, 215, 0)),
                ("UCS", "Tìm đường với chi phí tích lũy nhỏ nhất", (100, 149, 237)),
            ],
            "THUẬT TOÁN TỐI ƯU": [
                ("SA", "Tìm kiếm mô phỏng luyện kim", (199, 21, 133)),
                ("Beam", "Tìm đường theo chiều rộng nhưng giới hạn lựa chọn", (139, 69, 19)),
            ]
        }
        
        selected_algo = self.player_algo
        scroll_offset = 0
        scroll_dragging = False
        scroll_start_y = 0
        
        # Load font từ file hoặc system font
        try:
            # Thử load font từ thư mục game
            font_path = os.path.join(os.path.dirname(__file__), "NotoSans-Regular.ttf")
            if os.path.exists(font_path):
                font_title = pygame.font.Font(font_path, 28)
                font_category = pygame.font.Font(font_path, 20)
                font_name = pygame.font.Font(font_path, 18)
                font_desc = pygame.font.Font(font_path, 14)
            else:
                # Fallback to system fonts that support Vietnamese
                font_title = pygame.font.SysFont("Arial", 28)
                font_category = pygame.font.SysFont("Arial", 20)
                font_name = pygame.font.SysFont("Arial", 18)
                font_desc = pygame.font.SysFont("Arial", 14)
        except:
            # Ultimate fallback
            font_title = pygame.font.Font(None, 28)
            font_category = pygame.font.Font(None, 20)
            font_name = pygame.font.Font(None, 18)
            font_desc = pygame.font.Font(None, 14)
        
        # Tính toán tổng chiều cao nội dung
        content_height = 0
        for category, algorithms_list in algorithm_categories.items():
            content_height += 35
            content_height += len(algorithms_list) * 55
        
        visible_height = popup_height - 90
        max_scroll = max(0, content_height - visible_height)
        
        def draw_scrollbar(popup_rect):
            scroll_area_height = popup_rect.height - 100
            if content_height > visible_height:
                scrollbar_height = max(30, (visible_height / content_height) * scroll_area_height)
                scroll_ratio = scroll_offset / (content_height - visible_height) if (content_height - visible_height) > 0 else 0
                scrollbar_y = popup_rect.y + 100 + (scroll_area_height - scrollbar_height) * scroll_ratio
                
                scrollbar_rect = pygame.Rect(popup_rect.right - 15, scrollbar_y, 8, scrollbar_height)
                pygame.draw.rect(self.screen, (180, 180, 180), scrollbar_rect, border_radius=4)
                pygame.draw.rect(self.screen, (120, 120, 120), scrollbar_rect, 1, border_radius=4)
                return scrollbar_rect
            return None
        
        running_popup = True
        btns = []
        scrollbar_rect = None
        
        while running_popup:
            # Xử lý sự kiện
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return selected_algo
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return selected_algo
                    elif event.key == pygame.K_RETURN and selected_algo:
                        return selected_algo
                    elif event.key == pygame.K_UP:
                        scroll_offset = max(0, scroll_offset - 30)
                    elif event.key == pygame.K_DOWN:
                        scroll_offset = min(max_scroll, scroll_offset + 30)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        # Kiểm tra click trên các nút thuật toán
                        for btn, name in btns:
                            if btn.collidepoint(event.pos):
                                return name
                        
                        # Kiểm tra click trên scrollbar
                        if scrollbar_rect and scrollbar_rect.collidepoint(event.pos):
                            scroll_dragging = True
                            scroll_start_y = event.pos[1]
                    
                    elif event.button == 4:  # Cuộn lên
                        scroll_offset = max(0, scroll_offset - 30)
                    elif event.button == 5:  # Cuộn xuống
                        scroll_offset = min(max_scroll, scroll_offset + 30)

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        scroll_dragging = False

                elif event.type == pygame.MOUSEMOTION:
                    if scroll_dragging and scrollbar_rect:
                        delta_y = event.pos[1] - scroll_start_y
                        scroll_area_height = popup_height - 130
                        scroll_ratio = delta_y / scroll_area_height
                        scroll_offset = max(0, min(max_scroll, scroll_offset + scroll_ratio * content_height))
                        scroll_start_y = event.pos[1]
            
            # Vẽ toàn bộ màn hình game trước
            self.screen.fill(COLOR_BLACK)
            self.maze.draw(self.screen)
            self.player.draw(self.screen)
            for mummy in self.mummies:
                mummy.draw(self.screen)
            self.panel.draw(self.screen)
            
            # Vẽ popup
            popup_rect = pygame.Rect(
                (SCREEN_WIDTH - popup_width) // 2, 
                (SCREEN_HEIGHT - popup_height) // 2, 
                popup_width, popup_height
            )
            
            # Vẽ nền popup
            pygame.draw.rect(self.screen, (245, 245, 245), popup_rect, border_radius=10)
            pygame.draw.rect(self.screen, (200, 200, 200), popup_rect, 2, border_radius=10)
            
            # Tiêu đề chính
            title_text = "CHỌN THUẬT TOÁN TÌM ĐƯỜNG"
            title = font_title.render(title_text, True, (0, 102, 204))
            self.screen.blit(title, (popup_rect.centerx - title.get_width()//2, popup_rect.y + 15))

            # Cập nhật scroll offset
            scroll_offset = max(0, min(scroll_offset, max_scroll))
            
            # Vẽ scrollbar
            scrollbar_rect = draw_scrollbar(popup_rect)

            # Tạo surface cho nội dung cuộn
            content_surface = pygame.Surface((popup_rect.width - 35, visible_height))
            content_surface.fill((245, 245, 245))
            
            # Reset danh sách nút
            btns = []
            current_y = -scroll_offset
            
            # Vẽ nội dung
            for category, algorithms_list in algorithm_categories.items():
                if current_y + 35 > 0 and current_y < visible_height:
                    # Category background
                    category_bg = pygame.Rect(5, current_y, popup_rect.width - 45, 30)
                    pygame.draw.rect(content_surface, (210, 225, 240), category_bg, border_radius=4)
                    pygame.draw.rect(content_surface, (80, 130, 180), category_bg, 1, border_radius=4)
                    
                    category_text = font_category.render(category, True, (0, 70, 140))
                    content_surface.blit(category_text, (10, current_y + 6))
                
                current_y += 35
                
                for name, desc, color in algorithms_list:
                    if current_y + 55 > 0 and current_y < visible_height:
                        # Algorithm background
                        algo_bg = pygame.Rect(8, current_y, popup_rect.width - 55, 50)
                        if selected_algo == name:
                            pygame.draw.rect(content_surface, (255, 250, 200), algo_bg, border_radius=6)
                        else:
                            pygame.draw.rect(content_surface, (255, 255, 255), algo_bg, border_radius=6)
                        pygame.draw.rect(content_surface, (210, 210, 210), algo_bg, 1, border_radius=6)

                        # Tên thuật toán
                        name_text = font_name.render(name, True, (0, 90, 0))
                        content_surface.blit(name_text, (12, current_y + 5))

                        # Mô tả
                        desc_lines = []
                        if len(desc) > 50:
                            words = desc.split()
                            line1 = ' '.join(words[:len(words)//2])
                            line2 = ' '.join(words[len(words)//2:])
                            desc_lines = [line1, line2]
                        else:
                            desc_lines = [desc]
                        
                        for i, line in enumerate(desc_lines):
                            desc_text = font_desc.render(line, True, (70, 70, 70))
                            content_surface.blit(desc_text, (12, current_y + 25 + i*15))

                        # Nút chọn
                        btn = pygame.Rect(popup_rect.width - 140, current_y + 8, 80, 32)
                        mouse_pos = pygame.mouse.get_pos()
                        adjusted_mouse_pos = (mouse_pos[0] - popup_rect.x - 20, mouse_pos[1] - popup_rect.y - 90)
                        
                        btn_color = color
                        if btn.collidepoint(adjusted_mouse_pos):
                            btn_color = tuple(min(c + 20, 255) for c in color)
                        
                        pygame.draw.rect(content_surface, btn_color, btn, border_radius=6)
                        pygame.draw.rect(content_surface, (255, 255, 255), btn, 1, border_radius=6)
                        
                        label = font_desc.render("CHỌN", True, (255, 255, 255))
                        label_rect = label.get_rect(center=btn.center)
                        content_surface.blit(label, label_rect)

                        # Lưu vị trí thực của nút
                        real_btn = pygame.Rect(
                            popup_rect.x + 20 + btn.x, 
                            popup_rect.y + 90 + btn.y, 
                            btn.width, btn.height
                        )
                        btns.append((real_btn, name))
                    
                    current_y += 55
            
            # Hiển thị content surface
            self.screen.blit(content_surface, (popup_rect.x + 20, popup_rect.y + 80))
            
            # Hiển thị thuật toán đã chọn
            if selected_algo:
                selected_bg = pygame.Rect(popup_rect.x + 20, popup_rect.y + 540, popup_rect.width - 40, 40)
                pygame.draw.rect(self.screen, (230, 240, 255), selected_bg, border_radius=6)
                pygame.draw.rect(self.screen, (80, 130, 200), selected_bg, 1, border_radius=6)
                
                selected_text = f"ĐÃ CHỌN: {selected_algo}"
                if len(selected_text) > 40:
                    selected_text = selected_text[:37] + "..."
                selected_surface = font_category.render(selected_text, True, (0, 0, 150))
                self.screen.blit(selected_surface, (popup_rect.centerx - selected_surface.get_width()//2, popup_rect.y + 550))
            
            pygame.display.flip()
            self.clock.tick(60)
        
        return selected_algo

    def load_new_map(self, map_name, player_pos=(1, 15), mummy_pos=[(1, 9)]):
        self.maze = Maze(map_name)
        cell_size = self.maze.cell_size

        self.player = Player(player_pos[0], player_pos[1], self.maze.maze_size, cell_size)

        self.mummies = [
            Mummy(mx, my, self.maze.maze_size, cell_size)
            for (mx, my) in mummy_pos
        ]

    def set_buttons(self):
        btn_w, btn_h = 220, 40
        btn_x = MAZE_PANEL_WIDTH + (CONTROL_PANEL_WIDTH - btn_w) / 2

        def toggle_player_algo():
            # Hiển thị popup chọn thuật toán
            new_algo = self.choose_algorithm_popup()
            if new_algo:
                self.player_algo = new_algo
                # Cập nhật text cho button
                for widget in self.panel.widgets:
                    if hasattr(widget, 'text') and widget.text.startswith("Player:"):
                        widget.text = f"Player: {self.player_algo}"
                print(f"Đã chọn thuật toán: {new_algo}")

        def toggle_mummy_algo():
            if self.mummy_algo == "classic":
                self.mummy_algo = "BFS"
            else:
                self.mummy_algo = "classic"
            # Cập nhật text cho button
            for widget in self.panel.widgets:
                if hasattr(widget, 'text') and widget.text.startswith("Mummy:"):
                    widget.text = f"Mummy: {self.mummy_algo}"

        def change_map(_new_map = None):
            if _new_map is not None:
                new_map = _new_map
            else:
                # đổi giữa các map có sẵn
                maps = ["map6_1.txt", "map6_2.txt", "map6_3.txt", "map6_4.txt", "map6_5.txt", "map8_1.txt"]
                current = maps.index(self.maze.map_name)
                new_map = maps[(current + 1) % len(maps)]
                self.scale_arrow_images(360//int(new_map[3]))
            print(f"Đổi sang {new_map}")
            if new_map == "map6_1.txt":
                self.load_new_map(new_map, player_pos=(1, 1), mummy_pos=[(5, 9)])
            elif new_map == "map6_2.txt":
                self.load_new_map(new_map, player_pos=(1, 11), mummy_pos=[(3, 3)])
            elif new_map == "map6_3.txt":
                self.load_new_map(new_map, player_pos=(1, 11), mummy_pos=[(3, 3)])
            elif new_map == "map6_4.txt":
                self.load_new_map(new_map, player_pos=(1, 11), mummy_pos=[(3, 3)])
            elif new_map == "map6_5.txt":
                self.load_new_map(new_map, player_pos=(1, 11), mummy_pos=[(9, 9)])
            elif new_map == "map8_1.txt":
                self.load_new_map(new_map, player_pos=(5, 5), mummy_pos=[(15, 11), (3, 3)])
            # Cập nhật text cho button
            for widget in self.panel.widgets:
                if hasattr(widget, 'text') and widget.text in ["map6_1.txt", "map6_2.txt", "map6_3.txt", "map6_4.txt", "map6_5.txt", "map8_1.txt"]:
                    widget.text = str(new_map)

        self._change_map_func = change_map

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
        mummy_positions = [(m.grid_x, m.grid_y) for m in self.mummies]
        
        if self.player_algo in ["BFS", "IDS", "DFS"]:
            initial_state = (self.player.grid_x, self.player.grid_y)
            problem = SimpleMazeProblem(self.maze, initial_state, (gx, gy))
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
            "IDS": lambda prob: IDS(prob, max_depth=100),
            "Greedy": Greedy,
            "DFS": DFS,
            "AStart": AStar,
            "Beam": Beam,
            "SA": Simulated_Annealing
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

            self.panel.handle_event(event)
            
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
                            self.is_player_turn = True
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

            if ((self.player.grid_x, self.player.grid_y) == self.maze.calculate_stair()):
                    print("WINNNN")
                    congratulate_path = os.path.join(IMAGES_PATH, "j97_win.jpg")
                    congratulate_image = pygame.image.load(congratulate_path).convert()
                    congratulate_image = pygame.transform.scale(congratulate_image, (MAZE_PANEL_WIDTH,SCREEN_HEIGHT))
                    self.screen.blit(congratulate_image, (0, 0))
                    pygame.display.flip()
                    pygame.time.delay(2000)
                    self.reset_game()
            
            if self.maze.trap_pos and (self.player.grid_x, self.player.grid_y) == self.maze.trap_pos:
                    print("Game Over - Đậm phải trap")
                    jumpscare_path = os.path.join(IMAGES_PATH, "dinhbay.jpg")
                    jumpscare_image = pygame.image.load(jumpscare_path).convert()
                    jumpscare_image = pygame.transform.scale(jumpscare_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
                    self.screen.blit(jumpscare_image, (0, 0))
                    pygame.display.flip()
                    pygame.time.delay(2000)
                    self.reset_game()

        for mummy in self.mummies:
            if self.player_algo not in ["BFS", "IDS", "DFS"]:
                if (self.player.grid_x == mummy.grid_x and self.player.grid_y == mummy.grid_y):
                    print("Game Over - bị ma bắt")
                    jumpscare_path = os.path.join(IMAGES_PATH, "j97.jpeg")
                    jumpscare_image = pygame.image.load(jumpscare_path).convert()
                    jumpscare_image = pygame.transform.scale(jumpscare_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
                    self.screen.blit(jumpscare_image, (0, 0))
                    pygame.display.flip()
                    pygame.time.delay(2000)
                    self.reset_game()
                    
    def draw(self):
        self.screen.fill(COLOR_BLACK)
        self.maze.draw(self.screen)
        self.draw_path(self.screen)
        self.player.draw(self.screen)
        
        if self.player_algo not in ["BFS", "IDS", "DFS"]:
            for mummy in self.mummies:
                mummy.draw(self.screen)
        
        self.panel.draw(self.screen)
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
            if action == "DOWN":
                player_y += 2
            if action == "RIGHT":
                player_x += 2
            if action == "LEFT":
                player_x -= 2
        
            arrow_img = self.arrow_images.get(action)
            if arrow_img:
                x = MAZE_COORD_X + (player_x//2) * self.maze.cell_size
                y = MAZE_COORD_Y + (player_y//2) * self.maze.cell_size
                surface.blit(arrow_img, (x,y))
    
    def draw_control_panel(self):
        panel_rect = pygame.Rect(MAZE_PANEL_WIDTH, 0, CONTROL_PANEL_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, panel_rect)
        
    def start_wait(self):
        self.is_waiting = True
        self.wait_start_time = pygame.time.get_ticks()

    def reset_game(self):
        current_map = self.maze.map_name
        if hasattr(self, "_change_map_func"):
            self._change_map_func(current_map)
        self.solution_paths = []
        self.ai_mode_active = False
        self.is_player_turn = True
        self.is_waiting = False
        self.wait_start_time = 0
        self.wait_duration = 1000
        self.current_mummy_index = 0
        print(f"Game đã reset về map {current_map}!")

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
        self.arrow_images = {
            "UP": pygame.transform.scale(
                pygame.image.load(os.path.join(IMAGES_PATH, "up_arrow.png")).convert_alpha(), 
                size=(new_size, new_size)
            ),
            "DOWN": pygame.transform.scale(
                pygame.image.load(os.path.join(IMAGES_PATH, "down_arrow.png")).convert_alpha(), 
                size=(new_size, new_size)
            ),
            "LEFT": pygame.transform.scale(
                pygame.image.load(os.path.join(IMAGES_PATH, "left_arrow.png")).convert_alpha(), 
                size=(new_size, new_size)
            ),
            "RIGHT": pygame.transform.scale(
                pygame.image.load(os.path.join(IMAGES_PATH, "right_arrow.png")).convert_alpha(), 
                size=(new_size, new_size)
            )
        }