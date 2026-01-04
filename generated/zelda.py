import math
import random
from generated.helpers import Render, Input, Sound

import random
import math

# Base class for all entities in the dream
class Entity:
    def __init__(self, x, y, max_age=float('inf')):
        self.x = x
        self.y = y
        self.age = 0.0
        self.max_age = max_age
        self.is_active = True

    def update(self, delta: float):
        self.age += delta
        if self.age >= self.max_age:
            self.is_active = False

    def draw(self):
        pass # To be implemented by subclasses

    def is_alive(self):
        return self.is_active

# The dreaming Hero, embodying the player's presence
class Hero(Entity):
    def __init__(self):
        super().__init__(200, 150) # Start in the center
        self.dx = 0.0
        self.dy = 0.0
        self.speed = 80.0 # Pixels per second
        self.radius = 8
        self.power = 0 # Collected rupees increase power
        self.resilience = 3.0 # Current health (starts with 3 hearts, float for regeneration)
        self.max_resilience = 3.0 # Max health, increases with Heart Shards
        self.invincible_timer = 0.0
        self.invincible_duration = 1.0 # Seconds of invincibility after hit
        self.hit_flash_timer = 0.0
        self.hit_flash_duration = 0.1 # Visual flash duration

    def update(self, delta: float):
        super().update(delta)

        # Handle movement input
        self.dx = 0.0
        self.dy = 0.0
        if Input.is_key_pressed('w'): self.dy -= 1
        if Input.is_key_pressed('s'): self.dy += 1
        if Input.is_key_pressed('a'): self.dx -= 1
        if Input.is_key_pressed('d'): self.dx += 1
        
        # Normalize diagonal movement
        if self.dx != 0 and self.dy != 0:
            mag = math.sqrt(self.dx * self.dx + self.dy * self.dy)
            self.dx /= mag
            self.dy /= mag

        self.x += self.dx * self.speed * delta
        self.y += self.dy * self.speed * delta

        # Keep hero within screen bounds
        self.x = max(self.radius, min(399 - self.radius, self.x))
        self.y = max(self.radius, min(299 - self.radius, self.y))

        # Update invincibility timer
        if self.invincible_timer > 0:
            self.invincible_timer -= delta
            if self.invincible_timer < 0:
                self.invincible_timer = 0

        # Update hit flash timer
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= delta
            if self.hit_flash_timer < 0:
                self.hit_flash_timer = 0

        # Regenerate resilience slowly if not at max
        if self.resilience < self.max_resilience:
            self.resilience += delta * 0.5 # Recover half a heart per second
            self.resilience = min(self.resilience, self.max_resilience)

    def take_damage(self, amount: int):
        if self.invincible_timer <= 0:
            self.resilience -= amount
            Sound.play_tone(150, 0.1) # Damage sound
            self.invincible_timer = self.invincible_duration
            self.hit_flash_timer = self.hit_flash_duration
            if self.resilience <= 0:
                # If resilience hits 0, trigger a major visual/sound effect
                # Then reset resilience to 1 (or something low) to allow continuation
                Sound.play_tone(100, 0.5) # Critical damage sound
                self.resilience = 1.0 # Reset to 1 heart
                self.invincible_timer = self.invincible_duration * 2 # Longer invincibility

    def collect_rupee(self):
        self.power += 1
        Sound.play_tone(700 + self.power * 5, 0.05) # Rupee sound, scales slightly

    def collect_heart_shard(self):
        self.max_resilience += 1.0 # Max resilience increases by 1 heart
        Sound.play_tone(600, 0.1) # Heart sound

    def draw(self):
        # Only draw if not currently flashing from being hit
        if self.hit_flash_timer > 0 and int(self.hit_flash_timer * 10) % 2 == 0:
            return

        # Draw a triangle for the hero (pointing up)
        p1 = (int(self.x), int(self.y - self.radius))
        p2 = (int(self.x - self.radius), int(self.y + self.radius / 2))
        p3 = (int(self.x + self.radius), int(self.y + self.radius / 2))
        Render.draw_line(p1[0], p1[1], p2[0], p2[1])
        Render.draw_line(p2[0], p2[1], p3[0], p3[1])
        Render.draw_line(p3[0], p3[1], p1[0], p1[1])

        # Draw resilience (hearts) as circles near the hero
        heart_spacing = 10
        # Draw full hearts
        for i in range(int(self.resilience)):
            hx = int(self.x - (self.max_resilience - 1) * heart_spacing / 2 + i * heart_spacing)
            hy = int(self.y + self.radius + 10)
            Render.draw_circle(hx, hy, 3, filled=True)
        # Draw empty parts for fractional hearts or max hearts
        for i in range(int(self.max_resilience)):
            hx = int(self.x - (self.max_resilience - 1) * heart_spacing / 2 + i * heart_spacing)
            hy = int(self.y + self.radius + 10)
            Render.draw_circle(hx, hy, 3, filled=False) # Always draw outer circle
            # Draw half-filled for fractional hearts
            if self.resilience % 1.0 > 0.0 and i == int(self.resilience):
                # This is a bit tricky with only filled=True/False. Let's just draw an inner circle
                # to represent the filled portion. A small hack to show "half"
                Render.draw_circle(hx, hy, 1, filled=True)

# Artifacts: collected by the hero for power or resilience
class Rupee(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, max_age=10.0)
        self.size = 5
        self.rotation = 0.0
        self.rotation_speed = 3.0 # Radians per second

    def update(self, delta: float):
        super().update(delta)
        self.rotation += self.rotation_speed * delta

    def draw(self):
        # Draw a rotating square
        hw = self.size
        hh = self.size
        # Get points for a square centered at (self.x, self.y)
        points = [
            (-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)
        ]
        
        cos_rot = math.cos(self.rotation)
        sin_rot = math.sin(self.rotation)

        rotated_points = []
        for px, py in points:
            new_x = self.x + (px * cos_rot - py * sin_rot)
            new_y = self.y + (px * sin_rot + py * cos_rot)
            rotated_points.append((new_x, new_y))

        for i in range(len(rotated_points)):
            p1 = rotated_points[i]
            p2 = rotated_points[(i + 1) % len(rotated_points)]
            Render.draw_line(int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]))

# Heart Shard: increases max resilience
class HeartShard(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, max_age=12.0)
        self.radius = 4
        self.pulse_timer = random.uniform(0, math.pi * 2) # Offset for varied pulsing

    def update(self, delta: float):
        super().update(delta)
        self.pulse_timer += delta * 5 # Faster pulse

    def draw(self):
        # Draw a pulsing circle
        pulse_scale = 1 + 0.2 * math.sin(self.pulse_timer) # Scale between 0.8 and 1.2
        current_radius = int(self.radius * pulse_scale)
        Render.draw_circle(int(self.x), int(self.y), current_radius, filled=False)

# Triforce Shard: advances the dream stage
class TriforceShard(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, max_age=15.0)
        self.size = 10 # Size of one triangle side
        self.rotation = 0.0
        self.rotation_speed = 1.0

    def update(self, delta: float):
        super().update(delta)
        self.rotation += self.rotation_speed * delta

    def draw(self):
        # Draw three interlocking triangles (simplified Triforce)
        
        # Outer triangle
        h_outer = self.size * math.sqrt(3) # A larger triangle
        p_top_outer = (self.x, self.y - h_outer / 2)
        p_bl_outer = (self.x - self.size / 2 * 2, self.y + h_outer / 2) # Doubled size
        p_br_outer = (self.x + self.size / 2 * 2, self.y + h_outer / 2)

        # Inner gap triangle (empty space)
        h_inner_gap = self.size * math.sqrt(3) / 2
        p_top_inner = (self.x, self.y + h_inner_gap / 2)
        p_bl_inner = (self.x - self.size / 2, self.y - h_inner_gap / 2)
        p_br_inner = (self.x + self.size / 2, self.y - h_inner_gap / 2)

        # Apply rotation around center (self.x, self.y)
        def rotate_point(px, py, cx, cy, angle):
            rx = px - cx
            ry = py - cy
            new_x = cx + rx * math.cos(angle) - ry * math.sin(angle)
            new_y = cy + rx * math.sin(angle) + ry * math.cos(angle)
            return new_x, new_y

        # Rotate outer triangle points
        rotated_outer_p1 = rotate_point(p_top_outer[0], p_top_outer[1], self.x, self.y, self.rotation)
        rotated_outer_p2 = rotate_point(p_bl_outer[0], p_bl_outer[1], self.x, self.y, self.rotation)
        rotated_outer_p3 = rotate_point(p_br_outer[0], p_br_outer[1], self.x, self.y, self.rotation)

        # Rotate inner gap triangle points
        rotated_inner_p1 = rotate_point(p_top_inner[0], p_top_inner[1], self.x, self.y, self.rotation)
        rotated_inner_p2 = rotate_point(p_bl_inner[0], p_bl_inner[1], self.x, self.y, self.rotation)
        rotated_inner_p3 = rotate_point(p_br_inner[0], p_br_inner[1], self.x, self.y, self.rotation)
        
        # Draw the outer triangle
        Render.draw_line(int(rotated_outer_p1[0]), int(rotated_outer_p1[1]), int(rotated_outer_p2[0]), int(rotated_outer_p2[1]))
        Render.draw_line(int(rotated_outer_p2[0]), int(rotated_outer_p2[1]), int(rotated_outer_p3[0]), int(rotated_outer_p3[1]))
        Render.draw_line(int(rotated_outer_p3[0]), int(rotated_outer_p3[1]), int(rotated_outer_p1[0]), int(rotated_outer_p1[1]))

        # Draw the inner "gap" triangle to create the impression of three individual triangles
        # We draw its lines to leave the space blank.
        Render.draw_line(int(rotated_inner_p1[0]), int(rotated_inner_p1[1]), int(rotated_inner_p2[0]), int(rotated_inner_p2[1]))
        Render.draw_line(int(rotated_inner_p2[0]), int(rotated_inner_p2[1]), int(rotated_inner_p3[0]), int(rotated_inner_p3[1]))
        Render.draw_line(int(rotated_inner_p3[0]), int(rotated_inner_p3[1]), int(rotated_inner_p1[0]), int(rotated_inner_p1[1]))


# Enemies: abstract representations of threats
class Octorok(Entity): # Bouncing circle
    def __init__(self, x, y):
        super().__init__(x, y, max_age=8.0)
        self.radius = 6
        self.speed = random.uniform(30, 60)
        self.angle = random.uniform(0, 2 * math.pi)
        self.dx = self.speed * math.cos(self.angle)
        self.dy = self.speed * math.sin(self.angle)

    def update(self, delta: float):
        super().update(delta)
        self.x += self.dx * delta
        self.y += self.dy * delta

        # Bounce off walls (or screen edges in this simplified version)
        if self.x - self.radius < 0 or self.x + self.radius > 399:
            self.dx *= -1
            self.x = max(self.radius, min(399 - self.radius, self.x))
        if self.y - self.radius < 0 or self.y + self.radius > 299:
            self.dy *= -1
            self.y = max(self.radius, min(299 - self.radius, self.y))

    def draw(self):
        Render.draw_circle(int(self.x), int(self.y), self.radius, filled=False)

class Stalfos(Entity): # Horizontal patrolling line
    def __init__(self, x, y):
        super().__init__(x, y, max_age=10.0)
        self.length = 20
        self.speed = random.uniform(40, 70)
        self.direction = random.choice([-1, 1]) # -1 for left, 1 for right
        self.patrol_range = 50 # How far it moves left/right from spawn point
        self.spawn_x = x

    def update(self, delta: float):
        super().update(delta)
        self.x += self.speed * self.direction * delta

        if self.direction == 1 and self.x > self.spawn_x + self.patrol_range:
            self.direction = -1
        elif self.direction == -1 and self.x < self.spawn_x - self.patrol_range:
            self.direction = 1

    def draw(self):
        Render.draw_line(int(self.x - self.length / 2), int(self.y), int(self.x + self.length / 2), int(self.y))

class Darknut(Entity): # Slow, heavily armored rectangle
    def __init__(self, x, y):
        super().__init__(x, y, max_age=20.0)
        self.width = 15
        self.height = 15
        self.speed = random.uniform(10, 25)
        self.target_x = x
        self.target_y = y
        self.change_target_timer = 0.0
        self.change_target_interval = 2.0 # Change target every 2 seconds
        self.health = 3 # Requires multiple hits from hero

    def update(self, delta: float):
        super().update(delta)
        
        self.change_target_timer += delta
        if self.change_target_timer >= self.change_target_interval:
            self.target_x = random.randint(50, 350)
            self.target_y = random.randint(50, 250)
            self.change_target_timer = 0.0

        # Move towards target
        angle = math.atan2(self.target_y - self.y, self.target_x - self.x)
        self.x += self.speed * math.cos(angle) * delta
        self.y += self.speed * math.sin(angle) * delta

    def take_hit(self):
        self.health -= 1
        Sound.play_tone(300, 0.05) # Hit sound
        if self.health <= 0:
            self.is_active = False
            Sound.play_tone(200, 0.1) # Defeat sound

    def draw(self):
        Render.draw_rect(int(self.x - self.width / 2), int(self.y - self.height / 2), self.width, self.height, filled=False)
        if self.health > 1: # Indicate health by inner lines
            Render.draw_rect(int(self.x - self.width / 4), int(self.y - self.height / 4), self.width // 2, self.height // 2, filled=False)


# World elements for ambience and structure
class WallSegment(Entity):
    def __init__(self, x, y, width, height):
        super().__init__(x, y) # Walls are permanent, no max_age
        self.width = width
        self.height = height

    def draw(self):
        Render.draw_rect(self.x, self.y, self.width, self.height, filled=True) # Filled walls

class AmbientParticle(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, max_age=random.uniform(2.0, 5.0))
        self.speed = random.uniform(5, 20)
        self.angle = random.uniform(0, 2 * math.pi)
        self.dx = self.speed * math.cos(self.angle)
        self.dy = self.speed * math.sin(self.angle)
        self.initial_x = x
        self.initial_y = y
        self.size = 3 # Initial size

    def update(self, delta: float):
        super().update(delta)
        self.x += self.dx * delta
        self.y += self.dy * delta
        # Fade out by becoming smaller
        self.size = max(1, int(3 * (1 - self.age / self.max_age)))

    def draw(self):
        if self.is_alive():
            Render.draw_circle(int(self.x), int(self.y), self.size, filled=True)


# Main program class, managing the dream
class Program:
    def __init__(self):
        self.hero = Hero()
        self.artifacts = []
        self.enemies = []
        self.world_elements = []
        self.ambient_particles = []

        self.spawn_artifact_timer = 0.0
        self.spawn_enemy_timer = 0.0
        self.spawn_particle_timer = 0.0
        self.progression_timer = 0.0
        self.stage = 0

        # Dream stages with distinct properties
        self.stage_data = [
            {
                'name': "Whispering Woods",
                'art_spawn_int': 2.0, 'enemy_spawn_int': 3.0, 'part_spawn_int': 0.1,
                'art_types': [HeartShard], 'enemy_types': [Octorok],
                'walls': [], 'progression_threshold': 30.0, 'ambient_freq': 100,
                'num_walls_to_generate': 0
            },
            {
                'name': "Forgotten Temple",
                'art_spawn_int': 1.5, 'enemy_spawn_int': 2.5, 'part_spawn_int': 0.08,
                'art_types': [HeartShard, Rupee], 'enemy_types': [Octorok, Stalfos],
                'walls': [], 'progression_threshold': 60.0, 'ambient_freq': 150,
                'num_walls_to_generate': 5 # Example: 5 random walls
            },
            {
                'name': "Shadow's Keep",
                'art_spawn_int': 1.0, 'enemy_spawn_int': 2.0, 'part_spawn_int': 0.05,
                'art_types': [HeartShard, Rupee, TriforceShard], 'enemy_types': [Octorok, Stalfos, Darknut],
                'walls': [], 'progression_threshold': 90.0, 'ambient_freq': 200,
                'num_walls_to_generate': 10
            },
            {
                'name': "Hyrule's Heart",
                'art_spawn_int': 0.7, 'enemy_spawn_int': 1.5, 'part_spawn_int': 0.03,
                'art_types': [HeartShard, Rupee, TriforceShard], 'enemy_types': [Octorok, Stalfos, Darknut],
                'walls': [], 'progression_threshold': float('inf'), 'ambient_freq': 250,
                'num_walls_to_generate': 15
            }
        ]

        self.current_stage_data = self.stage_data[self.stage]
        self.dream_messages = [
            "A nascent hero stirs...",
            "Echoes of old structures emerge...",
            "Shadows gather in the labyrinth...",
            "The Triforce calls, the dream unfolds..."
        ]
        self.current_message = self.dream_messages[0]
        self.message_display_timer = 0.0
        self.message_duration = 4.0

        self._apply_stage_settings() # Initialize with stage 0 settings

        # Play initial ambient sound
        Sound.play_tone(self.current_stage_data['ambient_freq'], 0.1)
        
    def _generate_random_walls(self, count):
        walls = []
        for _ in range(count):
            x = random.randint(50, 300)
            y = random.randint(50, 250)
            width = random.randint(20, 80)
            height = random.randint(5, 15)
            if random.random() < 0.5: # Mostly horizontal or vertical
                walls.append(WallSegment(x, y, width, 10))
            else:
                walls.append(WallSegment(x, y, 10, height))
        
        # Add a thin border to enclose the space somewhat
        walls.append(WallSegment(0, 0, 400, 5))
        walls.append(WallSegment(0, 295, 400, 5))
        walls.append(WallSegment(0, 0, 5, 300))
        walls.append(WallSegment(395, 0, 5, 300))

        return walls

    def _apply_stage_settings(self):
        self.current_stage_data = self.stage_data[self.stage]
        self.world_elements = self._generate_random_walls(self.current_stage_data['num_walls_to_generate'])
        
        # Adjust ambient sound based on stage
        # Play a longer, more continuous ambient tone for the current stage
        Sound.play_tone(self.current_stage_data['ambient_freq'], 0.1) # Brief sound for transition
        # A more continuous background sound could be simulated by very frequent short tones
        # or by using the delta to determine when to repeat a tone, but `play_tone` blocks.
        # For this setup, we'll just have the initial brief tone.

    def update(self, delta: float):
        self.hero.update(delta)
        self.spawn_artifact_timer += delta
        self.spawn_enemy_timer += delta
        self.spawn_particle_timer += delta
        self.progression_timer += delta
        self.message_display_timer += delta

        # Automatic stage progression
        if self.stage < len(self.stage_data) - 1 and self.progression_timer >= self.current_stage_data['progression_threshold']:
            self._advance_stage()

        # Spawn artifacts
        if self.spawn_artifact_timer >= self.current_stage_data['art_spawn_int']:
            self._spawn_entity(self.current_stage_data['art_types'], self.artifacts)
            self.spawn_artifact_timer = 0.0

        # Spawn enemies
        if self.spawn_enemy_timer >= self.current_stage_data['enemy_spawn_int']:
            self._spawn_entity(self.current_stage_data['enemy_types'], self.enemies)
            self.spawn_enemy_timer = 0.0

        # Spawn ambient particles
        if self.spawn_particle_timer >= self.current_stage_data['part_spawn_int']:
            self._spawn_entity([AmbientParticle], self.ambient_particles)
            self.spawn_particle_timer = 0.0

        # Update and filter entities
        self._update_and_filter(self.artifacts, delta)
        self._update_and_filter(self.enemies, delta)
        self._update_and_filter(self.ambient_particles, delta)
        
        # Handle collisions
        self._handle_collisions()

    def _spawn_entity(self, entity_types: list, target_list: list):
        x = random.randint(20, 380)
        y = random.randint(20, 280)
        entity_type = random.choice(entity_types)
        
        # Ensure new entities don't spawn inside walls too often
        # Simple retry mechanism
        for _ in range(5): # Max 5 tries to find a clear spot
            spawn_clear = True
            test_entity_radius = 0 # Default for non-circular
            if entity_type == Octorok: test_entity_radius = 6
            elif entity_type == Rupee: test_entity_radius = 5
            elif entity_type == HeartShard: test_entity_radius = 4
            elif entity_type == TriforceShard: test_entity_radius = 15 # Larger for triforce
            elif entity_type == Stalfos: test_entity_radius = 10 # Half length approx
            elif entity_type == Darknut: test_entity_radius = 15 # Half width/height approx

            for wall in self.world_elements:
                # Simple AABB collision for wall check during spawn (using radius for approximation)
                if (x + test_entity_radius > wall.x and x - test_entity_radius < wall.x + wall.width and
                    y + test_entity_radius > wall.y and y - test_entity_radius < wall.y + wall.height):
                    spawn_clear = False
                    x = random.randint(20, 380) # Re-roll position
                    y = random.randint(20, 280)
                    break
            if spawn_clear:
                break
        
        if entity_type == AmbientParticle:
            target_list.append(entity_type(random.randint(0, 399), random.randint(0, 299)))
        else:
            target_list.append(entity_type(x, y))

    def _update_and_filter(self, entity_list: list, delta: float):
        new_list = []
        for entity in entity_list:
            entity.update(delta)
            if entity.is_alive():
                new_list.append(entity)
        entity_list[:] = new_list # Efficiently update the list in place

    def _handle_collisions(self):
        hero_hitbox = (self.hero.x, self.hero.y, self.hero.radius) # (cx, cy, r)

        # Artifacts
        for artifact in list(self.artifacts): # Iterate over a copy to allow modification
            if not artifact.is_alive(): continue
            artifact_hit_radius = 0
            if hasattr(artifact, 'size'): artifact_hit_radius = artifact.size
            elif hasattr(artifact, 'radius'): artifact_hit_radius = artifact.radius
            else: artifact_hit_radius = 5 # Default for unknown
            artifact_hitbox = (artifact.x, artifact.y, artifact_hit_radius)
            if self._check_circle_collision(hero_hitbox, artifact_hitbox):
                if isinstance(artifact, Rupee):
                    self.hero.collect_rupee()
                elif isinstance(artifact, HeartShard):
                    self.hero.collect_heart_shard()
                elif isinstance(artifact, TriforceShard):
                    self._advance_stage()
                artifact.is_active = False # Remove artifact after collection

        # Enemies
        for enemy in list(self.enemies):
            if not enemy.is_alive(): continue
            enemy_hitbox_radius = 10 # General collision radius for enemies
            if isinstance(enemy, Octorok): enemy_hitbox_radius = enemy.radius
            elif isinstance(enemy, Stalfos): enemy_hitbox_radius = enemy.length / 2 # Approx center for line
            elif isinstance(enemy, Darknut): enemy_hitbox_radius = max(enemy.width, enemy.height) / 2 # Approx center for rect

            enemy_hitbox = (enemy.x, enemy.y, enemy_hitbox_radius)

            if self._check_circle_collision(hero_hitbox, enemy_hitbox):
                if isinstance(enemy, Darknut):
                    if self.hero.power >= 1: # Darknuts are tougher, require some hero power
                        enemy.take_hit()
                        if not enemy.is_alive():
                            # Only remove if it's still in the list (can be removed by another collision in same frame if it was also hit)
                            if enemy in self.enemies: self.enemies.remove(enemy) 
                    else: # If hero lacks power, still takes damage, but darknut is not defeated
                        self.hero.take_damage(1)
                else: # Octoroks, Stalfos
                    self.hero.take_damage(1)
                    enemy.is_active = False # Simple enemies are defeated on contact
                    if enemy in self.enemies: # Ensure it's still in the list before trying to remove
                        self.enemies.remove(enemy)


    def _check_circle_collision(self, c1: tuple, c2: tuple) -> bool:
        cx1, cy1, r1 = c1
        cx2, cy2, r2 = c2
        dist_sq = (cx1 - cx2)**2 + (cy1 - cy2)**2
        return dist_sq <= (r1 + r2)**2

    def _advance_stage(self):
        if self.stage < len(self.stage_data) - 1:
            self.stage += 1
            self.progression_timer = 0.0 # Reset timer for new stage
            self.current_message = self.dream_messages[self.stage]
            self.message_display_timer = 0.0
            
            # Clear existing temporary entities (artifacts, enemies, particles)
            self.artifacts.clear()
            self.enemies.clear()
            self.ambient_particles.clear()

            # Apply new stage settings, including walls
            self._apply_stage_settings()

            Sound.play_tone(self.current_stage_data['ambient_freq'] + 100, 0.2) # Stage transition sound
        else:
            # Final stage achieved - perhaps a final message or visual flourish
            self.current_message = "The Legend is now fully dreamed..."
            self.message_display_timer = 0.0 # Make sure message displays

    def draw(self):
        # Draw world elements first
        for wall in self.world_elements:
            wall.draw()

        # Draw ambient particles (under everything)
        for particle in self.ambient_particles:
            particle.draw()

        # Draw artifacts
        for artifact in self.artifacts:
            artifact.draw()

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw()

        # Draw the hero
        self.hero.draw()
        
        # Display current message
        if self.message_display_timer < self.message_duration:
            text_width = len(self.current_message) * 8 # Approximate width for 16px font
            Render.draw_text(self.current_message, int(400 / 2 - text_width / 2), 299 - 30)

        # Display Hero stats (power, resilience)
        Render.draw_text(f"Power: {self.hero.power}", 5, 5)
        # Resilience is drawn by the hero itself

    def get_instructions(self) -> str:
        return "Use W A S D to move. Navigate the unfolding dream."

    def get_next_idea(self) -> list[str]:
        return ["Temporal Looping", "Shadow Echoes", "Dream Guardians"]