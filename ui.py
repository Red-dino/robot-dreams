import pygame

class Button:

    def __init__(self, text, rect, font):
        self.text = text
        self.rect = rect
        self.font = font

        self.hovered = False
        self.hover_loc = False

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 0 if self.hovered else 1)
        text_surf = self.font.render(self.text, False, (0, 0, 0) if self.hovered else (255, 255, 255))
        surface.blit(text_surf, self.rect.topleft)

    def check_hovered(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        return self.hovered

class TextInput:

    def __init__(self, rect, font, empty_string):
        self.rect = rect
        self.font = font
        self.empty_string = empty_string
        self.text = ""

        self.focused = False

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 0 if self.focused else 1)
        text_surf = self.font.render(self.text if self.text else self.empty_string, False, (0, 0, 0) if self.focused else (255, 255, 255))
        surface.blit(text_surf, self.rect.topleft)

    def check_focused(self, mouse_pos):
        self.focused = self.rect.collidepoint(mouse_pos)

    def is_focused(self):
        return self.focused

    def take_input(self, key_event):
        if not self.focused:
            return False

        key_name = pygame.key.name(key_event.key)
        if key_name == 'backspace':
            if self.text:
                self.text = self.text[:-1]
        elif key_name == 'space':
            self.text += ' '
        elif key_name == 'return':
            return len(self.text) > 0
        elif len(key_name) == 1:
            self.text += key_name
        return False
        
        

        
    