import pygame
import importlib
import time
from generated.helpers import Render, Input, Sound
from ui import Button, TextInput
from google import genai
from google.genai import types

class Main:

    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()

        self.font = pygame.font.Font(None, 30)

        self.client = genai.Client()
        self.prompt = self.get_prompt()
        self.load_default_program()
        self.get_new_chat()

    # Disk utils.
    def get_prompt(self):
        string = ''
        with open("prompt.txt", "r") as f:
            string = f.read()
        return string

    def write_program(self, text):
        name = str(int(time.time()))
        text = text.replace('```python', '')
        text = text.replace('```', '')
        with open("generated/" + name + ".py", 'w') as f:
            f.write('import math\n')
            f.write('import random\n')
            f.write('from generated.helpers import Render, Input, Sound\n\n')

            f.write(text)
        return name

    # LLM utils.
    def update_program_metadata(self):
        self.instructions = self.program.get_instructions()
        self.next_idea_buttons = self.get_next_idea_buttons(self.program.get_next_idea(), self.font)

    def load_default_program(self):
        module = importlib.import_module("generated.noise")
        self.program = module.Program()
        self.update_program_metadata()

    def load_new_program(self, chat, prompt):
        try:
            response = chat.send_message(prompt)
            name = self.write_program(response.text)
            # name = 'example'
            module = importlib.import_module("generated." + name)
            self.program = module.Program()
            self.update_program_metadata()
        except:
            import traceback
            traceback.print_exc()
            load_default_program()

    def get_new_chat(self, model="gemini-2.5-flash"):
        self.chat = self.client.chats.create(model=model, config=types.GenerateContentConfig(system_instruction=self.prompt))

    # UI utils.
    def get_next_idea_buttons(self, next_ideas, font):
        ideas = ["reboot", "keep dreaming"]
        ideas.extend(next_ideas)

        buttons = []
        x = 5
        for i in ideas:
            buttons.append(Button(i.lower(), pygame.Rect(x, 640, 795 / len(ideas) - 5, 40), font))
            x += 795 / len(ideas)
        return buttons

    def run(self):
        program_size = (800, 600)
        size = (1600, 900)
        screen = pygame.display.set_mode(size)
        clock = pygame.time.Clock()
        running = True

        computer = pygame.Surface((800, 800))
        background = pygame.image.load("background.png").convert_alpha()
        text_input = TextInput(pygame.Rect(5, 690, 790, 40), self.font, "(type...)")

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
                            self.load_new_program(self.chat, text_input.text)
                    else:
                        Input.key_down(pygame.key.name(event.key))
                elif event.type == pygame.KEYUP:
                    Input.key_up(pygame.key.name(event.key))
                elif event.type == pygame.MOUSEMOTION:
                    pos = pygame.mouse.get_pos()
                    pos = (pos[0] - 31, pos[1] - 45)

                    for b in self.next_idea_buttons:
                        b.check_hovered(pos)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    pos = (pos[0] - 31, pos[1] - 45)
                    
                    text_input.check_focused(pos)
                    for b in self.next_idea_buttons:
                        if b.check_hovered(pos):
                            if b.text == 'reboot':
                                self.load_default_program()
                                self.get_new_chat()              
                            else:
                                self.load_new_program(chat, b.text)

            # draw
            screen.blit(background, (0, 0))

            Render.clear_screen()

            try:
                self.program.update(dt / 1000)
                self.program.draw()
            except:
                import traceback
                traceback.print_exc()
                self.load_default_program()

            computer.fill((0, 0, 0))
            surf = pygame.transform.scale(Render.screen, program_size)
            computer.blit(surf, (0, 0))

            # Draw UI
            instruction_surf = self.font.render(self.instructions, False, (255, 255, 255))
            computer.blit(instruction_surf, (5, 605))

            for b in self.next_idea_buttons:
                b.draw(computer)

            text_input.draw(computer)

            screen.blit(computer, (31, 45))

            pygame.display.flip()
            dt = clock.tick(60)

if __name__ == "__main__":
    Main().run()
