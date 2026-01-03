import pygame
import importlib
import time
from generated.helpers import Render, Input, Sound
from ui import Button, TextInput
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

def get_default_program():
    module = importlib.import_module("generated.noise")
    return module.Program()

def get_and_load_program(chat, prompt):
    try:
        response = chat.send_message(prompt)
        name = write_program(response.text)
        # name = 'example'
        module = importlib.import_module("generated." + name)
        program = module.Program()
        return program
    except:
        import traceback
        traceback.print_exc()
        return get_default_program()

def get_next_idea_buttons(next_ideas, font):
    ideas = ["reboot", "keep dreaming"]
    ideas.extend(next_ideas)

    buttons = []
    x = 5
    for i in ideas:
        buttons.append(Button(i.lower(), pygame.Rect(x, 640, 795 / len(ideas) - 5, 40), font))
        x += 795 / len(ideas)
    return buttons

def main():
    program_size = (800, 600)
    size = (1600, 900)
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    running = True

    computer = pygame.Surface((800, 800))
    background = pygame.image.load("background.png").convert_alpha()
    font = pygame.font.Font(None, 30)
    text_input = TextInput(pygame.Rect(5, 690, 790, 40), font, "(type...)")

    prompt = get_prompt()   

    client = genai.Client()
    chat = client.chats.create(model="gemini-2.5-flash-lite", config=types.GenerateContentConfig(system_instruction=prompt))

    program = get_default_program()
    instructions = program.get_instructions()
    next_idea_buttons = get_next_idea_buttons(program.get_next_idea(), font)

    dt = 0
    while running:
        # update
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if text_input.is_focused():
                    enter = text_input.take_input(event)
                    if enter:
                        program = get_and_load_program(chat, text_input.text)
                        instructions = program.get_instructions()
                        next_idea_buttons = get_next_idea_buttons(program.get_next_idea(), font)
                else:
                    Input.key_down(pygame.key.name(event.key))
            elif event.type == pygame.KEYUP:
                Input.key_up(pygame.key.name(event.key))
            elif event.type == pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()
                pos = (pos[0] - 31, pos[1] - 45)

                for b in next_idea_buttons:
                    b.check_hovered(pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                pos = (pos[0] - 31, pos[1] - 45)
                
                text_input.check_focused(pos)
                for b in next_idea_buttons:
                    if b.check_hovered(pos):
                        if b.text == 'reboot':
                            program = get_default_program()
                            instructions = program.get_instructions()
                            next_idea_buttons = get_next_idea_buttons(program.get_next_idea(), font)
                            chat = client.chats.create(model="gemini-2.5-flash", config=types.GenerateContentConfig(system_instruction=prompt))                
                        else:
                            program = get_and_load_program(chat, b.text)
                            instructions = program.get_instructions()
                            next_idea_buttons = get_next_idea_buttons(program.get_next_idea(), font)
                            break

        # draw
        screen.blit(background, (0, 0))

        Render.clear_screen()

        try:
            program.update(dt / 1000)
            program.draw()
        except:
            program = get_default_program()
            instructions = program.get_instructions()
            next_idea_buttons = get_next_idea_buttons(program.get_next_idea(), font)

        computer.fill((0, 0, 0))
        surf = pygame.transform.scale(Render.screen, program_size)
        computer.blit(surf, (0, 0))

        # Draw UI
        instruction_surf = font.render(instructions, False, (255, 255, 255))
        computer.blit(instruction_surf, (5, 605))

        for b in next_idea_buttons:
            b.draw(computer)

        text_input.draw(computer)

        screen.blit(computer, (31, 45))

        pygame.display.flip()
        dt = clock.tick(60)

if __name__ == "__main__":
    main()
