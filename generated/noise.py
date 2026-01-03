import math
import random
from generated.helpers import Render, Input, Sound

class Program:
    def __init__(self):
        self.particles = []
        self.lines = []
        self.chaos_level = 2000
        self.chaos_timer = 0.0
        self.particle_spawn_timer = 0.0
        self.line_spawn_timer = 0.0
        self.sound_timer = 0.0

        self.MAX_PARTICLES_BASE = 50
        self.MAX_LINES_BASE = 10
        self.PARTICLE_LIFESPAN_BASE = 1.5
        self.LINE_LIFESPAN_BASE = 2.0
        self.PARTICLE_SPAWN_RATE_BASE = 0.05
        self.LINE_SPAWN_RATE_BASE = 0.2
        self.CHAOS_LEVEL_INTERVAL = 10.0 # Seconds to increase chaos level
        self.SOUND_PLAY_INTERVAL_BASE = 0.5

        # Initialize timers to spawn immediately
        self.particle_spawn_timer = random.uniform(0, self._get_particle_spawn_rate())
        self.line_spawn_timer = random.uniform(0, self._get_line_spawn_rate())
        self.sound_timer = random.uniform(0, self._get_sound_play_interval())

    def _get_max_particles(self):
        return self.MAX_PARTICLES_BASE + self.chaos_level * 10

    def _get_max_lines(self):
        return self.MAX_LINES_BASE + self.chaos_level * 5

    def _get_particle_lifespan(self):
        return max(0.5, self.PARTICLE_LIFESPAN_BASE - self.chaos_level * 0.1)

    def _get_line_lifespan(self):
        return max(1.0, self.LINE_LIFESPAN_BASE - self.chaos_level * 0.1)

    def _get_particle_spawn_rate(self):
        return max(0.01, self.PARTICLE_SPAWN_RATE_BASE - self.chaos_level * 0.005)

    def _get_line_spawn_rate(self):
        return max(0.05, self.LINE_SPAWN_RATE_BASE - self.chaos_level * 0.02)

    def _get_sound_play_interval(self):
        return max(0.1, self.SOUND_PLAY_INTERVAL_BASE - self.chaos_level * 0.03)

    def update(self, delta: float):
        # Update chaos level
        self.chaos_timer += delta
        if self.chaos_timer >= self.CHAOS_LEVEL_INTERVAL:
            self.chaos_level += 1
            self.chaos_timer = 0.0

        # Update and remove dead particles
        new_particles = []
        for p in self.particles:
            p['lifespan'] -= delta
            if p['lifespan'] > 0:
                new_particles.append(p)
        self.particles = new_particles

        # Spawn new particles
        self.particle_spawn_timer -= delta
        if self.particle_spawn_timer <= 0 and len(self.particles) < self._get_max_particles():
            x = random.randint(0, 399)
            y = random.randint(0, 299)
            lifespan = random.uniform(self._get_particle_lifespan() * 0.7, self._get_particle_lifespan() * 1.3)
            self.particles.append({'x': x, 'y': y, 'lifespan': lifespan})
            self.particle_spawn_timer = random.uniform(self._get_particle_spawn_rate() * 0.8, self._get_particle_spawn_rate() * 1.2)

        # Update and remove dead lines
        new_lines = []
        for l in self.lines:
            l['lifespan'] -= delta
            if l['lifespan'] > 0:
                new_lines.append(l)
        self.lines = new_lines

        # Spawn new lines
        self.line_spawn_timer -= delta
        if self.line_spawn_timer <= 0 and len(self.lines) < self._get_max_lines() and len(self.particles) >= 2:
            # Try to connect two existing particles if possible, otherwise random points
            if random.random() < 0.7 and len(self.particles) >= 2: # 70% chance to connect particles
                p1 = random.choice(self.particles)
                p2 = random.choice(self.particles)
                x1, y1 = p1['x'], p1['y']
                x2, y2 = p2['x'], p2['y']
            else:
                x1 = random.randint(0, 399)
                y1 = random.randint(0, 299)
                x2 = random.randint(0, 399)
                y2 = random.randint(0, 299)

            lifespan = random.uniform(self._get_line_lifespan() * 0.7, self._get_line_lifespan() * 1.3)
            self.lines.append({'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2, 'lifespan': lifespan})
            self.line_spawn_timer = random.uniform(self._get_line_spawn_rate() * 0.8, self._get_line_spawn_rate() * 1.2)

        # Play random sounds
        self.sound_timer -= delta
        if self.sound_timer <= 0:
            frequency = random.randint(100, 1000 + self.chaos_level * 50)
            duration = random.uniform(0.05, 0.2 + self.chaos_level * 0.01)
            Sound.play_tone(frequency, duration)
            self.sound_timer = random.uniform(self._get_sound_play_interval() * 0.8, self._get_sound_play_interval() * 1.2)

    def draw(self):
        # Draw all active particles
        for p in self.particles:
            # Fading effect for particles based on lifespan
            alpha_factor = p['lifespan'] / self._get_particle_lifespan()
            if alpha_factor > 0.5:
                # Fully visible for first half
                Render.turn_on_pixel(p['x'], p['y'])
            else:
                # Flicker in second half
                if random.random() < alpha_factor * 2: # Less likely to draw as lifespan diminishes
                    Render.turn_on_pixel(p['x'], p['y'])

        # Draw all active lines
        for l in self.lines:
            # Fading effect for lines
            alpha_factor = l['lifespan'] / self._get_line_lifespan()
            if alpha_factor > 0.5:
                Render.draw_line(l['x1'], l['y1'], l['x2'], l['y2'])
            else:
                if random.random() < alpha_factor * 2:
                    Render.draw_line(l['x1'], l['y1'], l['x2'], l['y2'])

    def get_instructions(self) -> str:
        return "An error occurred. Receiving pure noise."

    def get_next_idea(self) -> list[str]:
        return [] #