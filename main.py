import pygame
import numpy as np
import math
import random
from collections import defaultdict

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

class Render:
    screen = pygame.Surface((400, 300))
    font = pygame.font.Font(None, 16)

    def draw_text(text, x, y):
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

class Program:
    def __init__(self):
        pass

    def update(self, dt):
        pass

    def draw(self):
        pass

    def get_instructions(self):
        return ""

    def get_next_idea(self):
        return []

def main():
    size = (800, 600)
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    running = True

    program = Program()
    print(program.get_instructions())

    dt = 0

    while running:
        # update
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                Input.key_down(pygame.key.name(event.key))
            elif event.type == pygame.KEYUP:
                Input.key_up(pygame.key.name(event.key))

        program.update(dt / 1000)

        # draw
        Render.clear_screen()

        program.draw()

        surf = pygame.transform.scale(Render.screen, size)
        screen.blit(surf, (0, 0))

        pygame.display.flip()
        dt = clock.tick(60)

if __name__ == "__main__":
    main()