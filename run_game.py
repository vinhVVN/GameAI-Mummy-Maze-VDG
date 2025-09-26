import pygame
import os
from src.main import Game

# ===== Đường dẫn ảnh nền =====
PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__)))
ASSETS_PATH = os.path.join(PROJECT_PATH, "assets")
IMAGES_PATH = os.path.join(ASSETS_PATH, "images")
BACKGROUND_PATH = os.path.join(IMAGES_PATH, "background.png")

# Kích thước màn hình
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)

def main_menu():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("MummyGame - Menu")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 60)
    small_font = pygame.font.Font(None, 32)

    background_img = None
    if os.path.exists(BACKGROUND_PATH):
        background_img = pygame.image.load(BACKGROUND_PATH).convert()
        background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

    # Nút Play, Hướng dẫn, Quit
    play_button = pygame.Rect(SCREEN_WIDTH//2 - 100, 200, 200, 60)
    guide_button = pygame.Rect(SCREEN_WIDTH//2 - 100, 270, 200, 60)
    quit_button = pygame.Rect(SCREEN_WIDTH//2 - 100, 340, 200, 60)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.collidepoint(event.pos):
                    game = Game()
                    game.run()
                elif guide_button.collidepoint(event.pos):
                    print("Hướng dẫn (chưa có nội dung).")
                elif quit_button.collidepoint(event.pos):
                    running = False

        if background_img:
            screen.blit(background_img, (0, 0))
        else:
            screen.fill(COLOR_BLACK)

        title = font.render("Mummy Maze", True, COLOR_WHITE)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))

        pygame.draw.rect(screen, (100, 200, 100), play_button, border_radius=10)
        play_text = font.render("Play", True, COLOR_WHITE)
        screen.blit(play_text, (play_button.centerx - play_text.get_width()//2,
                                play_button.centery - play_text.get_height()//2))

        pygame.draw.rect(screen, (100, 150, 250), guide_button, border_radius=10)
        guide_text = font.render("Tutorial", True, COLOR_WHITE)
        screen.blit(guide_text, (guide_button.centerx - guide_text.get_width()//2,
                                 guide_button.centery - guide_text.get_height()//2))

        pygame.draw.rect(screen, (200, 100, 100), quit_button, border_radius=10)
        quit_text = font.render("Quit", True, COLOR_WHITE)
        screen.blit(quit_text, (quit_button.centerx - quit_text.get_width()//2,
                                quit_button.centery - quit_text.get_height()//2))

        small_font = pygame.font.SysFont("Arial", 28)

        names = [
            "Nguyen Thanh Vinh - 23110172",
            "Nguyen Hoang Giap - 23110096",
            "Duong Minh Duy - 23110083"
        ]
        for i, name in enumerate(names):
            text_surface = small_font.render(name, True, COLOR_WHITE)
            screen.blit(text_surface, (450, SCREEN_HEIGHT - 100 + i * 30))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main_menu()
