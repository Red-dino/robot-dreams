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
        text_surf = self.font.render(self.text if self.text or self.focused else self.empty_string, False, (0, 0, 0) if self.focused else (255, 255, 255))
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

class OptionMenu:

    def __init__(self, rect, font, options):
        self.rect = rect
        self.font = font
        self.options = options

        self.surf = pygame.Surface(rect.size)
        self._build_surfaces()
        self._recalculate_hover()

    def _build_surfaces(self):
        self.header_surf = self.font.render("Saved dreams:", False, (255, 255, 255))
        self.options_surf = pygame.Surface((self.rect.width, self.header_surf.get_height() * (1 + len(self.options))))

        y = 0
        for option in self.options:
            option_surf = self.font.render(option, False, (255, 255, 255))
            self.options_surf.blit(option_surf, (0, y))
            y += self.header_surf.get_height()

    def draw(self, surface):
        self.surf.fill((0, 0, 0))
        
        self.surf.blit(self.options_surf, (0, self.header_surf.get_height()))

        if self.hovered_option_i is not None:
            hover_rect = pygame.Rect(0, self.header_surf.get_height() * (self.hovered_option_i + 1), self.rect.width, self.header_surf.get_height())
            pygame.draw.rect(self.surf, (255, 255, 255), hover_rect)
            hovered_option = self.font.render(self.options[self.hovered_option_i], False, (0, 0, 0))
            self.surf.blit(hovered_option, hover_rect)

        pygame.draw.rect(self.surf, (0, 0, 0), (0, 0, self.rect.width, self.header_surf.get_height()))
        self.surf.blit(self.header_surf, (0, 0))

        surface.blit(self.surf, self.rect)

    def _recalculate_hover(self):
        self.hovered_option_i = None

        pos = pygame.mouse.get_pos()

        if not self.rect.collidepoint(pos):
            return

        adjusted_y = pos[1] - self.rect.y - self.header_surf.get_height()

        i = adjusted_y // self.header_surf.get_height()
        if i >= 0 and i < len(self.options) and adjusted_y < self.rect.height:
            self.hovered_option_i = i

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self._recalculate_hover()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._recalculate_hover()
            if self.hovered_option_i is not None:
                return self.options[self.hovered_option_i]

        return None



