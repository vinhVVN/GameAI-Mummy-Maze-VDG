import pygame
import os
from src.settings import *  
from src.maze import Maze 
from src.ui import Button, TextInput

class MapEditor:
    def __init__(self, game):
        self.game = game 
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Map Editor - Mummy Maze")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.map_size = 6  
        self.grid_size = 2 * self.map_size + 1  # Lưới 13x13
        self.map_data = self.create_initial_map()  
        self.maze = Maze("", load_file=False)  
        self.maze.maze_size = self.map_size
        self.maze.cell_size = 360 // self.map_size  # 60px mỗi ô logic
        self.maze.map_data = self.map_data  
        
        self.grid_x = MAZE_COORD_X  
        self.grid_y = MAZE_COORD_Y
        self.cell_size = self.maze.cell_size  
        self.selected_tool = ' ' 
        self.hovered_cell = None
        
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 32)
        
        self.player_pos = None  
        self.mummy_positions = [] 
        
        self.init_ui()
        self.update_display()

    def create_initial_map(self):
        return [['#' if r == 0 or r == self.grid_size-1 or c == 0 or c == self.grid_size-1 else ' ' 
                 for c in range(self.grid_size)] for r in range(self.grid_size)]

    def expand_to_file_format(self):
        # trả về map_data hiện tại (không tự động thêm tường)
        return [row[:] for row in self.map_data]

    def entry(self, placeholder):
        screen = pygame.display.get_surface()
        clock = pygame.time.Clock()
        
        input_box = TextInput(180, 200, 300, 40, placeholder)
        font = pygame.font.Font(None, 36)
        done = False
        filename = None

        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                result = input_box.handle_event(event)
                if result: 
                    filename = result
                    done = True

            screen.fill((28, 33, 45))
            label = font.render("Enter file name:", True, (255, 255, 255))
            screen.blit(label, (180, 150))
            input_box.draw(screen)

            pygame.display.flip()
            clock.tick(30)
        
        return filename
    
    
    def init_ui(self):
        self.buttons = []
        tools = [
            ('Empty ( )', ' '),
            ('Stair (S)', 'S'),
            ('Player (P)', 'P'),
            ('Mummy (M)', 'M')
        ]
        btn_x = 550
        btn_y = 100
        btn_w, btn_h = 200, 40
        for text, tool in tools:
            def set_tool(t=tool):
                self.selected_tool = t
                print(f"Selected tool: {t}") 
            btn = Button(btn_x, btn_y, btn_w, btn_h, text, set_tool)
            self.buttons.append(btn)
            btn_y += 50
        
        # Nút vẽ tường
        def draw_vertical_wall():
            self.selected_tool = 'vertical_wall'
            print("Selected tool: Vertical Wall")
        
        def draw_horizontal_wall():
            self.selected_tool = 'horizontal_wall'
            print("Selected tool: Horizontal Wall")
        
        self.buttons.append(Button(btn_x, btn_y, btn_w, btn_h, "Draw Vertical Wall", draw_vertical_wall))
        btn_y += 50
        self.buttons.append(Button(btn_x, btn_y, btn_w, btn_h, "Draw Horizontal Wall", draw_horizontal_wall))
        btn_y += 50
        
        def new_map():
            self.map_size = 6
            self.grid_size = 2 * self.map_size + 1
            self.cell_size = 360 // self.map_size 
            self.map_data = self.create_initial_map()
            self.maze.maze_size = self.map_size
            self.maze.cell_size = self.cell_size

            self.player_pos = None
            self.mummy_positions = []
            
            self.update_display()
        
        def save_map():
            name = self.entry("File map name (map6_1.txt):")
            if not name.endswith('.txt'): name += '.txt'
            if not name.startswith('map6'):
                return
            
            # Lưu file map chính
            filepath = os.path.join(MAPS_PATH, name)
            with open(filepath, 'w') as f:
                for row in self.map_data:
                    f.write(''.join(row) + '\n')
            print(f"Saved map to {filepath}")

            # Lưu file agent
            agent_filename = name.replace('.txt', '_agent.txt')
            agent_filepath = os.path.join(MAPS_PATH, agent_filename)
            with open(agent_filepath, 'w') as f:
                if self.player_pos:
                    f.write(f"P {self.player_pos[0]} {self.player_pos[1]}\n")
                for c, r in self.mummy_positions:
                    f.write(f"M {c} {r}\n")
            print(f"Saved agents to {agent_filepath}")
        
        
        def load_map():
            name = self.entry("Map name to load (map6_1.txt): ")
            if not name.endswith('.txt'): name += '.txt'
            if not name.startswith('map6'):
                return
            filepath = os.path.join(MAPS_PATH, name)

            # Load file map chính
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    self.map_data = [list(line.strip('\n')) for line in f]
                self.grid_size = len(self.map_data)
                self.map_size = (self.grid_size - 1) // 2
                self.maze.maze_size = self.map_size
                self.maze.cell_size = 360 // self.map_size
                self.update_display()
                print(f"Loaded map from {filepath}")
            else:
                print("File map không tồn tại")
                return

            # Load file agent tương ứng
            self.player_pos = None
            self.mummy_positions = []
            agent_filename = name.replace('.txt', '_agent.txt')
            agent_filepath = os.path.join(MAPS_PATH, agent_filename)

            if os.path.exists(agent_filepath):
                with open(agent_filepath, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) == 3:
                            char, x_str, y_str = parts
                            try:
                                x, y = int(x_str), int(y_str)
                                if char.upper() == 'P':
                                    self.player_pos = (x, y)
                                elif char.upper() == 'M':
                                    self.mummy_positions.append((x, y))
                            except ValueError:
                                continue 
                print(f"Loaded agents from {agent_filepath}")
        
        def close_editor():
            
            self.running = False
        
        func_btn_y = btn_y + 50
        self.buttons.append(Button(btn_x, func_btn_y, btn_w, btn_h, "New Map", new_map))
        func_btn_y += 50
        self.buttons.append(Button(btn_x, func_btn_y, btn_w, btn_h, "Save", save_map))
        func_btn_y += 50
        self.buttons.append(Button(btn_x, func_btn_y, btn_w, btn_h, "Load", load_map))
        func_btn_y += 50
        self.buttons.append(Button(btn_x, func_btn_y, btn_w, btn_h, "Close", close_editor))

    def update_display(self):
        self.maze.map_data = self.map_data
        # Cập nhật stair_pos nếu có
        for r, row in enumerate(self.maze.map_data):
            for c, char in enumerate(row):
                if char == 'S':
                    self.maze.stair_pos = (c, r)
                    break
            if self.maze.stair_pos:
                break

    def get_grid_pos(self, mouse_pos):
        mx, my = mouse_pos

        # Ưu tiên kiểm tra các ô bên trong mê cung trước
        gx = (mx - self.grid_x) // self.cell_size
        gy = (my - self.grid_y) // self.cell_size
        if 0 <= gx < self.map_size and 0 <= gy < self.map_size:
            # Trả về tọa độ trong file (ví dụ: ô logic (0,0) là (1,1) trong file)
            file_c = 2 * gx + 1
            file_r = 2 * gy + 1
            return (file_c, file_r)

        # Nếu không phải ô bên trong, kiểm tra các ô viền để đặt 'S'
        half_cell = self.cell_size // 2
        quarter_cell = self.cell_size // 4

        # Tạo danh sách các vị trí viền hợp lệ (tọa độ trong file .txt)
        edge_positions = []
        # Hàng trên và dưới (r=0, r=grid_size-1)
        for c in range(1, self.grid_size, 2):
            edge_positions.append((c, 0))
            edge_positions.append((c, self.grid_size - 1))
        # Cột trái và phải (c=0, c=grid_size-1)
        for r in range(1, self.grid_size, 2):
            edge_positions.append((0, r))
            edge_positions.append((self.grid_size - 1, r))

        # Kiểm tra xem chuột có click vào một trong các ô viền không
        for c, r in edge_positions:
            # Tính toán vị trí và kích thước của ô viền trên màn hình
            rect_x = self.grid_x + (c * half_cell) - quarter_cell
            rect_y = self.grid_y + (r * half_cell) - quarter_cell
            
            # Tạo một hình chữ nhật để kiểm tra va chạm
            edge_rect = pygame.Rect(rect_x, rect_y, half_cell, half_cell)

            # Nếu vị trí chuột nằm trong ô viền này, trả về tọa độ của nó
            if edge_rect.collidepoint(mx, my):
                return (c, r)

        # Nếu không click vào đâu cả
        return None

    def is_valid_pos(self, tool, gx, gy):
        # Đích 'S', nhân vật 'P' là duy nhất
        if tool in 'SP':
            # Kiểm tra trong map_data
            for r in range(self.grid_size):
                for c in range(self.grid_size):
                    if self.map_data[r][c] == tool:
                        print(f"'{tool}' đã tồn tại trên bản đồ.")
                        return False
                    
            if tool == 'P' and self.player_pos is not None:
                print(f"Player đã tồn tại.")
                return False

        # Logic cho Cầu thang 'S'
        if tool == 'S':
            is_on_horizontal_edge = (gy in (0, self.grid_size - 1)) and (gx % 2 != 0)
            is_on_vertical_edge = (gx in (0, self.grid_size - 1)) and (gy % 2 != 0)
            return is_on_horizontal_edge or is_on_vertical_edge

        # các công cụ khác (' ', 'P', 'M') phải được đặt bên trong đường viền
        is_inside_border = (0 < gx < self.grid_size - 1) and (0 < gy < self.grid_size - 1)
        if not is_inside_border:
            return False

        #  'P', 'M' chỉ có thể đặt trên ô sàn (cả hai tọa độ là số lẻ)
        if tool in 'PM':
            is_on_floor_tile = (gx % 2 != 0) and (gy % 2 != 0)
            return is_on_floor_tile

        # 'Empty' có thể dùng ở mọi nơi bên trong
        if tool == ' ':
            return True
            
        return False

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                for btn in self.buttons:
                    btn.handle_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Lấy tọa độ ô logic (sàn) hoặc ô viền (cho S)
                    pos = self.get_grid_pos(event.pos)
                    if pos:
                        gx, gy = pos
                        # 'EMPTY' 
                        if self.selected_tool == ' ':
                            mouse_x, mouse_y = event.pos
                            cell_pixel_x = self.grid_x + (gx // 2) * self.cell_size
                            cell_pixel_y = self.grid_y + (gy // 2) * self.cell_size
                            relative_x = mouse_x - cell_pixel_x
                            relative_y = mouse_y - cell_pixel_y
                            threshold = self.cell_size // 4
                            
                            target_c, target_r = gx, gy # Mặc định xóa vật phẩm tại (gx, gy)

                            # Suy ra tường cần xóa dựa trên vị trí click trong ô
                            if relative_y < threshold: target_r = gy - 1 # Tường trên
                            elif relative_y > self.cell_size - threshold: target_r = gy + 1 # Tường dưới
                            elif relative_x < threshold: target_c = gx - 1 # Tường trái
                            elif relative_x > self.cell_size - threshold: target_c = gx + 1 # Tường phải
                            
                            # Chỉ xóa nếu mục tiêu nằm trong viền
                            if 0 < target_c < self.grid_size - 1 and 0 < target_r < self.grid_size - 1:
                                self.map_data[target_r][target_c] = ' '
                            
                            # Xóa cả P và M nếu click trúng
                            if self.player_pos == (gx, gy): self.player_pos = None
                            if (gx, gy) in self.mummy_positions: self.mummy_positions.remove((gx, gy))
                            self.update_display()
                            
                            

                        # Tường
                        elif self.selected_tool == 'vertical_wall':
                             # Tường dọc nằm ở cột chẵn, hàng lẻ.
                             # Click vào ô (gx, gy), ta sẽ vẽ tường bên phải của nó.
                            target_c, target_r = gx + 1, gy
                            if 0 < target_c < self.grid_size - 1 and 0 < target_r < self.grid_size - 1:
                                self.map_data[target_r][target_c] = '#'
                            self.update_display()
                            
                        elif self.selected_tool == 'horizontal_wall':
                            # Tường ngang nằm ở cột lẻ, hàng chẵn.
                            # Click vào ô (gx, gy), ta sẽ vẽ tường bên dưới nó.
                            target_c, target_r = gx, gy + 1
                            if 0 < target_c < self.grid_size - 1 and 0 < target_r < self.grid_size - 1:
                                self.map_data[target_r][target_c] = '#'
                            self.update_display()
                            
                        # Player, Mummy, Đích
                        elif self.is_valid_pos(self.selected_tool, gx, gy):
                            # Đặt Player
                            if self.selected_tool == 'P':
                                self.player_pos = (gx, gy)
                            # Đặt hoặc xóa Mummy (toggle)
                            elif self.selected_tool == 'M':
                                if (gx, gy) in self.mummy_positions:
                                    self.mummy_positions.remove((gx, gy)) # Xóa nếu đã tồn tại
                                else:
                                    self.mummy_positions.append((gx, gy)) # Thêm nếu chưa có
                            # Đặt vật phẩm vào map_data như cũ
                            elif self.selected_tool in 'SKGT':
                                if self.selected_tool == 'S':
                                    for r in range(self.grid_size):
                                        for c in range(self.grid_size):
                                            if self.map_data[r][c] == 'S': self.map_data[r][c] = '#'
                                    self.map_data[gy][gx] = self.selected_tool
                                else:
                                    self.map_data[gy][gx] = self.selected_tool
                            self.update_display()
                            
                if event.type == pygame.MOUSEMOTION:
                    self.hovered_cell = self.get_grid_pos(event.pos)
            
            self.screen.fill(COLOR_PANEL_BG)
            
            # Title
            title = self.title_font.render("Map Editor", True, COLOR_WHITE)
            self.screen.blit(title, (300, 10))
            
            # Vẽ map 
            self.maze.draw(self.screen)
            
            # Vẽ lưới highlight với hiệu ứng hover 
            for r in range(self.map_size):
                for c in range(self.map_size):
                    x = self.grid_x + c * self.cell_size
                    y = self.grid_y + r * self.cell_size
                    file_gx = 2 * c + 1
                    file_gy = 2 * r + 1
                    is_hovered = self.hovered_cell == (file_gx, file_gy)
                    color = (100, 150, 100) if is_hovered else (50, 50, 50)
                    pygame.draw.rect(self.screen, color, (x, y, self.cell_size, self.cell_size), 1)
                    if is_hovered:
                        pygame.draw.rect(self.screen, (0, 255, 0, 100), (x, y, self.cell_size, self.cell_size), 2)  # Hiệu ứng hover
            
            # Vị trí cho phép đặt S
            edge_positions = []
            for c in (1, 3, 5, 7, 9, 11):
                edge_positions.append((0, c))
            for c in (1, 3, 5, 7, 9, 11):
                edge_positions.append((12, c))
            for r in (1, 3, 5, 7, 9, 11):
                edge_positions.append((r, 0))
            for r in (1, 3, 5, 7, 9, 11):
                edge_positions.append((r, 12))
            
            for r, c in edge_positions:
                x = self.grid_x + (c * self.cell_size) // 2 - self.cell_size // 4
                y = self.grid_y + (r * self.cell_size) // 2 - self.cell_size // 4
                color = (250, 0, 0) if (r, c) == self.hovered_cell else (150, 0, 0)
                pygame.draw.rect(self.screen, color, (x, y, self.cell_size // 2, self.cell_size // 2), 1)
                if (c, r) == self.hovered_cell and self.selected_tool == 'S':
                    pygame.draw.rect(self.screen, (0, 255, 0, 100), (x, y, self.cell_size // 2, self.cell_size // 2), 2)
            
            
            # Vẽ Player và Mummies
            agent_font = pygame.font.Font(None, self.cell_size // 2)
            # Vẽ Player
            if self.player_pos:
                c, r = self.player_pos
                px = self.grid_x + (c // 2) * self.cell_size + self.cell_size // 4
                py = self.grid_y + (r // 2) * self.cell_size + self.cell_size // 4
                text_surf = agent_font.render('P', True, (0, 150, 255))
                self.screen.blit(text_surf, (px, py))
            
            # Vẽ Mummies
            for c, r in self.mummy_positions:
                px = self.grid_x + (c // 2) * self.cell_size + self.cell_size // 4
                py = self.grid_y + (r // 2) * self.cell_size + self.cell_size // 4
                text_surf = agent_font.render('M', True, (255, 100, 0))
                self.screen.blit(text_surf, (px, py))
            
            # Vẽ buttons
            for btn in self.buttons:
                btn.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(FPS)

def open_map_editor(game):
    editor = MapEditor(game)
    editor.run()
    game.screen = pygame.display.set_mode((800, 480))