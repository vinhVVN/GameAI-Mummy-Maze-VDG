# popup.py
import pygame
import os
from src.config import GameConfig
from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BLACK

class AlgorithmPopup:
    def __init__(self, game):
        self.game = game
        # Điều chỉnh kích thước popup cho phù hợp với màn hình
        self.width = min(650, SCREEN_WIDTH - 40)  # Giảm kích thước để phù hợp với 800px
        self.height = min(400, SCREEN_HEIGHT - 40)  # Giảm kích thước để phù hợp với 480px
        self.selected_algo = game.player_algo
        self.scroll_offset = 0
        self.buttons = []
        self.scroll_speed = 30  # Tốc độ scroll
        
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
            height += 30  # Category height (tăng một chút)
            height += len(algorithms) * 60  # Algorithm items height (tăng để dễ nhìn)
        height += 20  # Thêm padding cuối
        return height
    
    def show(self):
        """Hiển thị popup và trả về thuật toán được chọn"""
        content_height = self.calculate_content_height()
        visible_height = self.height - 120  # Tăng header và footer space
        max_scroll = max(0, content_height - visible_height)
        
        # Debug print
        print(f"Content height: {content_height}, Visible height: {visible_height}, Max scroll: {max_scroll}")
        
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            # Vẽ trước để xây dựng self.buttons cho vòng xử lý sự kiện
            self.buttons = []
            self.draw(mouse_pos)

            # Xử lý events (sau khi đã có self.buttons)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return self.selected_algo
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return self.selected_algo
                    elif event.key == pygame.K_RETURN and self.selected_algo:
                        return self.selected_algo
                    elif event.key == pygame.K_UP:
                        self.scroll_offset = max(0, self.scroll_offset - self.scroll_speed)
                    elif event.key == pygame.K_DOWN:
                        self.scroll_offset = min(max_scroll, self.scroll_offset + self.scroll_speed)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for btn_rect, algo_name in self.buttons:
                            if btn_rect.collidepoint(mouse_pos):
                                return algo_name
                    elif event.button == 4:  # Scroll up
                        self.scroll_offset = max(0, self.scroll_offset - self.scroll_speed)
                    elif event.button == 5:  # Scroll down
                        self.scroll_offset = min(max_scroll, self.scroll_offset + self.scroll_speed)
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
        overlay.fill((0, 0, 0, 160))
        self.game.screen.blit(overlay, (0, 0))
        
        # Vẽ popup container
        popup_rect = pygame.Rect(
            (SCREEN_WIDTH - self.width) // 2,
            (SCREEN_HEIGHT - self.height) // 2,
            self.width, self.height
        )
        
        # Bóng đổ
        shadow_rect = popup_rect.move(0, 8)
        pygame.draw.rect(self.game.screen, (20, 20, 30), shadow_rect, border_radius=16)
        
        # Nền popup
        pygame.draw.rect(self.game.screen, (250, 250, 252), popup_rect, border_radius=16)
        pygame.draw.rect(self.game.screen, (110, 150, 220), popup_rect, 2, border_radius=16)
        
        # Header
        header_rect = pygame.Rect(popup_rect.x, popup_rect.y, popup_rect.width, 56)
        pygame.draw.rect(self.game.screen, (70, 130, 230), header_rect, border_radius=16)
        title_text = self.fonts['title'].render("CHỌN THUẬT TOÁN", True, (255, 255, 255))
        self.game.screen.blit(title_text, (popup_rect.centerx - title_text.get_width()//2, popup_rect.y + 16))
        
        # Content area
        visible_height = self.height - 120  # Đồng bộ với tính toán trong show()
        content_bg_rect = pygame.Rect(popup_rect.x + 16, popup_rect.y + 70, popup_rect.width - 32, visible_height)
        pygame.draw.rect(self.game.screen, (245, 248, 250), content_bg_rect, border_radius=10)
        
        # Vẽ nội dung có thể cuộn
        self.draw_scrollable_content(popup_rect, mouse_pos, visible_height)
        
        # Vẽ scroll indicator nếu cần
        content_height = self.calculate_content_height()
        if content_height > visible_height:
            self.draw_scroll_indicator(popup_rect, visible_height, content_height)
        
        # Footer
        footer_rect = pygame.Rect(popup_rect.x, popup_rect.y + self.height - 44, popup_rect.width, 44)
        pygame.draw.rect(self.game.screen, (240, 245, 250), footer_rect, border_radius=12)
        
        # Hiển thị thuật toán đã chọn
        if self.selected_algo:
            selected_text = f"ĐÃ CHỌN: {self.selected_algo}"
            selected_surface = self.fonts['category'].render(selected_text, True, (0, 80, 180))
            self.game.screen.blit(selected_surface, (popup_rect.centerx - selected_surface.get_width()//2, popup_rect.y + self.height - 28))
        
        # Hướng dẫn
        hint_text = "ESC: Thoát • ENTER: Xác nhận • ↑↓ hoặc Mouse Wheel: Cuộn"
        hint_surface = self.fonts['desc'].render(hint_text, True, (120, 120, 140))
        self.game.screen.blit(hint_surface, (popup_rect.centerx - hint_surface.get_width()//2, popup_rect.y + self.height - 14))
    
    def draw_scrollable_content(self, popup_rect, mouse_pos, visible_height):
        """Vẽ nội dung có thể cuộn"""
        current_y = -self.scroll_offset
        content_start_y = popup_rect.y + 70  # Đồng bộ với content area
        
        for category, algorithms in GameConfig.ALGORITHM_CATEGORIES.items():
            # Vẽ category nếu trong view
            category_top = content_start_y + current_y
            if category_top + 30 > content_start_y and category_top < content_start_y + visible_height:
                category_bg = pygame.Rect(popup_rect.x + 22, category_top, popup_rect.width - 44, 28)
                pygame.draw.rect(self.game.screen, (200, 220, 245), category_bg, border_radius=6)
                category_text = self.fonts['category'].render(category, True, (20, 60, 140))
                self.game.screen.blit(category_text, (category_bg.x + 10, category_bg.y + 6))
            
            current_y += 30
            
            # Vẽ algorithms
            for name, desc, color in algorithms:
                algo_top = content_start_y + current_y
                if algo_top + 60 > content_start_y and algo_top < content_start_y + visible_height:
                    self.draw_algorithm_item(popup_rect, algo_top, name, desc, color, mouse_pos)
                
                current_y += 60
    
    def draw_scroll_indicator(self, popup_rect, visible_height, content_height):
        """Vẽ thanh scroll indicator"""
        # Vẽ thanh scroll ở bên phải
        scrollbar_x = popup_rect.right - 20
        scrollbar_y = popup_rect.y + 70
        scrollbar_height = visible_height
        scrollbar_width = 8
        
        # Background của scrollbar
        scrollbar_bg = pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
        pygame.draw.rect(self.game.screen, (200, 200, 200), scrollbar_bg, border_radius=4)
        
        # Tính toán vị trí và kích thước của scroll thumb
        max_scroll = content_height - visible_height
        if max_scroll > 0:
            scroll_ratio = self.scroll_offset / max_scroll
            thumb_height = max(20, int(scrollbar_height * visible_height / content_height))
            thumb_y = scrollbar_y + int((scrollbar_height - thumb_height) * scroll_ratio)
            
            # Vẽ scroll thumb
            thumb_rect = pygame.Rect(scrollbar_x, thumb_y, scrollbar_width, thumb_height)
            pygame.draw.rect(self.game.screen, (100, 100, 100), thumb_rect, border_radius=4)
    
    def draw_algorithm_item(self, popup_rect, top, name, desc, color, mouse_pos):
        """Vẽ một item thuật toán"""
        algo_bg = pygame.Rect(popup_rect.x + 26, top, popup_rect.width - 52, 55)  # Tăng chiều cao item
        
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
        pygame.draw.rect(self.game.screen, (10, 10, 20), algo_bg.move(0, 3), border_radius=10)
        pygame.draw.rect(self.game.screen, bg_color, algo_bg, border_radius=10)
        pygame.draw.rect(self.game.screen, border_color, algo_bg, 1, border_radius=10)
        
        # Text
        name_text = self.fonts['name'].render(name, True, (30, 100, 30))
        self.game.screen.blit(name_text, (algo_bg.x + 12, algo_bg.y + 8))
        
        if len(desc) > 60:
            desc = desc[:57] + "..."
        desc_text = self.fonts['desc'].render(desc, True, (80, 80, 80))
        self.game.screen.blit(desc_text, (algo_bg.x + 12, algo_bg.y + 26))
        
        # Nút chọn
        btn = pygame.Rect(algo_bg.right - 70, algo_bg.y + 14, 58, 22)
        btn_color = color
        if btn.collidepoint(mouse_pos):
            btn_color = (min(color[0] + 30, 255), min(color[1] + 30, 255), min(color[2] + 30, 255))
        
        pygame.draw.rect(self.game.screen, btn_color, btn, border_radius=6)
        label = self.fonts['button'].render("CHỌN", True, (255, 255, 255))
        label_rect = label.get_rect(center=btn.center)
        self.game.screen.blit(label, label_rect)
        
        # Cho phép click cả hàng thuật toán để chọn
        self.buttons.append((algo_bg, name))
        self.buttons.append((btn, name))