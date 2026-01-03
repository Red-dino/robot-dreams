import pygame
import numpy as np
from collections import defaultdict

class Render:
    screen = pygame.Surface((400, 300))
    font = None

    def draw_text(text, x, y):
        if not Render.font:
            Render.font = pygame.font.Font(None, 16)
        surf = Render.font.render(text, False, (255, 255, 255))
        Render.screen.blit(surf, (x, y))

    def draw_rect(x, y, w, h, filled=False):
        pygame.draw.rect(Render.screen, (255, 255, 255), (x, y, w, h), 0 if filled else 1)

    def draw_circle(x, y, radius, filled=False):
        pygame.draw.circle(Render.screen, (255, 255, 255), (x, y), radius, 0 if filled else 1)

    def draw_line(x1, y1, x2, y2):
        pygame.draw.line(Render.screen, (255, 255, 255), (x1, y1), (x2, y2))

    def turn_on_pixel(x, y):
        Render.screen.set_at((int(x), int(y)), (255, 255, 255))

    def clear_screen():
        Render.screen.fill((0, 0, 0))

class Input:
    key_pressed = defaultdict(bool)

    def is_key_pressed(key):
        return Input.key_pressed[key]

    def key_down(key):
        Input.key_pressed[key] = True

    def key_up(key):
        if key in Input.key_pressed:
            del Input.key_pressed[key]

class Sound:
    def _generate_tone(frequency, duration, sample_rate=44100, volume=0.1):
        """Generates a sine wave tone as a numpy array of signed 16-bit integers."""
        n_samples = int(round(duration * sample_rate))
        # Generate the time points
        t = np.linspace(0., duration, n_samples, endpoint=False)
        # Generate the sine wave
        waveform = np.sin(2 * np.pi * frequency * t)
        # Scale to 16-bit integer range and apply volume
        # Max value for int16 is 32767
        max_amplitude = 2**15 - 1
        samples = (waveform * max_amplitude * volume).astype(np.int16)
        return samples

    def play_tone(frequency, duration):
        sound = pygame.mixer.Sound(buffer=Sound._generate_tone(frequency, duration))

        sound.play()