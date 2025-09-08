import pygame

class Spritesheet:
    def __init__(self, filepath):
        self.sheet = pygame.image.load(filepath).convert_alpha() # alpha dùng để xử lý vùng trong suốt
        
    def get_image(self, x, y, width, height): # (left, top, width, height)
        image = pygame.Surface((width, height), pygame.SRCALPHA) # flag đảm bảo surface này hỗ trợ độ trong suốt
        image.blit(self.sheet, (0,0), (x,y,width, height))
        return image
    