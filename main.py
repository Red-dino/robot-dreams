import pygame
import importlib
import time
from generated.helpers import Render, Input, Sound
from ui import Button
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
    try:
        response = chat.send_message(prompt)
        name = write_program(response.text)
        # name = 'example'
        module = importlib.import_module("generated." + name)
        program = module.Program()
        return program
    except Exception:
        import traceback
        traceback.print_exc()
        module = importlib.import_module("generated.noise")
        program = module.Program()
        return program

def get_next_idea_buttons(next_ideas, font):
    ideas = ["Keep dreaming"]
    ideas.extend(next_ideas)

    buttons = []
    x = 5
    for i in ideas:
        buttons.append(Button(i, pygame.Rect(x, 640, 795 / len(ideas) - 5, 40), font))
        x += 795 / len(ideas)
    return buttons

def main():
    program_size = (800, 600)
    size = (800, 800)
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    running = True

    prompt = get_prompt()   

    client = genai.Client()
    chat = client.chats.create(model="gemini-2.5-flash", config=types.GenerateContentConfig(system_instruction=prompt))

    font = pygame.font.Font(None, 30)

    program = get_and_load_program(chat, "... who are you?")
    instructions = program.get_instructions()
    next_idea_buttons = get_next_idea_buttons(program.get_next_idea(), font)

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
            elif event.type == pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()
                
                for b in next_idea_buttons:
                    b.check_hovered(pos)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                
                for b in next_idea_buttons:
                    if b.check_hovered(pos):
                        program = get_and_load_program(chat, b.text)
                        instructions = program.get_instructions()
                        next_idea_buttons = get_next_idea_buttons(program.get_next_idea(), font)
                        break

        program.update(dt / 1000)

        # draw
        screen.fill((0, 0, 0))

        Render.clear_screen()

        program.draw()

        surf = pygame.transform.scale(Render.screen, program_size)
        screen.blit(surf, (0, 0))

        # Draw UI
        instruction_surf = font.render(instructions, False, (255, 255, 255))
        screen.blit(instruction_surf, (5, 605))

        for b in next_idea_buttons:
            b.draw(screen)

        pygame.display.flip()
        dt = clock.tick(60)

if __name__ == "__main__":
    main()
