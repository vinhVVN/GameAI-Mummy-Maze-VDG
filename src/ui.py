import pygame
from src.settings import *


class Button:
    def __init__(self, x, y, width, height, text, command=None):
        self.rect = pygame.Rect(x, y, width, height)
        self._text = str(text)  # luôn convert sang string
        self.on_click = command
        self.is_hovered = False

        self.bg = (70, 80, 90)
        self.bg_hover = (100, 110, 120)
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
            if self.is_hovered and self.on_click:
                print(f"Da nhan {self.text}")
                self.on_click()

    def draw(self, surface):
        color = self.bg_hover if self.is_hovered else self.bg
        pygame.draw.rect(surface, color, self.rect, border_radius=8)

        text_surface = self.font.render(self.text, True, self.fg)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)


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
        pygame.draw.rect(surface, COLOR_PANEL_BG, self.rect)
        title_surf = self.font_title.render("VINHSAYGEX", True, COLOR_WHITE)
        title_rect = title_surf.get_rect(center=(self.rect.centerx, self.rect.top + 40))
        surface.blit(title_surf, title_rect)

        for widget in self.widgets:
            widget.draw(surface)
