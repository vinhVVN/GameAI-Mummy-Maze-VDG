import pygame
from src.settings import *
from src.sprites import *

class Character:
    def __init__(self, sprite_path, start_pos_x, start_pos_y, cell_size):
        self.grid_x = start_pos_x
        self.grid_y = start_pos_y
        
        self.pixel_x, self.pixel_y = self.get_screen_pos_from_grid(cell_size)
        
        self.spritesheet = Spritesheet(sprite_path)
        self.animations = self.load_animations()
        
        self.direction = "DOWN" # mặc định
        self.animation_frame = 0
        self.is_moving = False
        self.move_progress = 0.0
        self.move_speed = 0.05
        self.start_pixel_pos = (0,0)
        self.target_pixel_pos = (0,0)
        
    def load_animations(self):
        return {}
    
    # tính toạ độ pixel từ toạ độ grid
    def get_screen_pos_from_grid(self, cell_size, grid_x_override=None,grid_y_override=None): 
        grid_x = grid_x_override if grid_x_override is not None else self.grid_x
        grid_y = grid_y_override if grid_y_override is not None else self.grid_y
        
        screen_x = MAZE_COORD_X + (grid_x // 2) * cell_size
        screen_y = MAZE_COORD_Y + (grid_y // 2) * cell_size
        
        return screen_x, screen_y
    
    def update(self):
        if self.is_moving:
            self.move_progress += self.move_speed
            
            # Dùng nội suy tuyến tính để di chuyển lướt mượt hơn
            self.pixel_x = self.start_pixel_pos[0] + (self.target_pixel_pos[0] - self.start_pixel_pos[0]) * self.move_progress
            self.pixel_y = self.start_pixel_pos[1] + (self.target_pixel_pos[1] - self.start_pixel_pos[1]) * self.move_progress
            
            self.animation_frame = int(self.move_progress * 4) % 4 + 1
            
            if self.move_progress >= 1:
                self.is_moving = False
                self.pixel_x, self.pixel_y = self.target_pixel_pos
                self.grid_x, self.grid_y =  self.target_grid_pos 
                self.animation_frame = 0
        else:
            # get_tick() trả về thời gian từ lúc khởi tạo game
            # % 2 để lặp lại trong 2 khung hình
            self.animation_frame = (pygame.time.get_ticks() // 1000) % 2 # // 400 để làm chậm animation

            
    
    def draw(self, surface):
        current_animation = self.animations.get(self.direction, [])
        if current_animation:
            frame_index = self.animation_frame % len(current_animation)
            image = current_animation[frame_index]
            
            surface.blit(image, (self.pixel_x, self.pixel_y))
          
    def move(self, dx=0, dy=0, maze=None, cell_size=None):
        if self.is_moving or not maze:
            return False
        
        next_grid_x = self.grid_x + dx
        next_grid_y = self.grid_y + dy
        wall_x = self.grid_x + dx//2
        wall_y = self.grid_y + dy//2
        if maze.is_passable(wall_x, wall_y):
            if dx > 0:
                self.direction = "RIGHT"
            elif dx < 0:
                self.direction = "LEFT"
            elif dy > 0:
                self.direction = "DOWN"
            elif dy < 0:
                self.direction = "UP"
        
            self.is_moving = True
            self.move_progress = 0.0
            self.start_pixel_pos = (self.pixel_x, self.pixel_y)
            self.target_pixel_pos = self.get_screen_pos_from_grid(cell_size, next_grid_x, next_grid_y)
            self.target_grid_pos = (next_grid_x, next_grid_y)  
            return True
        return False
            
                  
            
class Player(Character):
    def __init__(self, start_pos_x, start_pos_y, maze_size, cell_size):
        sprite_path = os.path.join(IMAGES_PATH, f"explorer{maze_size}.png")
        super().__init__(sprite_path, start_pos_x, start_pos_y, cell_size)
    
    def load_animations(self):
        animations = {}
        w = self.spritesheet.sheet.get_width() // 5
        h = self.spritesheet.sheet.get_height() // 4
        
        animations["UP"] = [self.spritesheet.get_image(i*w, 0, w, h) for i in range(5)]
        animations["RIGHT"] = [self.spritesheet.get_image(i*w, h, w, h) for i in range(5)]
        animations["DOWN"] = [self.spritesheet.get_image(i*w, h*2, w, h) for i in range(5)]
        animations["LEFT"] = [self.spritesheet.get_image(i*w, h*3, w, h) for i in range(5)]
        
        return animations
    
    

class Mummy(Character):
    def __init__(self, start_pos_x, start_pos_y, maze_size, cell_size):
        sprite_path = os.path.join(IMAGES_PATH, f"mummy_white{maze_size}.png")
        super().__init__(sprite_path, start_pos_x, start_pos_y, cell_size)
        self.move_turns = 0
        
    def load_animations(self):
        animations = {}
        w = self.spritesheet.sheet.get_width() // 5
        h = self.spritesheet.sheet.get_height() // 4
        
        animations["UP"] = [self.spritesheet.get_image(i*w, 0, w, h) for i in range(5)]
        animations["RIGHT"] = [self.spritesheet.get_image(i*w, h, w, h) for i in range(5)]
        animations["DOWN"] = [self.spritesheet.get_image(i*w, h*2, w, h) for i in range(5)]
        animations["LEFT"] = [self.spritesheet.get_image(i*w, h*3, w, h) for i in range(5)]
        
        return animations
    
    def classic_move(self, player_pos, maze):
        """
        Di chuyển theo quy tắc White Mummy: luôn ưu tiên đi ngang (horizontal) trước.
        Có thể đi 2 bước ngang nếu được.
        """
        actions = []
        cur_x, cur_y = self.grid_x, self.grid_y
        player_x, player_y = player_pos

        for _ in range(2):
            dist_x = player_x - cur_x
            dist_y = player_y - cur_y

            moved_this_attempt = False

            if dist_x != 0:
                move_x = (dist_x // abs(dist_x) * 2)
                if maze.is_passable(cur_x + move_x // 2, cur_y):
                    actions.append("RIGHT" if move_x > 0 else "LEFT")
                    cur_x += move_x
                    moved_this_attempt = True
                    continue

            if dist_y != 0:
                move_y = (dist_y // abs(dist_y) * 2)
                if maze.is_passable(cur_x, cur_y + move_y // 2):
                    actions.append("UP" if move_y < 0 else "DOWN")
                    cur_y += move_y
                    moved_this_attempt = True
                    continue 
                
            
            
            if not moved_this_attempt:
                break 

        return actions
            