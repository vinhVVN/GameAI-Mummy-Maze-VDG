import sys
import os

# THÊM ĐOẠN NÀY - QUAN TRỌNG
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import pygame
from src.main import Game
from src.settings import SOUNDS_PATH

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
    font = pygame.font.Font(None, 64)
    small_font = pygame.font.Font(None, 28)

    background_img = None
    if os.path.exists(BACKGROUND_PATH):
        background_img = pygame.image.load(BACKGROUND_PATH).convert()
        background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

    # Nhạc nền menu
    try:
        pygame.mixer.init()
        menu_music = os.path.join(SOUNDS_PATH, "music_menu.mp3")
        if os.path.exists(menu_music):
            pygame.mixer.music.load(menu_music)
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"Khởi tạo nhạc menu lỗi: {e}")

    # Nút Play, Hướng dẫn, Quit
    play_button = pygame.Rect(SCREEN_WIDTH//2 - 130, 240, 260, 58)
    guide_button = pygame.Rect(SCREEN_WIDTH//2 - 130, 308, 260, 58)
    quit_button = pygame.Rect(SCREEN_WIDTH//2 - 130, 376, 260, 58)
    hovered = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.collidepoint(event.pos):
                    # Tắt nhạc menu, vào game
                    try:
                        if pygame.mixer.get_init():
                            pygame.mixer.music.stop()
                    except:
                        pass
                    game = Game()
                    game.run()
                    # Quay lại menu: bật lại nhạc menu
                    try:
                        if pygame.mixer.get_init():
                            menu_music = os.path.join(SOUNDS_PATH, "music_menu.mp3")
                            if os.path.exists(menu_music):
                                pygame.mixer.music.load(menu_music)
                                pygame.mixer.music.set_volume(0.6)
                                pygame.mixer.music.play(-1)
                    except:
                        pass
                elif guide_button.collidepoint(event.pos):
                    print("Hướng dẫn (chưa có nội dung).")
                elif quit_button.collidepoint(event.pos):
                    running = False

        if background_img:
            screen.blit(background_img, (0, 0))
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))
        else:
            screen.fill(COLOR_BLACK)

        title = font.render("Mummy Maze", True, (245, 245, 255))
        title_shadow = font.render("Mummy Maze", True, (20, 20, 30))
        title_pos = (SCREEN_WIDTH//2 - title.get_width()//2, 120)
        screen.blit(title_shadow, (title_pos[0], title_pos[1] + 4))
        screen.blit(title, title_pos)

        # Hover state
        mouse_pos = pygame.mouse.get_pos()
        hovered = None
        if play_button.collidepoint(mouse_pos):
            hovered = 'play'
        elif guide_button.collidepoint(mouse_pos):
            hovered = 'guide'
        elif quit_button.collidepoint(mouse_pos):
            hovered = 'quit'

        # Button draw helper
        def draw_button(rect, label, base_color):
            is_hover = hovered == label.lower()
            shadow_offset = 5 if not is_hover else 3
            shadow = rect.move(0, shadow_offset)
            pygame.draw.rect(screen, (15, 15, 20), shadow, border_radius=12)
            color = tuple(min(255, c + 20) for c in base_color) if is_hover else base_color
            pygame.draw.rect(screen, color, rect, border_radius=12)
            pygame.draw.rect(screen, (200, 220, 240), rect, 1, border_radius=12)
            lbl = font.render(label, True, COLOR_WHITE)
            screen.blit(lbl, (rect.centerx - lbl.get_width()//2, rect.centery - lbl.get_height()//2))

        draw_button(play_button, "Play", (90, 180, 110))

        draw_button(guide_button, "Tutorial", (90, 140, 220))

        draw_button(quit_button, "Quit", (200, 100, 110))

        small_font = pygame.font.SysFont("Arial", 22)
        names = [
            "Nguyen Thanh Vinh - 23110172",
            "Nguyen Hoang Giap - 23110096",
            "Duong Minh Duy - 23110083"
        ]
        for i, name in enumerate(names):
            text_surface = small_font.render(name, True, (220, 230, 240))
            screen.blit(text_surface, (SCREEN_WIDTH - 330, SCREEN_HEIGHT - 100 + i * 26))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main_menu()