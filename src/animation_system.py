# animation_system.py
import pygame
import os
from config import IMAGES_PATH

class AnimationSystem:
    def __init__(self):
        self.animations = []
        self.arrow_images = {}
        
    def load_arrow_images(self, cell_size):
        """Load và scale arrow images"""
        self.arrow_images = {
            "UP": self.load_and_scale_image("up_arrow.png", cell_size),
            "DOWN": self.load_and_scale_image("down_arrow.png", cell_size),
            "LEFT": self.load_and_scale_image("left_arrow.png", cell_size),
            "RIGHT": self.load_and_scale_image("right_arrow.png", cell_size)
        }
    
    def load_and_scale_image(self, filename, size):
        """Load và scale image với error handling"""
        try:
            path = os.path.join(IMAGES_PATH, filename)
            image = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(image, (size, size))
        except (pygame.error, FileNotFoundError) as e:
            print(f"Cannot load image: {path}. Error: {e}")
            # Trả về surface trắng thay thế
            surface = pygame.Surface((size, size), pygame.SRCALPHA)
            surface.fill((255, 255, 255, 128))
            return surface
    
    def scale_arrow_images(self, new_size):
        """Scale lại arrow images khi kích thước cell thay đổi"""
        for direction in self.arrow_images:
            self.arrow_images[direction] = pygame.transform.scale(
                self.arrow_images[direction], (new_size, new_size)
            )
    
    def draw_path(self, surface, solution_paths, current_pos, cell_size, is_player_moving=False):
        """Vẽ đường đi dự kiến"""
        if not solution_paths:
            return
            
        start_x, start_y = current_pos
        
        for action in solution_paths:
            if action == "UP":
                start_y -= 2
            elif action == "DOWN":
                start_y += 2
            elif action == "RIGHT":
                start_x += 2
            elif action == "LEFT":
                start_x -= 2
            
            arrow_img = self.arrow_images.get(action)
            if arrow_img:
                x = 50 + (start_x // 2) * cell_size
                y = 50 + (start_y // 2) * cell_size
                surface.blit(arrow_img, (x, y))