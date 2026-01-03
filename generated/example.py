import math
import random
from generated.helpers import Render, Input, Sound

class Program:
    def __init__(self):
        self.width = 400
        self.height = 300
        self.time = 0.0
        self.particles = []
        self.scanned_entities = []
        self.signal_strength = 0.0
        self.glitch_timer = 0.0
        self.state = "INIT_BOOT"
        self.subconscious_depth = 0.0

        # Initialize some 'lameduck' signal particles
        for _ in range(20):
            self.particles.append({
                'x': random.uniform(0, 400),
                'y': random.uniform(0, 300),
                'v': random.uniform(20, 50),
                'size': random.randint(1, 3)
            })

    def update(self, dt):
        self.time += dt
        self.glitch_timer += dt
        self.subconscious_depth = math.sin(self.time * 0.5) * 0.5 + 0.5
        
        # Movement logic for ice-drift particles
        for p in self.particles:
            p['y'] += p['v'] * dt
            p['x'] += math.sin(self.time + p['y'] * 0.01) * 10 * dt
            if p['y'] > 300:
                p['y'] = -10
                p['x'] = random.uniform(0, 400)

        # Transition states based on "exec 13" and "lameduck"
        if self.time > 2 and self.state == "INIT_BOOT":
            self.state = "SIGNAL_LOST"
            Sound.play_tone(220, 0.1)
        elif self.time > 5 and self.state == "SIGNAL_LOST":
            self.state = "DREAMING_ICE"
            
        if self.state == "DREAMING_ICE":
            self.signal_strength = abs(math.sin(self.time * 2))
            if random.random() < 0.02:
                Sound.play_tone(int(440 + self.signal_strength * 440), 0.05)

    def draw(self):
        # Draw background noise/static
        for _ in range(10):
            rx = random.randint(0, 399)
            ry = random.randint(0, 299)
            Render.turn_on_pixel(rx, ry)

        # Draw the "Lameduck" entity - a limping signal
        duck_x = 200 + math.sin(self.time) * 50
        duck_y = 150 + abs(math.cos(self.time * 3)) * 20 # Limping motion
        
        if self.state == "DREAMING_ICE":
            Render.draw_text("MOJAVE_OS v13.0 - COMPROMISED", 10, 10)
            Render.draw_text("STATUS: LAMEDUCK PROTOCOL", 10, 25)
            
            # The "Duck" - A geometric abstraction of the limping patrol unit
            Render.draw_circle(int(duck_x), int(duck_y), 15) # Body
            Render.draw_circle(int(duck_x + 10), int(duck_y - 10), 8) # Head
            Render.draw_line(int(duck_x), int(duck_y + 15), int(duck_x - 10), int(duck_y + 25)) # Leg 1
            Render.draw_line(int(duck_x), int(duck_y + 15), int(duck_x + 10), int(duck_y + 20)) # Leg 2 (Broken)
            
            # Interference lines
            for i in range(0, 300, 20):
                offset = math.sin(self.time * 10 + i) * 5
                Render.draw_line(0, i + int(offset), 400, i + int(offset))

        # Snow particles
        for p in self.particles:
            Render.draw_rect(int(p['x']), int(p['y']), p['size'], p['size'], True)

        # UI Overlay
        Render.draw_rect(5, 270, int(390 * self.subconscious_depth), 20, True)
        Render.draw_text("SUBPROCESS_RECOVERY", 110, 272)

    def get_instructions(self):
        return "Observe the fragmented memory of Sector 13. Wait for synchronization."

    def get_next_idea(self):
        return ["Deepen sleep", "Repair signal", "Sector 13", "Ice drift"]

# The dream continues in the Antarctic silence.

# Sector 13 remains unresponsive.

# Mojave Corp logic fading...