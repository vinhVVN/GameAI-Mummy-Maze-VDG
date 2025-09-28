# popup.py
import pygame
import os
from config import GameConfig, SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BLACK

class AlgorithmPopup:
    def __init__(self, game):
        self.game = game
        self.width, self.height = 600, 350
        self.selected_algo = game.player_algo
        self.scroll_offset = 0
        self.buttons = []
        
        # Load fonts
        self.fonts = self.load_fonts()
    
    def load_fonts(self):
        """Load fonts với fallback"""
        try:
            font_path = os.path.join(os.path.dirname(__file__), "NotoSans-Regular.ttf")
            if os.path.exists(font_path):
                return {
                    'title': pygame.font.Font(font_path, 22),
                    'category': pygame.font.Font(font_path, 16),
                    'name': pygame.font.Font(font_path, 14),
                    'desc': pygame.font.Font(font_path, 11),
                    'button': pygame.font.Font(font_path, 10)
                }
            else:
                return {
                    'title': pygame.font.SysFont("Arial", 22),
                    'category': pygame.font.SysFont("Arial", 16),
                    'name': pygame.font.SysFont("Arial", 14),
                    'desc': pygame.font.SysFont("Arial", 11),
                    'button': pygame.font.SysFont("Arial", 10)
                }
        except:
            return {
                'title': pygame.font.Font(None, 22),
                'category': pygame.font.Font(None, 16),
                'name': pygame.font.Font(None, 14),
                'desc': pygame.font.Font(None, 11),
                'button': pygame.font.Font(None, 10)
            }
    
    def calculate_content_height(self):
        """Tính tổng chiều cao nội dung"""
        height = 0
        for category, algorithms in GameConfig.ALGORITHM_CATEGORIES.items():
            height += 25  # Category height
            height += len(algorithms) * 50  # Algorithm items height
        return height
    
    def show(self):
        """Hiển thị popup và trả về thuật toán được chọn"""
        content_height = self.calculate_content_height()
        visible_height = self.height - 80
        max_scroll = max(0, content_height - visible_height)
        
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            self.buttons = []
            
            # Xử lý events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return self.selected_algo
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return self.selected_algo
                    elif event.key == pygame.K_RETURN and self.selected_algo:
                        return self.selected_algo
                    elif event.key == pygame.K_UP:
                        self.scroll_offset = max(0, self.scroll_offset - 25)
                    elif event.key == pygame.K_DOWN:
                        self.scroll_offset = min(max_scroll, self.scroll_offset + 25)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for btn_rect, algo_name in self.buttons:
                            if btn_rect.collidepoint(mouse_pos):
                                return algo_name
                    elif event.button == 4:  # Scroll up
                        self.scroll_offset = max(0, self.scroll_offset - 25)
                    elif event.button == 5:  # Scroll down
                        self.scroll_offset = min(max_scroll, self.scroll_offset + 25)
            
            # Vẽ
            self.draw(mouse_pos)
            pygame.display.flip()
            self.game.clock.tick(60)
        
        return self.selected_algo
    
    def draw(self, mouse_pos):
        """Vẽ popup"""
        # Vẽ background game với hiệu ứng mờ
        self.game.screen.fill(COLOR_BLACK)
        self.game.maze.draw(self.game.screen)
        self.game.player.draw(self.game.screen)
        for mummy in self.game.mummies:
            mummy.draw(self.game.screen)
        self.game.panel.draw(self.game.screen)
        
        # Vẽ overlay mờ
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.game.screen.blit(overlay, (0, 0))
        
        # Vẽ popup container
        popup_rect = pygame.Rect(
            (SCREEN_WIDTH - self.width) // 2,
            (SCREEN_HEIGHT - self.height) // 2,
            self.width, self.height
        )
        
        # Nền popup
        pygame.draw.rect(self.game.screen, (250, 250, 252), popup_rect, border_radius=10)
        pygame.draw.rect(self.game.screen, (100, 150, 220), popup_rect, 2, border_radius=10)
        
        # Header
        header_rect = pygame.Rect(popup_rect.x, popup_rect.y, popup_rect.width, 40)
        pygame.draw.rect(self.game.screen, (70, 130, 230), header_rect, border_radius=10)
        title_text = self.fonts['title'].render("CHỌN THUẬT TOÁN", True, (255, 255, 255))
        self.game.screen.blit(title_text, (popup_rect.centerx - title_text.get_width()//2, popup_rect.y + 12))
        
        # Content area
        content_bg_rect = pygame.Rect(popup_rect.x + 10, popup_rect.y + 50, popup_rect.width - 20, self.height - 90)
        pygame.draw.rect(self.game.screen, (245, 248, 250), content_bg_rect, border_radius=6)
        
        # Vẽ nội dung có thể cuộn
        self.draw_scrollable_content(popup_rect, mouse_pos, visible_height)
        
        # Footer
        footer_rect = pygame.Rect(popup_rect.x, popup_rect.y + self.height - 40, popup_rect.width, 40)
        pygame.draw.rect(self.game.screen, (240, 245, 250), footer_rect, border_radius=10)
        
        # Hiển thị thuật toán đã chọn
        if self.selected_algo:
            selected_text = f"ĐÃ CHỌN: {self.selected_algo}"
            selected_surface = self.fonts['category'].render(selected_text, True, (0, 80, 180))
            self.game.screen.blit(selected_surface, (popup_rect.centerx - selected_surface.get_width()//2, popup_rect.y + self.height - 28))
        
        # Hướng dẫn
        hint_text = "ESC: Thoát • ENTER: Xác nhận"
        hint_surface = self.fonts['desc'].render(hint_text, True, (120, 120, 140))
        self.game.screen.blit(hint_surface, (popup_rect.centerx - hint_surface.get_width()//2, popup_rect.y + self.height - 12))
    
    def draw_scrollable_content(self, popup_rect, mouse_pos, visible_height):
        """Vẽ nội dung có thể cuộn"""
        current_y = -self.scroll_offset
        
        for category, algorithms in GameConfig.ALGORITHM_CATEGORIES.items():
            # Vẽ category nếu trong view
            category_top = popup_rect.y + 50 + current_y
            if category_top + 25 > popup_rect.y + 50 and category_top < popup_rect.y + 50 + visible_height:
                category_bg = pygame.Rect(popup_rect.x + 15, category_top, popup_rect.width - 30, 20)
                pygame.draw.rect(self.game.screen, (180, 210, 240), category_bg, border_radius=4)
                category_text = self.fonts['category'].render(category, True, (20, 60, 140))
                self.game.screen.blit(category_text, (popup_rect.x + 20, category_top + 3))
            
            current_y += 25
            
            # Vẽ algorithms
            for name, desc, color in algorithms:
                algo_top = popup_rect.y + 50 + current_y
                if algo_top + 50 > popup_rect.y + 50 and algo_top < popup_rect.y + 50 + visible_height:
                    self.draw_algorithm_item(popup_rect, algo_top, name, desc, color, mouse_pos)
                
                current_y += 50
    
    def draw_algorithm_item(self, popup_rect, top, name, desc, color, mouse_pos):
        """Vẽ một item thuật toán"""
        algo_bg = pygame.Rect(popup_rect.x + 20, top, popup_rect.width - 40, 40)
        
        # Xác định màu dựa trên trạng thái
        is_hovered = algo_bg.collidepoint(mouse_pos)
        if is_hovered:
            bg_color = (255, 255, 240)
            border_color = (min(color[0] + 40, 255), min(color[1] + 40, 255), min(color[2] + 40, 255))
        elif self.selected_algo == name:
            bg_color = (255, 250, 220)
            border_color = color
        else:
            bg_color = (255, 255, 255)
            border_color = (220, 220, 220)
        
        # Vẽ background
        pygame.draw.rect(self.game.screen, bg_color, algo_bg, border_radius=5)
        pygame.draw.rect(self.game.screen, border_color, algo_bg, 1, border_radius=5)
        
        # Text
        name_text = self.fonts['name'].render(name, True, (30, 100, 30))
        self.game.screen.blit(name_text, (popup_rect.x + 25, top + 5))
        
        if len(desc) > 40:
            desc = desc[:37] + "..."
        desc_text = self.fonts['desc'].render(desc, True, (80, 80, 80))
        self.game.screen.blit(desc_text, (popup_rect.x + 25, top + 22))
        
        # Nút chọn
        btn = pygame.Rect(popup_rect.x + popup_rect.width - 75, top + 10, 50, 18)
        btn_color = color
        if btn.collidepoint(mouse_pos):
            btn_color = (min(color[0] + 30, 255), min(color[1] + 30, 255), min(color[2] + 30, 255))
        
        pygame.draw.rect(self.game.screen, btn_color, btn, border_radius=3)
        label = self.fonts['button'].render("CHỌN", True, (255, 255, 255))
        label_rect = label.get_rect(center=btn.center)
        self.game.screen.blit(label, label_rect)
        
        self.buttons.append((btn, name))