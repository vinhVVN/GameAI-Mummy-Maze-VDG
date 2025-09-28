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
        popup_width, popup_height = 600, 350  # Giảm thêm kích thước
        
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
        
        # Load font với kích thước nhỏ hơn nữa
        try:
            font_path = os.path.join(os.path.dirname(__file__), "NotoSans-Regular.ttf")
            if os.path.exists(font_path):
                font_title = pygame.font.Font(font_path, 22)
                font_category = pygame.font.Font(font_path, 16)
                font_name = pygame.font.Font(font_path, 14)
                font_desc = pygame.font.Font(font_path, 11)
                font_button = pygame.font.Font(font_path, 10)
            else:
                font_title = pygame.font.SysFont("Arial", 22)
                font_category = pygame.font.SysFont("Arial", 16)
                font_name = pygame.font.SysFont("Arial", 14)
                font_desc = pygame.font.SysFont("Arial", 11)
                font_button = pygame.font.SysFont("Arial", 10)
        except:
            font_title = pygame.font.Font(None, 22)
            font_category = pygame.font.Font(None, 16)
            font_name = pygame.font.Font(None, 14)
            font_desc = pygame.font.Font(None, 11)
            font_button = pygame.font.Font(None, 10)
        
        # Tính toán tổng chiều cao nội dung với kích thước nhỏ hơn
        content_height = 0
        for category, algorithms_list in algorithm_categories.items():
            content_height += 25  # Giảm chiều cao category
            content_height += len(algorithms_list) * 50  # Giảm chiều cao mỗi thuật toán
        
        visible_height = popup_height - 80  # Chiều cao khung nhìn
        max_scroll = max(0, content_height - visible_height)
        
        running_popup = True
        btns = []
        
        while running_popup:
            mouse_pos = pygame.mouse.get_pos()
            
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
                        scroll_offset = max(0, scroll_offset - 25)
                    elif event.key == pygame.K_DOWN:
                        scroll_offset = min(max_scroll, scroll_offset + 25)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        # Kiểm tra click trên các nút thuật toán
                        for btn, name in btns:
                            if btn.collidepoint(mouse_pos):
                                selected_algo = name
                                return selected_algo
                    
                    elif event.button == 4:  # Cuộn lên
                        scroll_offset = max(0, scroll_offset - 25)
                    elif event.button == 5:  # Cuộn xuống
                        scroll_offset = min(max_scroll, scroll_offset + 25)
            
            # Vẽ toàn bộ màn hình game trước với hiệu ứng mờ
            self.screen.fill(COLOR_BLACK)
            self.maze.draw(self.screen)
            self.player.draw(self.screen)
            for mummy in self.mummies:
                mummy.draw(self.screen)
            self.panel.draw(self.screen)
            
            # Vẽ lớp phủ mờ
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            # Vẽ popup
            popup_rect = pygame.Rect(
                (SCREEN_WIDTH - popup_width) // 2, 
                (SCREEN_HEIGHT - popup_height) // 2, 
                popup_width, popup_height
            )
            
            # Vẽ nền popup chính
            pygame.draw.rect(self.screen, (250, 250, 252), popup_rect, border_radius=10)
            pygame.draw.rect(self.screen, (100, 150, 220), popup_rect, 2, border_radius=10)
            
            # Header - LUÔN HIỂN THỊ
            header_rect = pygame.Rect(popup_rect.x, popup_rect.y, popup_rect.width, 40)
            pygame.draw.rect(self.screen, (70, 130, 230), header_rect, border_radius=10)
            pygame.draw.rect(self.screen, (40, 100, 200), header_rect, 2, border_radius=10)
            
            # Tiêu đề chính - LUÔN HIỂN THỊ
            title_text = "CHỌN THUẬT TOÁN"
            title = font_title.render(title_text, True, (255, 255, 255))
            self.screen.blit(title, (popup_rect.centerx - title.get_width()//2, popup_rect.y + 12))

            # Cập nhật scroll offset
            scroll_offset = max(0, min(scroll_offset, max_scroll))
            
            # Vẽ scrollbar nếu cần
            if content_height > visible_height:
                scroll_area_height = popup_rect.height - 60
                scrollbar_height = max(25, (visible_height / content_height) * scroll_area_height)
                scroll_ratio = scroll_offset / max_scroll if max_scroll > 0 else 0
                scrollbar_y = popup_rect.y + 50 + (scroll_area_height - scrollbar_height) * scroll_ratio
                
                scrollbar_rect = pygame.Rect(popup_rect.right - 8, scrollbar_y, 5, scrollbar_height)
                pygame.draw.rect(self.screen, (150, 180, 230), scrollbar_rect, border_radius=2)
                pygame.draw.rect(self.screen, (80, 120, 200), scrollbar_rect, 1, border_radius=2)

            # Vùng nội dung có thể cuộn - VẼ NỀN TRƯỚC
            content_bg_rect = pygame.Rect(popup_rect.x + 10, popup_rect.y + 50, popup_rect.width - 20, visible_height)
            pygame.draw.rect(self.screen, (245, 248, 250), content_bg_rect, border_radius=6)
            
            # Reset danh sách nút
            btns = []
            current_y = -scroll_offset
            
            # Vẽ nội dung CHỈ các phần tử trong vùng nhìn thấy
            for category, algorithms_list in algorithm_categories.items():
                # Vẽ category nếu nằm trong vùng nhìn thấy
                category_top = popup_rect.y + 50 + current_y
                category_bottom = category_top + 25
                
                if category_bottom > popup_rect.y + 50 and category_top < popup_rect.y + 50 + visible_height:
                    # Category background
                    category_bg = pygame.Rect(popup_rect.x + 15, category_top, popup_rect.width - 30, 20)
                    pygame.draw.rect(self.screen, (180, 210, 240), category_bg, border_radius=4)
                    pygame.draw.rect(self.screen, (60, 110, 190), category_bg, 1, border_radius=4)
                    
                    category_text = font_category.render(category, True, (20, 60, 140))
                    self.screen.blit(category_text, (popup_rect.x + 20, category_top + 3))
                
                current_y += 25
                
                for name, desc, color in algorithms_list:
                    # Vẽ thuật toán nếu nằm trong vùng nhìn thấy
                    algo_top = popup_rect.y + 50 + current_y
                    algo_bottom = algo_top + 50
                    
                    if algo_bottom > popup_rect.y + 50 and algo_top < popup_rect.y + 50 + visible_height:
                        # Algorithm background
                        algo_bg = pygame.Rect(popup_rect.x + 20, algo_top, popup_rect.width - 40, 40)
                        
                        # Xác định màu sắc dựa trên trạng thái
                        is_hovered = algo_bg.collidepoint(mouse_pos)
                        if is_hovered:
                            bg_color = (255, 255, 240)
                            border_color = (min(color[0] + 40, 255), min(color[1] + 40, 255), min(color[2] + 40, 255))
                        elif selected_algo == name:
                            bg_color = (255, 250, 220)
                            border_color = color
                        else:
                            bg_color = (255, 255, 255)
                            border_color = (220, 220, 220)
                        
                        # Vẽ nền chính
                        pygame.draw.rect(self.screen, bg_color, algo_bg, border_radius=5)
                        pygame.draw.rect(self.screen, border_color, algo_bg, 1, border_radius=5)

                        # Tên thuật toán
                        name_text = font_name.render(name, True, (30, 100, 30))
                        self.screen.blit(name_text, (popup_rect.x + 25, algo_top + 5))

                        # Mô tả ngắn gọn hơn
                        if len(desc) > 40:
                            desc = desc[:37] + "..."
                        desc_text = font_desc.render(desc, True, (80, 80, 80))
                        self.screen.blit(desc_text, (popup_rect.x + 25, algo_top + 22))

                        # Nút chọn nhỏ hơn
                        btn = pygame.Rect(popup_rect.x + popup_rect.width - 75, algo_top + 10, 50, 18)
                        
                        btn_color = color
                        if btn.collidepoint(mouse_pos):
                            btn_color = (min(color[0] + 30, 255), min(color[1] + 30, 255), min(color[2] + 30, 255))
                        
                        # Vẽ nút
                        pygame.draw.rect(self.screen, btn_color, btn, border_radius=3)
                        pygame.draw.rect(self.screen, (255, 255, 255), btn, 1, border_radius=3)
                        
                        label = font_button.render("CHỌN", True, (255, 255, 255))
                        label_rect = label.get_rect(center=btn.center)
                        self.screen.blit(label, label_rect)

                        btns.append((btn, name))
                    
                    current_y += 50
            
            # Footer - LUÔN HIỂN THỊ
            footer_rect = pygame.Rect(popup_rect.x, popup_rect.y + popup_height - 40, popup_rect.width, 40)
            pygame.draw.rect(self.screen, (240, 245, 250), footer_rect, border_radius=10)
            pygame.draw.rect(self.screen, (200, 220, 240), footer_rect, 1, border_radius=10)
            
            # Hiển thị thuật toán đã chọn
            if selected_algo:
                selected_text = f"ĐÃ CHỌN: {selected_algo}"
                if len(selected_text) > 25:
                    selected_text = selected_text[:22] + "..."
                selected_surface = font_category.render(selected_text, True, (0, 80, 180))
                self.screen.blit(selected_surface, (popup_rect.centerx - selected_surface.get_width()//2, popup_rect.y + popup_height - 28))
            
            # Hướng dẫn ngắn gọn
            hint_text = "ESC: Thoát • ENTER: Xác nhận"
            hint_surface = font_desc.render(hint_text, True, (120, 120, 140))
            self.screen.blit(hint_surface, (popup_rect.centerx - hint_surface.get_width()//2, popup_rect.y + popup_height - 12))
            
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
        """Scale lại kích thước các ảnh mũi tên với xử lý lỗi"""
        try:
            # Tạo dictionary mới cho arrow images
            scaled_arrow_images = {}
            
            # Danh sách các hướng và file tương ứng
            arrow_directions = {
                "UP": "up_arrow.png",
                "DOWN": "down_arrow.png", 
                "LEFT": "left_arrow.png",
                "RIGHT": "right_arrow.png"
            }
            
            for direction, filename in arrow_directions.items():
                try:
                    # Tạo đường dẫn đầy đủ đến file ảnh
                    image_path = os.path.join(IMAGES_PATH, filename)
                    
                    # Kiểm tra file có tồn tại không
                    if not os.path.exists(image_path):
                        print(f"Cảnh báo: Không tìm thấy file {image_path}")
                        # Tạo một surface màu thay thế để debug
                        fallback_surface = pygame.Surface((new_size, new_size), pygame.SRCALPHA)
                        # Mỗi hướng có màu khác nhau để dễ phân biệt
                        colors = {
                            "UP": (255, 0, 0, 128),      # Đỏ
                            "DOWN": (0, 255, 0, 128),    # Xanh lá
                            "LEFT": (0, 0, 255, 128),    # Xanh dương
                            "RIGHT": (255, 255, 0, 128)  # Vàng
                        }
                        fallback_surface.fill(colors[direction])
                        
                        # Vẽ mũi tên đơn giản
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
                    
                    # Load và scale ảnh
                    original_image = pygame.image.load(image_path).convert_alpha()
                    scaled_image = pygame.transform.scale(original_image, (new_size, new_size))
                    scaled_arrow_images[direction] = scaled_image
                    
                    print(f"Đã scale ảnh {direction} thành kích thước {new_size}x{new_size}")
                    
                except pygame.error as e:
                    print(f"Lỗi khi load ảnh {filename}: {e}")
                    # Tạo surface mặc định
                    default_surface = pygame.Surface((new_size, new_size), pygame.SRCALPHA)
                    default_surface.fill((128, 128, 128, 128))  # Màu xám trong suốt
                    scaled_arrow_images[direction] = default_surface
            
            # Cập nhật arrow_images
            self.arrow_images = scaled_arrow_images
            print("Đã hoàn thành scale tất cả ảnh mũi tên")
            
        except Exception as e:
            print(f"Lỗi không xác định trong scale_arrow_images: {e}")
            # Đảm bảo arrow_images luôn có giá trị hợp lệ
            self.arrow_images = {
                "UP": pygame.Surface((new_size, new_size), pygame.SRCALPHA),
                "DOWN": pygame.Surface((new_size, new_size), pygame.SRCALPHA),
                "LEFT": pygame.Surface((new_size, new_size), pygame.SRCALPHA),
                "RIGHT": pygame.Surface((new_size, new_size), pygame.SRCALPHA)
            }