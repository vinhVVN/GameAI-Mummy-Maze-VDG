import pygame
import os
from src.settings import *
from src.sprites import Spritesheet

class Maze:
    def __init__(self, map_name, load_file = True):
        self.map_data = []
        self.stair_pos = None
        self.key_pos = None
        self.gate_pos = None
        self.trap_pos = None

        self.map_name = map_name
        self.mummy_start_pos = [(5,9)]
        self.player_start_pos = (1, 1)
        if load_file:
            self.loadmap(map_name)
        
            
        self.maze_pixel_size = 360
        self.maze_size = len(self.map_data) // 2 if self.map_data else 6
        self.cell_size = self.maze_pixel_size // self.maze_size # size của 1 ô (pixel)
        
        self.backdrop_img = None
        self.floor_img = None
        self.wall_sprites = {}
        self.stair_sprites = [] # các hướng của cầu thang
        
        
        self.load_assets()
        
    def loadmap(self, map_name):
        filepath = os.path.join(MAPS_PATH, map_name)
        with open(filepath, "r") as file:
            for r, line in enumerate(file): # lấy từng dòng trong file
                row = list(line.strip('\n')) # loại bỏ ký tự xuống dòng
                for c, char in enumerate(row):
                    if char == 'S':
                        self.stair_pos = (c, r)
                    elif char == 'K':    
                        self.key_pos = (c, r)
                    elif char == 'G':
                        self.gate_pos = (c, r)
                    elif char == 'T':
                        self.trap_pos = (c, r)
                    
                self.map_data.append(row)
                
        agent_filename = map_name.replace('.txt', '_agent.txt')
        agent_filepath = os.path.join(MAPS_PATH, agent_filename)

        if os.path.exists(agent_filepath):
            temp_mummies = []
            with open(agent_filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    parts = line.split()
                    if len(parts) == 3:
                        char_type, x_str, y_str = parts
                        try:
                            x, y = int(x_str), int(y_str) 
                            if char_type.upper() == 'P':
                                self.player_start_pos = (x, y)
                            elif char_type.upper() == 'M':
                                temp_mummies.append((x, y))
                        except ValueError:
                            print(f"Cảnh báo: Không thể đọc dòng agent trong file {agent_filename}: {line}")

            # Chỉ gán nếu file có dữ liệu mummy
            if temp_mummies:
                self.mummy_start_pos = temp_mummies

        if not self.mummy_start_pos:
            self.mummy_start_pos = ((5, 9)) # Một mummy mặc định
        
        
                
    def calculate_stair(self):
        sx, sy = self.stair_pos
        gx, gy = 0, 0
        if self.stair_pos[0] == 0: # LEFT
            gx = 1
            gy = sy
        elif self.stair_pos[0] >= self.maze_size * 2: # RIGHT
            gx = sx - 1
            gy = sy
        elif self.stair_pos[1] >= self.maze_size: # DOWN
            gx = sx
            gy = sy - 1
        else:
            gx = sx
            gy = sy + 1
        return gx, gy
        
    def load_assets(self):
        self.backdrop_img = pygame.image.load(os.path.join(IMAGES_PATH, "backdrop.png"))
        self.floor_img = pygame.image.load(os.path.join(IMAGES_PATH, f"floor{self.maze_size}.jpg"))
        self.trap_img = pygame.image.load(os.path.join(IMAGES_PATH,f"trap{self.maze_size}.png"))
        wall_sheet = Spritesheet(os.path.join(IMAGES_PATH, f"walls{self.maze_size}.png"))
        if self.maze_size == 6:
            self.wall_sprites['left'] = wall_sheet.get_image(0,0,12,78)
            self.wall_sprites['up'] = wall_sheet.get_image(12,0,72,18)
        
        if self.maze_size == 8:
            self.wall_sprites['left'] = wall_sheet.get_image(0,0,11,58)
            self.wall_sprites['up'] = wall_sheet.get_image(11,0,50,13)
            
        elif self.maze_size == 10:
            self.wall_sprites['left'] = wall_sheet.get_image(0, 0, 8, 48)
            self.wall_sprites['up'] = wall_sheet.get_image(8, 0, 44, 12)
        
        stair_sheet = Spritesheet(os.path.join(IMAGES_PATH, f"stairs{self.maze_size}.png"))
        sw = stair_sheet.sheet.get_width() // 4 # chiều rộng 1 sprite
        sh = stair_sheet.sheet.get_height()
        self.stair_sprites.append(stair_sheet.get_image(0,0,sw,sh)) # Up
        self.stair_sprites.append(stair_sheet.get_image(sw,0,sw,sh)) # Right
        self.stair_sprites.append(stair_sheet.get_image(2*sw,0,sw,sh)) # Down
        self.stair_sprites.append(stair_sheet.get_image(3*sw,0,sw,sh)) # Left
    
    def draw(self, surface):
        surface.blit(self.backdrop_img, (0,0))
        surface.blit(self.floor_img, (MAZE_COORD_X, MAZE_COORD_Y))
        self.draw_stairs(surface)
        self.draw_walls(surface)
        self.draw_trap(surface)

        
    def draw_stairs(self, surface):
        if not self.stair_pos:
            return
        
        grid_x = self.stair_pos[0] // 2
        grid_y = self.stair_pos[1] // 2

        stair_img = self.stair_sprites[0] # mặc định hướng lên
        draw_x = MAZE_COORD_X + grid_x * self.cell_size
        draw_y = MAZE_COORD_Y + grid_y * self.cell_size
        
        if self.stair_pos[0] == 0: # LEFT
            stair_img = self.stair_sprites[3]
            draw_x -= stair_img.get_width()
        elif self.stair_pos[0] >= self.maze_size * 2: # RIGHT
            stair_img = self.stair_sprites[1]
        elif self.stair_pos[1] >= self.maze_size: # DOWN
            stair_img = self.stair_sprites[2]
        else:
            draw_y -= stair_img.get_height()
        
        surface.blit(stair_img, (draw_x, draw_y))
        
        
        
    def draw_walls(self, surface):
        for r, row in enumerate(self.map_data):
            for c, char in enumerate(row):
                if char != '#':
                    continue
                draw_x = MAZE_COORD_X + (c // 2) * self.cell_size
                draw_y = MAZE_COORD_Y + (r // 2) * self.cell_size
                
                # Vẽ tường ngang
                if r % 2 == 0 and c % 2 != 0:
                    # vị trí vẽ sao cho khớp với ô
                    offset_x = -6
                    offset_y = -12
                    surface.blit(self.wall_sprites['up'], 
                                 (draw_x + offset_x, draw_y + offset_y))
                
                #Vẽ tường dọc
                elif c % 2 == 0 and r % 2 != 0:
                    offset_x = -6
                    offset_y = -12
                    surface.blit(self.wall_sprites['left'],
                                 (draw_x + offset_x, draw_y + offset_y))
    
    
    def draw_trap(self, surface):
        if not self.trap_pos:
            return
        
        draw_x = MAZE_COORD_X + (self.trap_pos[0] // 2) * self.cell_size
        draw_y = MAZE_COORD_Y + (self.trap_pos[1] // 2) * self.cell_size
        surface.blit(self.trap_img, (draw_x, draw_y))
    
    def is_passable(self, grid_x, grid_y):
        if 0 <= grid_x < len(self.map_data[0]) and 0 <= grid_y < len(self.map_data):
            return self.map_data[grid_y][grid_x] != "#"
        return False
    