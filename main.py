import pygame
import importlib
import time
from generated.helpers import Render, Input, Sound
from google import genai
from google.genai import types

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

def get_prompt():
    string = ''
    with open("prompt.txt", "r") as f:
        string = f.read()
    return string

def write_program(text):
    name = str(int(time.time()))
    text = text.replace('```python', '')
    text = text.replace('```', '')
    with open("generated/" + name + ".py", 'w') as f:
        f.write('import math\n')
        f.write('import random\n')
        f.write('from generated.helpers import Render, Input, Sound\n\n')

        f.write(text)
    return name

def get_and_load_program(chat, prompt):
    response = chat.send_message(prompt)
    name = write_program(response.text)
    # name = '1767410044'
    module = importlib.import_module("generated." + name)
    program = module.Program()
    print(program.get_instructions())
    print(program.get_next_idea())
    return program

def main():
    size = (800, 600)
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    running = True

    prompt = get_prompt()   

    client = genai.Client()
    chat = client.chats.create(model="gemini-2.5-flash-lite", config=types.GenerateContentConfig(system_instruction=prompt))

    program = get_and_load_program(chat, "flying kite")

    dt = 0
    while running:
        # update
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if pygame.key.name(event.key) == 'g':
                    program = get_and_load_program(chat, "Keep dreaming.")

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