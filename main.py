import pygame
import importlib
import time
from enum import Enum
from google import genai
from google.genai import types

from generated.helpers import Render, Input, Sound
from ui import Button, TextInput, OptionMenu
from util import DiskUtil, LlmUtil

class State(Enum):
    builder = 0
    loading_program = 1
    program_menu = 2

class Main:

    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()

        self.font = pygame.font.Font(None, 30)
        self.builder_button = Button("visualizer", pygame.Rect(0, 760, 400, 40), self.font)
        self.program_menu_button = Button("logged dreams", pygame.Rect(400, 760, 400, 40), self.font)

        self._set_state(State.builder)

        self.client = genai.Client()
        self.system_instructions = DiskUtil.read_system_instructions()
        self._create_new_chat()
        self._load_default_program()

        self.program_future = None

    def _set_state(self, new_state):
        self.state = new_state
        if self.state == State.program_menu:
            self._open_program_menu()
        self._recalculate_toggle_button_hover()

    def _load_program(self, program):
        self.program = program
        self.instructions = self.program.get_instructions()
        self.next_idea_buttons = self._get_next_idea_buttons(self.program.get_next_idea(), self.font)

    def _load_default_program(self):
        self._load_program(LlmUtil.load_default_program())

    def _load_new_program_async(self, prompt):
        if self.program_future:
            return

        self._set_state(State.loading_program)
        self.text_input.focused = False

        name = str(int(time.time())) + "".join(filter(str.isalnum, prompt))
        self.program_future = LlmUtil.load_new_program_async(self.chat, prompt, name)

    def _check_program_future(self):
        if not self.program_future:
            return

        if self.program_future.done():
            self._set_state(State.builder)
            program = self.program_future.result()
            self._load_program(program)
            self.program_future = None

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

    def _open_program_menu(self):
        self.program_menu = OptionMenu(pygame.Rect(39, 37, 800, 760), self.font, DiskUtil.get_saved_program_names())

    def _recalculate_toggle_button_hover(self):
        pos = pygame.mouse.get_pos()
        pos = (pos[0] - 39, pos[1] - 37)
        
        self.builder_button.hovered = self.state == State.builder or self.builder_button.check_hovered(pos) 
        self.program_menu_button.hovered = self.state == State.program_menu or self.program_menu_button.check_hovered(pos)

    def _handle_toggle_button_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self._recalculate_toggle_button_hover()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._recalculate_toggle_button_hover()
            if self.builder_button.hovered and self.state != State.builder:
                self._set_state(State.builder)
            elif self.program_menu_button.hovered and self.state != State.program_menu:
                self._set_state(State.program_menu)

    def _handle_builder_event(self, event):
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if self.text_input.is_focused():
                enter = self.text_input.take_input(event)
                if enter:
                    self._load_new_program_async(self.text_input.text)
        elif event.type == pygame.MOUSEMOTION:
            pos = pygame.mouse.get_pos()
            pos = (pos[0] - 39, pos[1] - 37)

            for b in self.next_idea_buttons:
                b.check_hovered(pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            pos = (pos[0] - 39, pos[1] - 37)
            
            self.text_input.check_focused(pos)
            for b in self.next_idea_buttons:
                if b.check_hovered(pos):
                    if b.text == 'reboot':
                        self._load_default_program()
                        self._create_new_chat()                                
                    else:
                        self._load_new_program_async(b.text)

    def _handle_game_event(self, event):
        if event.type == pygame.KEYDOWN:
            Input.key_down(pygame.key.name(event.key))
        elif event.type == pygame.KEYUP:
            Input.key_up(pygame.key.name(event.key))

    def run(self):
        program_size = (800, 600)
        size = (1600, 900)
        screen = pygame.display.set_mode(size)
        clock = pygame.time.Clock()
        running = True

        computer = pygame.Surface((800, 800))
        background = pygame.image.load("background.png").convert_alpha()
        self.text_input = TextInput(pygame.Rect(5, 690, 790, 40), self.font, "(click to type...)")

        dt = 0
        while running:
            # update
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return
                if self.state == State.builder:
                    consumed = self._handle_builder_event(event)
                    if not consumed:
                        self._handle_toggle_button_event(event)
                        self._handle_game_event(event)
                elif self.state == State.loading_program:
                    self._handle_game_event(event)
                elif self.state == State.program_menu:
                    self._handle_toggle_button_event(event)
                    name = self.program_menu.handle_event(event)
                    if name is not None:
                        self._load_program(LlmUtil.load_local_program(name))
                        self._set_state(State.builder)

            if self.state == State.loading_program:
                self._check_program_future()

            # draw
            screen.blit(background, (0, 0))

            Render.clear_screen()

            computer.fill((0, 0, 0))

            if self.state == State.builder or self.state == State.loading_program:
                try:
                    self.program.update(dt / 1000)
                    self.program.draw()
                except:
                    import traceback
                    traceback.print_exc()
                    self._load_default_program()

                surf = pygame.transform.scale(Render.screen, program_size)
                computer.blit(surf, (0, 0))

            if self.state == State.builder:
                instruction_surf = self.font.render(self.instructions, False, (255, 255, 255))
                computer.blit(instruction_surf, (5, 605))

                for b in self.next_idea_buttons:
                    b.draw(computer)

                self.text_input.draw(computer)
            elif self.state == State.loading_program:
                loading_surf = self.font.render("processing dream signal...", False, (255, 255, 255))
                computer.blit(loading_surf, (5, 605))

            if self.state == State.builder or self.state == State.program_menu:
                self.builder_button.draw(computer)
                self.program_menu_button.draw(computer)

            screen.blit(computer, (39, 37))

            if self.state == State.program_menu:
                self.program_menu.draw(screen)

            pygame.display.flip()
            dt = clock.tick(60)

if __name__ == "__main__":
    Main().run()
