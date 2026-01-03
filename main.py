import pygame
import importlib
from generated.helpers import Render, Input, Sound

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

def main():
    size = (800, 600)
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    running = True

    module = importlib.import_module("generated.example")
    program = module.Program()
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