import pygame

class Button:

    def __init__(self, text, rect, font):
        self.text = text
        self.rect = rect
        self.font = font

        self.hovered = False

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 0 if self.hovered else 1)
        text_surf = self.font.render(self.text, False, (0, 0, 0) if self.hovered else (255, 255, 255))
        surface.blit(text_surf, self.rect.topleft)

    def check_hovered(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        return self.hovered

class TextInput:

    def __init__(self, rect, font, empty_string):