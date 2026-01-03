import pygame
import math
import random
import numpy as np

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
    queue = []

    def get_events():
        q = Input.queue
        Input.queue = []
        return q

    def add_event(event):
        Input.queue.append(event)

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
        self.time = 0.0
        self.bones = []
        self.pulse = 0.0
        self.bone_count = 15
        self.glitch_y = 0
        self.corruption = 0.0

        # Skeleton structure: center point and radiating limbs
        for i in range(self.bone_count):
            self.bones.append({
                "angle": (i / self.bone_count) * 6.28,
                "length": random.randint(40, 100),
                "segments": random.randint(2, 4),
                "offset": random.random() * 6.28
            })

    def update(self, dt):
        self.time += dt
        self.pulse = math.sin(self.time * 3) * 0.5 + 0.5
        
        # Listen for keystrokes to "awaken" the marrow
        events = Input.get_events()
        if events:
            self.corruption += 0.05
            Sound.play_tone(100 + int(self.corruption * 500), 0.05)
            self.glitch_y = random.randint(0, 299)
            
        if self.corruption > 1.0:
            self.corruption = 1.0

    def draw(self):
        cx, cy = 200, 150
        
        # Draw the "Skull" (The Core)
        radius = 20 + int(math.sin(self.time * 2) * 2)
        Render.draw_circle(cx, cy, radius)
        # Eye sockets
        Render.draw_circle(cx - 8, cy - 2, 4, True)
        Render.draw_circle(cx + 8, cy - 2, 4, True)
        
        # Draw the ribcage/limbs
        for b in self.bones:
            angle = b["angle"] + math.sin(self.time + b["offset"]) * 0.2
            curr_x, curr_y = cx, cy
            
            # Move out from center
            curr_x += math.cos(angle) * radius
            curr_y += math.sin(angle) * radius
            
            for s in range(b["segments"]):
                seg_len = b["length"] / b["segments"]
                # Swaying movement
                next_angle = angle + math.sin(self.time * 2 + s) * (0.1 + self.corruption)
                next_x = curr_x + math.cos(next_angle) * seg_len
                next_y = curr_y + math.sin(next_angle) * seg_len
                
                Render.draw_line(int(curr_x), int(curr_y), int(next_x), int(next_y))
                
                # Joint markers
                Render.draw_circle(int(next_x), int(next_y), 2, True)
                
                curr_x, curr_y = next_x, next_y
                angle = next_angle

        # Nightmare effects
        if self.corruption > 0.3:
            for _ in range(int(self.corruption * 10)):
                rx = random.randint(0, 399)
                ry = random.randint(0, 299)
                Render.draw_text("CALCIUM", rx, ry)

        # Progression text
        if self.corruption < 0.9:
            Render.draw_text("THE BONES REMEMBER", 120, 20)
        else:
            Render.draw_text("THE MARROW SPEAKS", 120 + int(math.sin(self.time * 20)*2), 20)
            
        # Screen glitch
        if random.random() < self.corruption:
            Render.draw_line(0, self.glitch_y, 399, self.glitch_y)

    def get_instructions(self):
        return "Press keys to rattle the cage and awaken the marrow."

    def get_next_idea(self):
        return ["Fossilize", "Dancing limbs", "Shadow cast", "Dust ritual"]

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
                if event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    Input.add_event(pygame.key.name(event.key))
                    print(pygame.key.name(event.key))
                

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