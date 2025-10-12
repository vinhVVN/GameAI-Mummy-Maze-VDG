import pygame
from src.settings import *


class Button:
    def __init__(self, x, y, width, height, text, command=None):
        self.rect = pygame.Rect(x, y, width, height)
        self._text = str(text)  # luôn convert sang string
        self.on_click = command
        self.is_hovered = False
        self.is_pressed = False

        self.bg = (60, 70, 85)
        self.bg_hover = (85, 100, 120)
        self.bg_pressed = (50, 60, 75)
        self.fg = COLOR_WHITE

        self.font = pygame.font.Font(None, 28)

    # property text: đảm bảo luôn ép về string khi set
    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = str(value)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                self.is_pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_pressed:
                self.is_pressed = False
                if self.is_hovered and self.on_click:
                    self.on_click()

    def draw(self, surface):
        # Shadow
        shadow_offset = 4 if not self.is_pressed else 2
        shadow_rect = self.rect.move(0, shadow_offset)
        pygame.draw.rect(surface, (20, 20, 25), shadow_rect, border_radius=10)

        # Button face
        if self.is_pressed:
            color = self.bg_pressed
        else:
            color = self.bg_hover if self.is_hovered else self.bg
        face_rect = self.rect.move(0, -1 if self.is_pressed else 0)
        pygame.draw.rect(surface, color, face_rect, border_radius=10)

        # Border
        border_color = (140, 170, 200) if self.is_hovered else (110, 130, 150)
        pygame.draw.rect(surface, border_color, face_rect, 1, border_radius=10)

        text_surface = self.font.render(self.text, True, self.fg)
        text_rect = text_surface.get_rect(center=face_rect.center)
        surface.blit(text_surface, text_rect)

class ImageButton:
    def __init__(self, x, y, width, height, image_path, on_click_func=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, height))
        self.on_click_func = on_click_func
        self.is_hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered and self.on_click_func:
                self.on_click_func()

    def draw(self, surface):
        # Làm mờ nút khi không di chuột qua
        alpha = 255 if self.is_hovered else 180
        self.image.set_alpha(alpha)
        surface.blit(self.image, self.rect.topleft)

class Panel:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.widgets = []
        self.font_title = pygame.font.Font(None, 40)

    def add_widget(self, widget):
        self.widgets.append(widget)

    def handle_event(self, event):
        for widget in self.widgets:
            widget.handle_event(event)

    def draw(self, surface):
        # Panel background with gradient-like layers
        pygame.draw.rect(surface, (45, 52, 63), self.rect)
        inner = self.rect.inflate(-12, -12)
        pygame.draw.rect(surface, (52, 61, 74), inner, border_radius=12)
        border = self.rect.inflate(-2, -2)
        pygame.draw.rect(surface, (70, 90, 110), border, 2, border_radius=14)

        # Title
        title_surf = self.font_title.render("Mummy Maze", True, COLOR_WHITE)
        title_rect = title_surf.get_rect(center=(self.rect.centerx, self.rect.top + 40))
        surface.blit(title_surf, title_rect)

        for widget in self.widgets:
            widget.draw(surface)
            
            
class LogPanel:
    def __init__(self, x, y, width, height):
        # Vị trí X cố định, chiều rộng sẽ thay đổi
        self.x = x
        self.y = y
        self.full_width = width
        self.height = height
        
        # rect hiện tại sẽ thay đổi chiều rộng
        self.rect = pygame.Rect(self.x, self.y, 0, self.height)
        self._is_animating = False
        
        self.font_title = pygame.font.Font(None, 24)
        self.font_content = pygame.font.SysFont("Consolas", 14)
        
        self.scroll_offset = 0
        self.line_height = self.font_content.get_linesize()
        self.total_content_height = 0
        self.summary_data = {}

    def update(self, is_expanded, speed=0.1):
        target_width = self.full_width if is_expanded else 0
        current_width = self.rect.width

        if abs(target_width - round(current_width)) > 1:
            self.rect.width += (target_width - current_width) * speed
            self._is_animating = True
        else:
            self.rect.width = target_width
            self._is_animating = False

    def is_animating(self):
        return self._is_animating
        
    def update_summary(self, data_dict):
        self.summary_data = data_dict

    def clear(self):
        self.scroll_offset = 0
        self.summary_data = {}

    def handle_event(self, event):
        if self.rect.width > 0 and self.rect.collidepoint(pygame.mouse.get_pos()):
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4: # Cuộn lên
                    self.scroll_offset = max(0, self.scroll_offset - self.line_height * 3)
                elif event.button == 5: # Cuộn xuống
                    max_scroll = max(0, self.total_content_height - self.rect.height + 100)
                    self.scroll_offset = min(max_scroll, self.scroll_offset + self.line_height * 3)
    
    def _draw_text_wrapped(self, surface, text, start_pos, font, color, max_width):
        words = text.split(' ')
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] < max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)
        
        x, y = start_pos
        for line in lines:
            if y >= 0 and y < surface.get_height():
                line_surface = font.render(line, True, color)
                surface.blit(line_surface, (x, y))
            y += font.get_linesize()
        return y - start_pos[1]

    def draw(self, surface, logger):
        if self.rect.width < 2: return
            
        # Vẽ nền và viền cho panel chính
        pygame.draw.rect(surface, (20, 30, 40), self.rect)
        pygame.draw.rect(surface, (60, 70, 80), self.rect, 2, border_radius=5)
        content_surface_height = max(self.rect.height, self.total_content_height + 50)
        content_surface = pygame.Surface((self.rect.width, content_surface_height), pygame.SRCALPHA)
        
        y_pos_on_subsurface = 10
        # Vẽ Summary
        y_pos_on_subsurface += self._draw_text_wrapped(content_surface, "Summary", (10, y_pos_on_subsurface), self.font_title, (255, 215, 0), self.rect.width - 20)
        for key, value in self.summary_data.items():
            y_pos_on_subsurface += self._draw_text_wrapped(content_surface, f"  {key}: {value}", (15, y_pos_on_subsurface), self.font_content, (220, 220, 220), self.rect.width - 20)
        y_pos_on_subsurface += self.line_height
        
        # Vẽ Live Log
        y_pos_on_subsurface += self._draw_text_wrapped(content_surface, "Live Log:", (10, y_pos_on_subsurface), self.font_title, (255, 215, 0), self.rect.width - 20)
        logs = logger.get_live_logs()
        for line in logs:
            color = (220, 220, 220)
            if "ACCEPT" in line or "Found" in line or "SUCCESS" in line: color = (100, 255, 100)
            elif "REJECT" in line or "FAILED" in line or "ERROR" in line: color = (255, 100, 100)
            elif "Cost" in line or "f=" in line or "Bước" in line: color = (100, 200, 255)
            y_pos_on_subsurface += self._draw_text_wrapped(content_surface, line, (10, y_pos_on_subsurface), self.font_content, color, self.rect.width - 20)
        
        # Cập nhật lại tổng chiều cao nội dung thực tế
        self.total_content_height = y_pos_on_subsurface
        
        visible_area = pygame.Rect(0, self.scroll_offset, self.rect.width, self.rect.height)
        surface.blit(content_surface, self.rect.topleft, area=visible_area)
        
        pygame.draw.rect(surface, (60, 70, 80), self.rect, 2, border_radius=5)


class TextInput:
    def __init__(self, x, y, width, height, placeholder="", font_size=26):
        self.rect = pygame.Rect(x, y, width, height)
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.text_color = COLOR_WHITE
        self.placeholder_color = (150, 150, 150)
        self.bg_color = (45, 52, 63)
        self.font = pygame.font.Font(None, font_size)
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.color = self.color_inactive

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Nếu người dùng click vào ô thì kích hoạt
            self.active = self.rect.collidepoint(event.pos)
            self.color = self.color_active if self.active else self.color_inactive

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                print(f"Input entered: {self.text}")
                self.active = False
                self.color = self.color_inactive
                return self.text
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
        return None

    def draw(self, surface):
        # Vẽ nền
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=8)

        # Vẽ border
        pygame.draw.rect(surface, self.color, self.rect, 2, border_radius=8)

        # Chọn text để hiển thị
        if self.text:
            text_surface = self.font.render(self.text, True, self.text_color)
        else:
            text_surface = self.font.render(self.placeholder, True, self.placeholder_color)

        # Vẽ text
        surface.blit(text_surface, (self.rect.x + 10, self.rect.y + (self.rect.height - text_surface.get_height()) // 2))
