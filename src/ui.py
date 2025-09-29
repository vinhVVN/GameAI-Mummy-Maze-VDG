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
