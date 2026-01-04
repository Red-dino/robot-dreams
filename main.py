import pygame
import importlib
import time
from google import genai
from google.genai import types

from generated.helpers import Render, Input, Sound
from ui import Button, TextInput
from util import DiskUtil, LlmUtil

class Main:

    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()

        self.font = pygame.font.Font(None, 30)

        self.client = genai.Client()
        self.system_instructions = DiskUtil.read_system_instructions()
        self._create_new_chat()
        self._load_default_program()

    def _load_program(self, program):
        self.program = program
        self.instructions = self.program.get_instructions()
        self.next_idea_buttons = self._get_next_idea_buttons(self.program.get_next_idea(), self.font)

    def _load_default_program(self):
        self._load_program(LlmUtil.load_default_program())

    def _load_new_program(self, prompt):
        name = "".join(filter(str.isalnum, prompt)) + str(int(time.time()))
        program = LlmUtil.load_new_program(self.chat, prompt, name)
        self._load_program(program)

    def _create_new_chat(self):
        self.chat = LlmUtil.create_new_chat(self.client, self.system_instructions)

    def _get_next_idea_buttons(self, next_ideas, font):
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
                            self._load_new_program(text_input.text)
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
                                self._load_default_program()
                                self._create_new_chat()                                
                            else:
                                self._load_new_program(b.text)

            # draw
            screen.blit(background, (0, 0))

            Render.clear_screen()

            try:
                self.program.update(dt / 1000)
                self.program.draw()
            except:
                import traceback
                traceback.print_exc()
                self._load_default_program()

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
