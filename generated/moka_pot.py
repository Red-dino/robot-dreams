import math
import random
from generated.helpers import Render, Input, Sound


import math
import random

# Define constants for window size
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 300

class Program:
    def __init__(self):
        # Game states/stages
        self.stage = 0  # 0: Intro, 1: Water, 2: Grounds, 3: Pressure, 4: Percolation, 5: Coffee
        self.stage_timer = 0.0

        # Player properties
        self.player_x = WINDOW_WIDTH // 2
        self.player_y = WINDOW_HEIGHT // 2
        self.player_radius = 5
        self.player_speed = 80.0 # pixels per second
        self.player_collected_orbs = 0

        # Stage 1: Water Chamber
        self.water_orbs = []
        self.max_water_orbs = 15
        self.orb_spawn_timer = 0.0
        self.orb_spawn_interval = 1.0 # seconds

        # Stage 2: Grounds Chamber
        self.ground_particles = []
        self.max_ground_particles = 100
        self.grounds_initialized = False
        self.grounds_infused_count = 0

        # Stage 3: Pressure Passage
        self.pressure_pulse_strength = 0.0
        self.pressure_path_base_width = 80
        self.pressure_path_min_width = 30
        self.pressure_passage_height = WINDOW_HEIGHT - 60
        self.pressure_current_width = self.pressure_path_base_width

        # Stage 4: Percolation Tube
        self.percolation_speed_multiplier = 1.0
        self.percolation_wave_offset = 0.0
        self.percolation_tube_top_y = 20
        self.percolation_tube_bottom_y = WINDOW_HEIGHT - 20
        self.percolation_tube_length = self.percolation_tube_bottom_y - self.percolation_tube_top_y
        self.percolation_max_height_needed = self.percolation_tube_length * 1.5 # Need to "percolate" more than just window height

        # Stage 5: Coffee Chamber
        self.coffee_radiance_effect = 0.0
        self.coffee_particles = []
        self.coffee_max_particles = 50
        self.coffee_pulse_timer = 0.0


        self._reset_game_state() # Call a helper to set initial state

    def _reset_game_state(self):
        self.stage = 0
        self.stage_timer = 0.0
        self.player_x = WINDOW_WIDTH // 2
        self.player_y = WINDOW_HEIGHT // 2
        self.player_radius = 5
        self.player_collected_orbs = 0

        self.water_orbs = []
        self.orb_spawn_timer = 0.0
        for _ in range(3): # Initial orbs
            self._spawn_water_orb()

        self.ground_particles = []
        self.grounds_initialized = False
        self.grounds_infused_count = 0

        self.pressure_pulse_strength = 0.0
        self.pressure_current_width = self.pressure_path_base_width

        self.percolation_speed_multiplier = 1.0
        self.percolation_wave_offset = 0.0
        self.player_y = self.percolation_tube_bottom_y # Player starts at bottom for percolation
        self.player_x = WINDOW_WIDTH // 2
        self.percolation_height_reached = 0.0

        self.coffee_radiance_effect = 0.0
        self.coffee_particles = []
        self.coffee_pulse_timer = 0.0


    def _spawn_water_orb(self):
        # Spawn orbs within a bottom chamber region
        orb_x = random.randint(50, WINDOW_WIDTH - 50)
        orb_y = random.randint(WINDOW_HEIGHT // 2 + 50, WINDOW_HEIGHT - 50)
        self.water_orbs.append({'x': orb_x, 'y': orb_y, 'age': 0.0})

    def _initialize_grounds(self):
        if not self.grounds_initialized:
            # Grounds fill a central region above the player start point
            for _ in range(self.max_ground_particles):
                ground_x = random.randint(50, WINDOW_WIDTH - 50)
                ground_y = random.randint(50, WINDOW_HEIGHT // 2 + 50) # From mid-screen up
                self.ground_particles.append({'x': ground_x, 'y': ground_y, 'infused': False})
            self.grounds_initialized = True

    def update(self, delta: float):
        self.stage_timer += delta

        # Handle player movement
        dx = 0
        dy = 0
        if Input.is_key_pressed('w'):
            dy -= 1
        if Input.is_key_pressed('s'):
            dy += 1
        if Input.is_key_pressed('a'):
            dx -= 1
        if Input.is_key_pressed('d'):
            dx += 1

        player_actual_speed = self.player_speed
        if self.stage == 4: # Percolation stage has upward bias
            player_actual_speed *= self.percolation_speed_multiplier

        if dx != 0 or dy != 0:
            magnitude = math.sqrt(dx*dx + dy*dy)
            if magnitude > 0:
                self.player_x += (dx / magnitude) * player_actual_speed * delta
                self.player_y += (dy / magnitude) * player_actual_speed * delta

        # Clamp player position within window bounds (generic)
        self.player_x = max(self.player_radius, min(WINDOW_WIDTH - self.player_radius, self.player_x))
        self.player_y = max(self.player_radius, min(WINDOW_HEIGHT - self.player_radius, self.player_y))


        if self.stage == 0: # Intro
            if Input.is_key_pressed('space'):
                self.stage = 1
                self.stage_timer = 0.0
                Sound.play_tone(100, 0.2) # Soft start tone
                self.player_y = WINDOW_HEIGHT - 70 # Position player in water chamber


        elif self.stage == 1: # Water Chamber
            # Clamp player to bottom half of screen
            self.player_y = max(WINDOW_HEIGHT // 2, min(WINDOW_HEIGHT - self.player_radius, self.player_y))

            # Update and spawn water orbs
            self.orb_spawn_timer += delta
            if self.orb_spawn_timer >= self.orb_spawn_interval and len(self.water_orbs) < self.max_water_orbs:
                self._spawn_water_orb()
                self.orb_spawn_timer = 0.0

            orbs_to_remove = []
            for i, orb in enumerate(self.water_orbs):
                orb['age'] += delta
                dist = math.sqrt((self.player_x - orb['x'])**2 + (self.player_y - orb['y'])**2)
                if dist < self.player_radius + 5: # Orb radius is 5
                    self.player_collected_orbs += 1
                    self.player_radius = min(10, self.player_radius + 0.5) # Player grows slightly
                    orbs_to_remove.append(i)
                    Sound.play_tone(400 + self.player_collected_orbs * 10, 0.05) # Rising tone for collection

            for i in sorted(orbs_to_remove, reverse=True):
                self.water_orbs.pop(i)

            # Stage transition condition
            if self.player_collected_orbs >= 10: # Collect 10 orbs to proceed
                self.stage = 2
                self.stage_timer = 0.0
                self.player_x = WINDOW_WIDTH // 2
                self.player_y = WINDOW_HEIGHT - 50 # Reposition for next stage (bottom of grounds)
                Sound.play_tone(500, 0.2) # Transition tone
                self._initialize_grounds()


        elif self.stage == 2: # Grounds Chamber
            # Clamp player to the grounds chamber
            self.player_y = max(self.player_radius + 30, min(WINDOW_HEIGHT - 30 - self.player_radius, self.player_y))
            self.player_x = max(self.player_radius + 30, min(WINDOW_WIDTH - 30 - self.player_radius, self.player_x))

            # Player interaction with grounds
            for i, particle in enumerate(self.ground_particles):
                if not particle['infused']:
                    dist = math.sqrt((self.player_x - particle['x'])**2 + (self.player_y - particle['y'])**2)
                    if dist < self.player_radius + 1: # Ground particles are tiny
                        particle['infused'] = True # Mark as "infused"
                        self.grounds_infused_count += 1
                        Sound.play_tone(150 + random.randint(-10, 10), 0.01) # Soft, low clicks
            
            # Stage transition: move player to top of the chamber after infusing enough grounds
            if self.grounds_infused_count >= self.max_ground_particles * 0.7: # Infuse 70% of grounds
                self.stage = 3
                self.stage_timer = 0.0
                self.player_x = WINDOW_WIDTH // 2
                self.player_y = WINDOW_HEIGHT - 30 # Start at bottom of pressure tube
                Sound.play_tone(600, 0.2)


        elif self.stage == 3: # Pressure Build-Up
            # Clamp player horizontally within current width
            current_path_half_width = self.pressure_current_width / 2
            self.player_x = max(WINDOW_WIDTH // 2 - current_path_half_width + self.player_radius,
                                min(WINDOW_WIDTH // 2 + current_path_half_width - self.player_radius, self.player_x))
            
            # Clamp player vertically within the passage
            self.player_y = max(30 + self.player_radius, min(WINDOW_HEIGHT - 30 - self.player_radius, self.player_y))

            # Pressure walls oscillate and narrow
            self.pressure_pulse_strength = (math.sin(self.stage_timer * 3) + 1) / 2 # 0 to 1
            self.pressure_current_width = self.pressure_path_base_width - \
                                          (self.pressure_path_base_width - self.pressure_path_min_width) * (self.stage_timer / 5.0) # Narrows over 5 seconds
            self.pressure_current_width = max(self.pressure_path_min_width, self.pressure_current_width)

            # Upward force
            self.player_y -= self.player_speed * delta * (0.5 + self.pressure_pulse_strength * 0.5) # Stronger push with pulse

            # Check if player has moved past the 'pressure' area (reached top)
            if self.player_y < 50: # Reached top of the pressure passage
                self.stage = 4
                self.stage_timer = 0.0
                self.player_x = WINDOW_WIDTH // 2 # Reset position for percolation
                self.player_y = self.percolation_tube_bottom_y # Start at bottom of percolation tube
                Sound.play_tone(700, 0.3)


        elif self.stage == 4: # Percolation Tube
            # Player is constantly pushed upwards
            self.player_y -= self.player_speed * delta * self.percolation_speed_multiplier
            self.percolation_height_reached += self.player_speed * delta * self.percolation_speed_multiplier

            self.percolation_speed_multiplier = min(3.0, self.percolation_speed_multiplier + delta * 0.1) # Speed up over time
            self.percolation_wave_offset += delta * 1.5 # For visual wave motion

            # Clamp player horizontally within dynamic tube
            current_tube_half_width = 25 + math.sin(self.player_y * 0.05 + self.percolation_wave_offset) * 10
            self.player_x = max(WINDOW_WIDTH // 2 - current_tube_half_width + self.player_radius,
                                min(WINDOW_WIDTH // 2 + current_tube_half_width - self.player_radius, self.player_x))

            # Stage transition: If player has "percolated" enough distance (even off-screen)
            if self.percolation_height_reached >= self.percolation_max_height_needed:
                self.stage = 5
                self.stage_timer = 0.0
                self.player_x = WINDOW_WIDTH // 2
                self.player_y = WINDOW_HEIGHT // 2 # Center for coffee
                Sound.play_tone(800, 0.5)
                # Initialize coffee particles
                for _ in range(self.coffee_max_particles):
                    self.coffee_particles.append({
                        'x': random.randint(50, WINDOW_WIDTH - 50),
                        'y': random.randint(50, WINDOW_HEIGHT - 50),
                        'dx': random.uniform(-10, 10),
                        'dy': random.uniform(-10, 10),
                        'life': random.uniform(1.0, 3.0),
                        'max_life': 0
                    })
                    self.coffee_particles[-1]['max_life'] = self.coffee_particles[-1]['life']


        elif self.stage == 5: # Coffee Chamber
            self.coffee_pulse_timer += delta
            self.coffee_radiance_effect = (math.sin(self.coffee_pulse_timer * 2) + 1) / 2 * 5 # Pulse 0 to 5

            # Update coffee particles
            for p in self.coffee_particles:
                p['x'] += p['dx'] * delta
                p['y'] += p['dy'] * delta
                p['life'] -= delta
                if p['life'] <= 0:
                    # Reset particle
                    p['x'] = random.randint(50, WINDOW_WIDTH - 50)
                    p['y'] = random.randint(50, WINDOW_HEIGHT - 50)
                    p['dx'] = random.uniform(-10, 10)
                    p['dy'] = random.uniform(-10, 10)
                    p['life'] = random.uniform(1.0, 3.0)
                    p['max_life'] = p['life']

            if Input.is_key_pressed('r'):
                self._reset_game_state()
                Sound.play_tone(100, 0.2) # Reset tone


    def draw(self):

        if self.stage == 0: # Intro
            Render.draw_text("The Alchemist's Vessel", 50, WINDOW_HEIGHT // 2 - 20)
            Render.draw_text(self.get_instructions(), 50, WINDOW_HEIGHT // 2 + 20)

        elif self.stage == 1: # Water Chamber
            # Draw water chamber boundary
            Render.draw_rect(20, WINDOW_HEIGHT // 2 - 10, WINDOW_WIDTH - 40, WINDOW_HEIGHT // 2, filled=False)
            
            # Draw oscillating water lines
            num_lines = 10
            for i in range(num_lines):
                y_base = WINDOW_HEIGHT // 2 + i * ((WINDOW_HEIGHT // 2 - 20) // num_lines)
                offset = math.sin(self.stage_timer * (0.5 + i * 0.1) + i) * 10
                Render.draw_line(20, int(y_base + offset), WINDOW_WIDTH - 20, int(y_base - offset))

            for orb in self.water_orbs:
                radius = 5 + math.sin(orb['age'] * 5) * 2 # Pulsating orb
                Render.draw_circle(int(orb['x']), int(orb['y']), int(radius), filled=True)
            
            Render.draw_text(f"Essence: {self.player_collected_orbs}/10", 10, 10)

        elif self.stage == 2: # Grounds Chamber
            # Draw grounds chamber boundary
            Render.draw_rect(30, 30, WINDOW_WIDTH - 60, WINDOW_HEIGHT - 60, filled=False)

            # Draw grounds particles (only if not "infused")
            for particle in self.ground_particles:
                if not particle['infused']:
                    Render.turn_on_pixel(int(particle['x']), int(particle['y']))
                # No other drawing for infused, they just disappear.
            Render.draw_text(f"Infused: {self.grounds_infused_count}/{int(self.max_ground_particles * 0.7)}", 10, 10)

        elif self.stage == 3: # Pressure Build-Up
            # Calculate current path width and center
            current_path_half_width = self.pressure_current_width / 2
            left_wall_x = WINDOW_WIDTH // 2 - current_path_half_width
            right_wall_x = WINDOW_WIDTH // 2 + current_path_half_width

            # Draw passage walls
            Render.draw_rect(int(left_wall_x - 5 - self.pressure_pulse_strength * 5), 20, 5, WINDOW_HEIGHT - 40, filled=True) # Left wall
            Render.draw_rect(int(right_wall_x + self.pressure_pulse_strength * 5), 20, 5, WINDOW_HEIGHT - 40, filled=True) # Right wall

            # Visualize pressure pulses
            num_pulse_lines = 8
            for i in range(num_pulse_lines):
                y_offset = (self.stage_timer * 30 + i * (self.pressure_passage_height / num_pulse_lines)) % self.pressure_passage_height
                line_y = 30 + y_offset
                amplitude = self.pressure_pulse_strength * 10 * math.sin(self.stage_timer * 5 + i) # Dynamic amplitude
                Render.draw_line(int(left_wall_x + 5), int(line_y + amplitude), int(right_wall_x - 5), int(line_y - amplitude))

            # Display "Pressure" indicator
            Render.draw_text(f"Pressure: {int(self.pressure_pulse_strength * 100)}%", 10, 10)


        elif self.stage == 4: # Percolation Tube
            # Draw dynamic tube walls
            current_left_wall_x = WINDOW_WIDTH // 2 - 25 - math.sin(self.percolation_wave_offset + self.player_y * 0.03) * 10
            current_right_wall_x = WINDOW_WIDTH // 2 + 25 + math.sin(self.percolation_wave_offset + self.player_y * 0.03) * 10
            
            # Draw vertical lines for the tube walls, making them "wave"
            num_segments = 20
            for i in range(num_segments):
                y1 = int(self.percolation_tube_bottom_y - i * (self.percolation_tube_length / num_segments))
                y2 = int(self.percolation_tube_bottom_y - (i + 1) * (self.percolation_tube_length / num_segments))
                
                wave_factor1 = math.sin(self.percolation_wave_offset * 2 + y1 * 0.02) * 10
                wave_factor2 = math.sin(self.percolation_wave_offset * 2 + y2 * 0.02) * 10

                Render.draw_line(int(WINDOW_WIDTH // 2 - 25 + wave_factor1), y1, int(WINDOW_WIDTH // 2 - 25 + wave_factor2), y2)
                Render.draw_line(int(WINDOW_WIDTH // 2 + 25 + wave_factor1), y1, int(WINDOW_WIDTH // 2 + 25 + wave_factor2), y2)

            # Draw bubbling effects (small circles rising)
            for i in range(30):
                bubble_x = WINDOW_WIDTH // 2 + random.randint(-20, 20) + math.sin(self.stage_timer * 2 + i) * 5
                bubble_y = (WINDOW_HEIGHT - (self.stage_timer * 100 + i * 20) % (WINDOW_HEIGHT + 50))
                if bubble_y > 0 and bubble_y < WINDOW_HEIGHT:
                    Render.draw_circle(int(bubble_x), int(bubble_y), 2)
            
            Render.draw_text(f"Ascent: {int(self.percolation_height_reached)}/{int(self.percolation_max_height_needed)}", 10, 10)


        elif self.stage == 5: # Coffee Chamber
            # Draw top chamber boundary
            Render.draw_rect(20, 20, WINDOW_WIDTH - 40, WINDOW_HEIGHT - 40, filled=False)

            # Player (now "coffee essence") radiates
            Render.draw_circle(int(self.player_x), int(self.player_y), int(self.player_radius + self.coffee_radiance_effect), filled=True)

            # Draw subtle moving particles
            for p in self.coffee_particles:
                # Simulate fading by drawing fewer pixels for lower life
                num_pixels = int(5 * (p['life'] / p['max_life']))
                for _ in range(num_pixels):
                    offset_x = random.randint(-2, 2)
                    offset_y = random.randint(-2, 2)
                    Render.turn_on_pixel(int(p['x'] + offset_x), int(p['y'] + offset_y))
            
            Render.draw_text("Essence Complete.", 50, WINDOW_HEIGHT // 2 - 20)
            Render.draw_text(self.get_instructions(), 50, WINDOW_HEIGHT // 2 + 20)


        # Draw player in all stages except intro
        if self.stage > 0:
            Render.draw_circle(int(self.player_x), int(self.player_y), int(self.player_radius), filled=True)


    def get_instructions(self) -> str:
        if self.stage == 0:
            return "Press 'space' to begin the journey."
        elif self.stage == 1:
            return "Navigate WASD. Collect shimmering energies."
        elif self.stage == 2:
            return "Move WASD to permeate the rich fragments."
        elif self.stage == 3:
            return "Feel the pressure, guide WASD. Rise!"
        elif self.stage == 4:
            return "Ride the current with WASD, ascend!"
        elif self.stage == 5:
            return "The essence is complete. Press 'r' to dream again."
        return "" # Should not happen

    def get_next_idea(self) -> list[str]:
        return ["Gravity Inversion", "Sentient Grounds"]
