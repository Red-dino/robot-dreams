import math
import random
from generated.helpers import Render, Input, Sound


import random
import math

# Assume Input, Render, Sound are available in the execution context

class Particle:
    def __init__(self, x, y, screen_width, screen_height):
        self.x = float(x)
        self.y = float(y)
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.base_speed = random.uniform(30.0, 70.0) # pixels per second
        angle = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(angle) * self.base_speed
        self.vy = math.sin(angle) * self.base_speed

        self.trail_history = [] # Stores (x, y) tuples
        self.max_trail_length = 20 # Number of points to store for the trail
        self.trail_interval = 0.03 # Time in seconds between storing trail points
        self.trail_timer = 0.0
        self.color_variant_offset = random.uniform(-0.1, 0.1) # Subtle visual variation

    def update(self, delta: float, random_perturbation_strength: float, 
               attractor_pos=None, attractor_strength=0.0,
               repulsors=None, global_turbulence_strength=0.0):
        
        # Store trail point
        self.trail_timer += delta
        if self.trail_timer >= self.trail_interval:
            self.trail_history.append((self.x, self.y))
            if len(self.trail_history) > self.max_trail_length:
                self.trail_history.pop(0)
            self.trail_timer = 0.0

        # Apply random perturbation to velocity
        self.vx += random.uniform(-random_perturbation_strength, random_perturbation_strength) * delta * 60
        self.vy += random.uniform(-random_perturbation_strength, random_perturbation_strength) * delta * 60

        # Apply global turbulence
        self.vx += random.uniform(-global_turbulence_strength, global_turbulence_strength) * delta
        self.vy += random.uniform(-global_turbulence_strength, global_turbulence_strength) * delta

        # Apply attractor force
        if attractor_pos and attractor_strength > 0:
            ax, ay = attractor_pos
            dx = ax - self.x
            dy = ay - self.y
            dist_sq = dx*dx + dy*dy
            if dist_sq < 1.0: 
                dist_sq = 1.0 # Prevent division by zero
                dx = random.uniform(-1, 1) # Give a slight random nudge
                dy = random.uniform(-1, 1)
                dist = math.sqrt(dx*dx + dy*dy)
            else:
                dist = math.sqrt(dist_sq)
            
            force_magnitude = attractor_strength / (dist + 15.0) 
            force_magnitude = min(force_magnitude, 200.0) 
            
            self.vx += (dx / dist) * force_magnitude * delta
            self.vy += (dy / dist) * force_magnitude * delta
        
        # Apply repulsor forces
        if repulsors:
            for repulsor in repulsors:
                rx, ry = repulsor['pos']
                r_strength = repulsor['strength']
                r_radius = repulsor['radius']

                dx = self.x - rx # Vector from repulsor to particle
                dy = self.y - ry
                dist_sq = dx*dx + dy*dy

                if dist_sq < r_radius*r_radius:
                    dist = math.sqrt(dist_sq)
                    if dist < 1.0: # Prevent division by zero if particle is exactly on repulsor
                        dist = 1.0
                        dx = random.uniform(-1, 1)
                        dy = random.uniform(-1, 1)
                        dist = math.sqrt(dx*dx + dy*dy)

                    # Force strongest near center, drops off to edge of radius
                    force_magnitude = r_strength * (1.0 - (dist / r_radius)) 
                    force_magnitude = min(force_magnitude, 250.0) # Max repulsor force
                    
                    self.vx += (dx / dist) * force_magnitude * delta
                    self.vy += (dy / dist) * force_magnitude * delta


        # Clamp velocity to prevent runaway speeds, but ensure minimum movement
        current_speed_mag = math.sqrt(self.vx**2 + self.vy**2)
        max_speed = self.base_speed * 3.0
        min_speed = 15.0 

        if current_speed_mag > max_speed:
            self.vx = (self.vx / current_speed_mag) * max_speed
            self.vy = (self.vy / current_speed_mag) * max_speed
        elif current_speed_mag < min_speed and current_speed_mag > 0.01: # Avoid division by small number
            self.vx = (self.vx / current_speed_mag) * min_speed
            self.vy = (self.vy / current_speed_mag) * min_speed
        elif current_speed_mag <= 0.01: # Completely stopped or almost, give a random kick
            angle = random.uniform(0, 2 * math.pi)
            self.vx = math.cos(angle) * min_speed
            self.vy = math.sin(angle) * min_speed

        # Update position
        self.x += self.vx * delta
        self.y += self.vy * delta

        # Wrap around screen boundaries
        if self.x < 0: self.x += self.screen_width
        if self.x >= self.screen_width: self.x -= self.screen_width
        if self.y < 0: self.y += self.screen_height
        if self.y >= self.screen_height: self.y -= self.screen_height

    def draw(self):
        # Draw the particle head as a filled circle
        Render.draw_circle(int(self.x), int(self.y), 2, filled=True)
        
        # Draw the trail using lines, fading out older segments
        if len(self.trail_history) > 1:
            for i in range(len(self.trail_history) - 1):
                p1_x, p1_y = self.trail_history[i]
                p2_x, p2_y = self.trail_history[i+1]
                
                # Fading effect: make older segments shorter or less frequent
                # This uses a simple "skip" mechanism instead of true alpha
                if i % (1 + (len(self.trail_history) - i) // 5) == 0: # Draw fewer older segments
                    Render.draw_line(int(p1_x), int(p1_y), int(p2_x), int(p2_y))


class Program:
    def __init__(self):
        self.screen_width = 400
        self.screen_height = 300
        self.particles = []
        self.max_particles = 10
        self.particle_spawn_rate = 1.0 # particles per second
        self.spawn_timer = 0.0
        self.random_perturbation_strength = 20.0 # How much velocity randomly changes
        self.global_turbulence_strength = 0.0 # Background "noise" affecting all particles

        self.attractor_active = False
        self.attractor_pos = (0.0, 0.0)
        self.attractor_strength = 200.0 
        self.attractor_duration = 5.0 
        self.attractor_cooldown = 5.0 
        self.attractor_timer = 0.0 
        self.attractor_is_cooldown = False
        self.attractor_movement_type = 'random_jump' # 'random_jump', 'circular_orbit', 'sine_wave'
        self.attractor_circular_angle = 0.0
        self.attractor_circular_radius = 80.0
        self.attractor_circular_speed = 0.5 # radians per second
        self.attractor_center_x = self.screen_width / 2
        self.attractor_center_y = self.screen_height / 2

        self.repulsors = [] # List of {'id': int, 'pos': (x,y), 'strength': float, 'radius': float, 'timer': float, 'movement_type': str}
        self.max_repulsors = 0
        self.repulsor_spawn_interval = 8.0 # Min time between repulsor spawns
        self.repulsor_spawn_timer = 0.0
        self.repulsor_strength = 250.0
        self.repulsor_radius = 40.0
        self.repulsor_duration = 3.0
        self.repulsor_angle_offset = random.uniform(0, 2 * math.pi) # For patterned movement

        self.progression_stage = 0
        self.stage_timer = 0.0
        # Durations for each stage (Stage 0 is initial, Stage 1 is 15s, etc.)
        self.stage_durations = [15.0, 30.0, 45.0, 60.0, 80.0, 100.0] # Added a new stage for more complexity
        self.paused = False
        
        # Debounce flags for key presses
        self._space_key_pressed = False
        self._p_key_pressed = False
        self._a_key_pressed = False

        self.static_pixel_count = 0
        
        # Particle connection lines
        self.enable_connections = False
        self.connection_distance = 30.0
        self.max_connections_per_particle = 3

        # Soundscape variables
        self.ambient_drone_freq = 110 
        self.ambient_drone_play_interval = 0.2 
        self.ambient_drone_duration = 0.25 
        self.ambient_drone_timer = 0.0

        self.static_sound_interval = 0.05 
        self.static_sound_timer = 0.0
        self.static_sound_freq_range = (2000, 4000) 

        self.attractor_sound_freq_base = 60 
        self.attractor_sound_duration = 0.15 
        self.attractor_sound_interval = 0.1 
        self.attractor_sound_timer = 0.0

        self.repulsor_sound_freq_base = 800 
        self.repulsor_sound_freq_range = 400 
        self.repulsor_sound_duration = 0.05 
        self.repulsor_sound_cooldown = 0.3 
        self.repulsor_sound_timers = {} # Tracks cooldown for each repulsor ID

        self.reset_program() # Initialize with some particles

    def reset_program(self):
        self.particles = []
        self.max_particles = 10
        self.particle_spawn_rate = 1.0
        self.random_perturbation_strength = 20.0
        self.global_turbulence_strength = 0.0

        self.attractor_active = False
        self.attractor_pos = (0.0, 0.0)
        self.attractor_strength = 200.0
        self.attractor_duration = 5.0
        self.attractor_cooldown = 5.0
        self.attractor_timer = 0.0
        self.attractor_is_cooldown = False
        self.attractor_movement_type = 'random_jump'
        self.attractor_circular_angle = 0.0
        self.attractor_circular_radius = 80.0
        self.attractor_circular_speed = 0.5
        self.attractor_center_x = self.screen_width / 2
        self.attractor_center_y = self.screen_height / 2

        self.repulsors = []
        self.max_repulsors = 0
        self.repulsor_spawn_interval = 8.0
        self.repulsor_spawn_timer = 0.0
        self.repulsor_strength = 250.0
        self.repulsor_radius = 40.0
        self.repulsor_duration = 3.0
        self.repulsor_angle_offset = random.uniform(0, 2 * math.pi)

        self.progression_stage = 0
        self.stage_timer = 0.0
        self.paused = False
        self.static_pixel_count = 0
        
        self.enable_connections = False
        self.connection_distance = 30.0
        self.max_connections_per_particle = 3
        
        # Reset soundscape values
        self.ambient_drone_freq = 110
        self.ambient_drone_play_interval = 0.2
        self.ambient_drone_duration = 0.25
        self.ambient_drone_timer = 0.0

        self.static_sound_interval = 0.05
        self.static_sound_timer = 0.0
        self.static_sound_freq_range = (2000, 4000)

        self.attractor_sound_freq_base = 60
        self.attractor_sound_duration = 0.15
        self.attractor_sound_interval = 0.1
        self.attractor_sound_timer = 0.0
        
        self.repulsor_sound_freq_base = 800
        self.repulsor_sound_freq_range = 400
        self.repulsor_sound_duration = 0.05
        self.repulsor_sound_cooldown = 0.3
        self.repulsor_sound_timers = {}
        
        # Spawn initial particles
        for _ in range(self.max_particles // 2):
            self._spawn_particle()

    def _spawn_particle(self):
        x = random.uniform(0, self.screen_width)
        y = random.uniform(0, self.screen_height)
        self.particles.append(Particle(x, y, self.screen_width, self.screen_height))

    def _spawn_repulsor(self):
        if len(self.repulsors) < self.max_repulsors:
            x = random.uniform(self.repulsor_radius, self.screen_width - self.repulsor_radius)
            y = random.uniform(self.repulsor_radius, self.screen_height - self.repulsor_radius)
            # Use object ID as unique identifier for sound timers
            new_repulsor = {
                'id': random.randint(0, 1000000), # Simple unique ID
                'pos': (x, y),
                'strength': self.repulsor_strength,
                'radius': self.repulsor_radius,
                'timer': 0.0,
                'movement_type': 'random_jump' # Default
            }
            if self.progression_stage >= 5: # Repulsors also start moving in patterns later
                 new_repulsor['movement_type'] = random.choice(['sine_wave_x', 'sine_wave_y'])
                 new_repulsor['start_x'] = x
                 new_repulsor['start_y'] = y
                 new_repulsor['amplitude'] = random.uniform(20.0, 50.0)
                 new_repulsor['frequency'] = random.uniform(0.5, 1.5) # oscillations per second
                 new_repulsor['phase_offset'] = random.uniform(0, 2 * math.pi)

            self.repulsors.append(new_repulsor)
            Sound.play_tone(100, 0.05) # Repulsor appeared sound
            self.repulsor_sound_timers[new_repulsor['id']] = 0.0 # Initialize timer

    def update(self, delta: float):
        # Input handling with debouncing
        if Input.is_key_pressed('space'):
            if not self._space_key_pressed:
                self._space_key_pressed = True
                self.reset_program()
                Sound.play_tone(440, 0.1) # Simple reset sound
        else:
            self._space_key_pressed = False

        if Input.is_key_pressed('p'):
            if not self._p_key_pressed:
                self._p_key_pressed = True
                self.paused = not self.paused
                Sound.play_tone(660 if self.paused else 880, 0.05)
        else:
            self._p_key_pressed = False
        
        if Input.is_key_pressed('a'): # Add more particles
            if not self._a_key_pressed:
                self._a_key_pressed = True
                for _ in range(5):
                    # Allow exceeding max_particles for manual addition, up to a limit
                    if len(self.particles) < self.max_particles * 2: 
                        self._spawn_particle()
                Sound.play_tone(1000, 0.03)
        else:
            self._a_key_pressed = False

        if self.paused:
            return

        # Progression
        self.stage_timer += delta
        if self.progression_stage < len(self.stage_durations) and \
           self.stage_timer >= self.stage_durations[self.progression_stage]:
            
            self.progression_stage += 1
            Sound.play_tone(220 + self.progression_stage * 110, 0.1) # Ascending tone for stage change

            if self.progression_stage == 1: # Basic movement, more particles, subtle drone
                self.max_particles = 30
                self.particle_spawn_rate = 2.0
                self.random_perturbation_strength = 40.0
                self.static_pixel_count = 50
                self.ambient_drone_freq = 150
                self.ambient_drone_play_interval = 0.18
                self.ambient_drone_duration = 0.2
            elif self.progression_stage == 2: # Attractors introduced, drone deepens, static more present
                self.max_particles = 60
                self.particle_spawn_rate = 3.0
                self.random_perturbation_strength = 60.0
                self.attractor_strength = 300.0
                self.attractor_duration = 4.0
                self.attractor_cooldown = 4.0
                self.static_pixel_count = 100
                self.global_turbulence_strength = 10.0
                self.ambient_drone_freq = 180
                self.ambient_drone_play_interval = 0.15
                self.ambient_drone_duration = 0.18
                self.attractor_sound_freq_base = 80 # Attractor hum
            elif self.progression_stage == 3: # Repulsors introduced, more chaos, drone more complex
                self.max_particles = 100
                self.particle_spawn_rate = 4.0
                self.random_perturbation_strength = 80.0
                self.attractor_strength = 400.0
                self.attractor_duration = 3.0
                self.attractor_cooldown = 3.0
                self.max_repulsors = 1 
                self.repulsor_spawn_interval = 6.0
                self.static_pixel_count = 150
                self.global_turbulence_strength = 20.0
                self.ambient_drone_freq = 220
                self.ambient_drone_play_interval = 0.12
                self.ambient_drone_duration = 0.15
                self.repulsor_sound_freq_base = 1000 # Repulsor buzz
                self.repulsor_sound_freq_range = 500
                self.enable_connections = True # Introduce connection lines
                self.connection_distance = 40.0
                self.max_connections_per_particle = 4
            elif self.progression_stage == 4: # Attractor circular movement, more repulsors, higher intensities
                self.max_particles = 150
                self.particle_spawn_rate = 5.0
                self.random_perturbation_strength = 100.0
                self.attractor_strength = 500.0
                self.attractor_duration = 2.0
                self.attractor_cooldown = 2.0
                self.attractor_movement_type = 'circular_orbit' # Attractor starts orbiting
                self.attractor_circular_radius = 100.0
                self.attractor_circular_speed = 0.8
                self.max_repulsors = 2
                self.repulsor_spawn_interval = 4.0
                self.repulsor_strength = 350.0
                self.repulsor_radius = 50.0
                self.static_pixel_count = 200
                self.global_turbulence_strength = 30.0
                self.ambient_drone_freq = 280
                self.ambient_drone_play_interval = 0.1
                self.ambient_drone_duration = 0.12
                self.attractor_sound_freq_base = 100 
                self.repulsor_sound_freq_base = 1200 
                self.connection_distance = 50.0
                self.max_connections_per_particle = 5
            elif self.progression_stage == 5: # Repulsors move in patterns, peak complexity
                self.max_particles = 200
                self.particle_spawn_rate = 6.0
                self.random_perturbation_strength = 120.0
                self.attractor_strength = 600.0
                self.attractor_duration = 1.5
                self.attractor_cooldown = 1.5
                self.attractor_movement_type = 'sine_wave' # Attractor changes to sine wave
                self.attractor_center_x = self.screen_width / 2
                self.attractor_center_y = self.screen_height / 2
                self.attractor_sine_amplitude_x = 120.0
                self.attractor_sine_amplitude_y = 80.0
                self.attractor_sine_freq_x = 0.7
                self.attractor_sine_freq_y = 1.0
                self.max_repulsors = 3
                self.repulsor_spawn_interval = 2.0
                self.repulsor_strength = 450.0
                self.repulsor_radius = 60.0
                self.static_pixel_count = 250
                self.global_turbulence_strength = 40.0
                self.ambient_drone_freq = 350
                self.ambient_drone_play_interval = 0.08
                self.ambient_drone_duration = 0.1
                self.attractor_sound_freq_base = 120 
                self.repulsor_sound_freq_base = 1500
                self.static_sound_freq_range = (3000, 6000)
                self.connection_distance = 60.0
                self.max_connections_per_particle = 6
            elif self.progression_stage == 6: # Ultra chaos - everything intensified
                self.max_particles = 250
                self.particle_spawn_rate = 7.0
                self.random_perturbation_strength = 150.0
                self.attractor_strength = 700.0
                self.attractor_duration = 1.0
                self.attractor_cooldown = 1.0
                self.attractor_movement_type = random.choice(['circular_orbit', 'sine_wave']) # Randomize movement type again
                self.max_repulsors = 4
                self.repulsor_spawn_interval = 1.5
                self.repulsor_strength = 500.0
                self.repulsor_radius = 70.0
                self.static_pixel_count = 300
                self.global_turbulence_strength = 50.0
                self.ambient_drone_freq = 400
                self.ambient_drone_play_interval = 0.07
                self.ambient_drone_duration = 0.09
                self.attractor_sound_freq_base = 150
                self.repulsor_sound_freq_base = 1800
                self.static_sound_freq_range = (4000, 7000)
                self.connection_distance = 70.0
                self.max_connections_per_particle = 7

        # Particle spawning
        if len(self.particles) < self.max_particles:
            self.spawn_timer += delta
            if self.spawn_timer >= 1.0 / self.particle_spawn_rate:
                self._spawn_particle()
                self.spawn_timer = 0.0

        # Attractor logic (starts from Stage 2)
        if self.progression_stage >= 2: 
            self.attractor_timer += delta
            if self.attractor_is_cooldown:
                if self.attractor_timer >= self.attractor_cooldown:
                    self.attractor_is_cooldown = False
                    self.attractor_timer = 0.0
                    self.attractor_active = False 
            else: 
                if not self.attractor_active:
                    if self.attractor_timer >= random.uniform(2.0, self.attractor_cooldown * 1.5): 
                        self.attractor_active = True
                        if self.attractor_movement_type == 'random_jump':
                            self.attractor_pos = (random.uniform(50.0, self.screen_width - 50.0), random.uniform(50.0, self.screen_height - 50.0))
                        elif self.attractor_movement_type == 'circular_orbit':
                            self.attractor_circular_angle = random.uniform(0, 2 * math.pi) # Start at a random point
                            self.attractor_pos = (self.attractor_center_x + math.cos(self.attractor_circular_angle) * self.attractor_circular_radius,
                                                  self.attractor_center_y + math.sin(self.attractor_circular_angle) * self.attractor_circular_radius)
                        elif self.attractor_movement_type == 'sine_wave':
                            # Position will be calculated dynamically, set a starting point
                            self.attractor_pos = (self.attractor_center_x, self.attractor_center_y)

                        self.attractor_timer = 0.0
                        Sound.play_tone(1500, 0.02) # Attractor appeared sound
                else: # Attractor is active
                    # Update attractor position if it's following a pattern
                    if self.attractor_movement_type == 'circular_orbit':
                        self.attractor_circular_angle += self.attractor_circular_speed * delta
                        self.attractor_pos = (self.attractor_center_x + math.cos(self.attractor_circular_angle) * self.attractor_circular_radius,
                                              self.attractor_center_y + math.sin(self.attractor_circular_angle) * self.attractor_circular_radius)
                    elif self.attractor_movement_type == 'sine_wave':
                        current_time_offset = self.attractor_timer + self.stage_timer # Use overall time for smooth sine
                        sx = self.attractor_center_x + math.sin(current_time_offset * self.attractor_sine_freq_x) * self.attractor_sine_amplitude_x
                        sy = self.attractor_center_y + math.cos(current_time_offset * self.attractor_sine_freq_y) * self.attractor_sine_amplitude_y
                        self.attractor_pos = (sx, sy)

                    if self.attractor_timer >= self.attractor_duration:
                        self.attractor_active = False
                        self.attractor_is_cooldown = True
                        self.attractor_timer = 0.0
                        Sound.play_tone(700, 0.02) # Attractor disappeared sound

        # Repulsor logic (starts from Stage 3)
        if self.progression_stage >= 3:
            self.repulsor_spawn_timer += delta
            if self.repulsor_spawn_timer >= self.repulsor_spawn_interval:
                self._spawn_repulsor()
                self.repulsor_spawn_timer = 0.0 # Reset for next spawn

            # Update and remove expired repulsors
            active_repulsors = []
            removed_repulsor_ids = set(self.repulsor_sound_timers.keys())
            for repulsor in self.repulsors:
                repulsor['timer'] += delta
                
                # Update repulsor position if it's following a pattern
                if repulsor['movement_type'] == 'sine_wave_x':
                    new_x = repulsor['start_x'] + math.sin(repulsor['timer'] * repulsor['frequency'] + repulsor['phase_offset']) * repulsor['amplitude']
                    repulsor['pos'] = (new_x, repulsor['start_y'])
                elif repulsor['movement_type'] == 'sine_wave_y':
                    new_y = repulsor['start_y'] + math.sin(repulsor['timer'] * repulsor['frequency'] + repulsor['phase_offset']) * repulsor['amplitude']
                    repulsor['pos'] = (repulsor['start_x'], new_y)

                if repulsor['timer'] < self.repulsor_duration:
                    active_repulsors.append(repulsor)
                    removed_repulsor_ids.discard(repulsor['id'])
                else:
                    Sound.play_tone(300, 0.03) # Repulsor disappeared sound
            self.repulsors = active_repulsors
            for repulsor_id in removed_repulsor_ids:
                if repulsor_id in self.repulsor_sound_timers: # Check if key exists before deleting
                    del self.repulsor_sound_timers[repulsor_id]


        # Update all particles
        for particle in self.particles:
            particle.update(delta, self.random_perturbation_strength, 
                             self.attractor_pos if self.attractor_active else None, 
                             self.attractor_strength if self.attractor_active else 0.0,
                             self.repulsors,
                             self.global_turbulence_strength)

        # Soundscape Updates

        # Ambient drone
        self.ambient_drone_timer += delta
        if self.ambient_drone_timer >= self.ambient_drone_play_interval:
            # Vary frequency slightly for a more organic drone
            freq = self.ambient_drone_freq + random.uniform(-self.ambient_drone_freq * 0.1, self.ambient_drone_freq * 0.1)
            Sound.play_tone(int(freq), self.ambient_drone_duration)
            self.ambient_drone_timer = 0.0

        # Static noise (related to static_pixel_count)
        if self.static_pixel_count > 0:
            self.static_sound_timer += delta
            if self.static_sound_timer >= self.static_sound_interval:
                if random.random() < self.static_pixel_count / 300.0: # Chance to play static increases with count
                    freq = random.uniform(self.static_sound_freq_range[0], self.static_sound_freq_range[1])
                    Sound.play_tone(int(freq), 0.01) # Very short burst for static
                self.static_sound_timer = 0.0
            
            # Also draw static pixels here
            for _ in range(self.static_pixel_count // 2): # Draw half of the static count each frame for flicker
                x = random.randint(0, self.screen_width - 1)
                y = random.randint(0, self.screen_height - 1)
                Render.turn_on_pixel(x, y)


        # Attractor sound
        if self.attractor_active:
            self.attractor_sound_timer += delta
            if self.attractor_sound_timer >= self.attractor_sound_interval:
                # Pitch changes slightly based on remaining duration (more urgent as it fades)
                time_remaining = self.attractor_duration - self.attractor_timer
                if time_remaining > 0:
                    pitch_shift = (self.attractor_duration - time_remaining) / self.attractor_duration * 0.5 # Shifts pitch up by 50% max
                    freq = self.attractor_sound_freq_base * (1 + pitch_shift)
                    Sound.play_tone(int(freq), self.attractor_sound_duration)
                self.attractor_sound_timer = 0.0

        # Repulsor sounds
        for repulsor in self.repulsors:
            repulsor_id = repulsor['id']
            # Ensure the ID is in the sound timers dictionary
            if repulsor_id not in self.repulsor_sound_timers:
                self.repulsor_sound_timers[repulsor_id] = 0.0

            self.repulsor_sound_timers[repulsor_id] += delta
            if self.repulsor_sound_timers[repulsor_id] >= self.repulsor_sound_cooldown:
                # Play a repulsor sound, vary frequency
                freq = self.repulsor_sound_freq_base + random.uniform(-self.repulsor_sound_freq_range, self.repulsor_sound_freq_range)
                Sound.play_tone(int(freq), self.repulsor_sound_duration)
                self.repulsor_sound_timers[repulsor_id] = 0.0 # Reset cooldown for this specific repulsor


    def draw(self):
        # Draw particles and their trails
        for particle in self.particles:
            particle.draw()

        # Draw connection lines between nearby particles
        if self.enable_connections:
            num_particles = len(self.particles)
            for i in range(num_particles):
                p1 = self.particles[i]
                connections_made = 0
                for j in range(i + 1, num_particles): # Avoid duplicate lines and self-connection
                    if connections_made >= self.max_connections_per_particle:
                        break
                    p2 = self.particles[j]
                    dx = p1.x - p2.x
                    dy = p1.y - p2.y
                    dist_sq = dx*dx + dy*dy
                    
                    if dist_sq < self.connection_distance * self.connection_distance:
                        Render.draw_line(int(p1.x), int(p1.y), int(p2.x), int(p2.y))
                        connections_made += 1

        
        # Draw attractor if active with a pulsing effect
        if self.attractor_active:
            pulse_radius = 5 + 3 * (1 + math.sin(self.attractor_timer * 5)) # Pulsing between 5 and 8
            Render.draw_circle(int(self.attractor_pos[0]), int(self.attractor_pos[1]), int(pulse_radius), filled=False)
            Render.draw_line(int(self.attractor_pos[0]) - 8, int(self.attractor_pos[1]), int(self.attractor_pos[0]) + 8, int(self.attractor_pos[1]))
            Render.draw_line(int(self.attractor_pos[0]), int(self.attractor_pos[1]) - 8, int(self.attractor_pos[0]), int(self.attractor_pos[1]) + 8)

        # Draw repulsors
        for repulsor in self.repulsors:
            rx, ry = repulsor['pos']
            r_radius = repulsor['radius']
            # Jittering/spiky effect for repulsor
            jitter_offset = 2 * math.sin(repulsor['timer'] * 10) 
            Render.draw_rect(int(rx - r_radius - jitter_offset), int(ry - r_radius - jitter_offset), 
                             int(r_radius * 2 + jitter_offset * 2), int(r_radius * 2 + jitter_offset * 2), filled=False)
            Render.draw_line(int(rx - 5), int(ry - 5), int(rx + 5), int(ry + 5))
            Render.draw_line(int(rx - 5), int(ry + 5), int(rx + 5), int(ry - 5))

        # Draw UI/debug info
        Render.draw_text(f"Particles: {len(self.particles)} / {self.max_particles}", 5, 5)
        Render.draw_text(f"Stage: {self.progression_stage} / {len(self.stage_durations)}", 5, 20)
        if self.paused:
            Render.draw_text("PAUSED", self.screen_width - 70, 5)

    def get_instructions(self) -> str:
        return "Press 'space' to reset. Press 'p' to pause/unpause. Press 'a' to add particles."

    def get_next_idea(self) -> list[str]:
        return ["Particle types", "User interaction", "Persistent elements"]
