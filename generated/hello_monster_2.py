import math
import random
from generated.helpers import Render, Input, Sound


# The math and random modules are already imported for use.
# For example:
# import math
# import random

class Program:
    def __init__(self):
        self.width = 400
        self.height = 300
        self.center_x = self.width // 2
        self.center_y = self.height // 2

        self.monster_state = 0  # Represents the progression of the monster's revelation
        self.interaction_count = 0 # How many times the user has interacted
        self.last_interaction_time = 0.0
        self.interaction_cooldown = 0.5 # seconds between valid interactions

        self.particles = [] # List of [x, y, vx, vy, life_timer, max_life_timer]
        self.max_particles = 300
        self.particle_burst_size = 10
        self.particle_speed_base = 30.0 # pixels per second
        self.particle_life_base = 2.0 # seconds

        self.ambient_pulse_timer = 0.0
        self.ambient_pulse_speed = 1.0 # Hz
        self.ambient_pulse_max_radius = 50
        self.ambient_pulse_min_radius = 20

        self.energy_lines = [] # List of [x1, y1, x2, y2, life_timer, max_life_timer]
        self.max_energy_lines = 50
        self.line_life_base = 1.5

        self.floating_forms = [] # List of [x, y, radius, life_timer, max_life_timer] for higher states
        self.max_floating_forms = 10

        # Thresholds for state progression
        self.state_thresholds = [0, 3, 7, 12, 18, 25, 35] # Interaction counts to reach new states

        # Soundscape variables
        self.last_ambient_sound_time = 0.0
        self.ambient_sound_interval = 2.0 # seconds between ambient notes/chords
        self.current_active_sound_sequence = [] # List of [freq, duration, delay_timer, original_delay]
        self.current_sound_sequence_idx = 0

        self._init_sound_patterns()

    def _init_sound_patterns(self):
        # Define ambient sound sequences for each state
        self.ambient_patterns = {
            0: [(60, 1.0)], # Single low hum
            1: [(70, 0.8), (75, 0.8)], # Two slightly different hums
            2: [(80, 0.7), (85, 0.7), (90, 0.7)], # Three interwoven hums
            3: [(90, 0.6), (95, 0.6), (102, 0.6)], # Slightly higher, more complex
            4: [(110, 0.5), (115, 0.5), (125, 0.5), (130, 0.5)], # Four notes, more dynamic
            5: [(140, 0.4), (145, 0.4), (155, 0.4), (160, 0.4), (170, 0.4)], # Five notes, more "presence"
            6: [(180, 0.3), (185, 0.3), (195, 0.3), (200, 0.3), (210, 0.3), (220, 0.3)], # Higher, more intricate, 6 notes
            7: [(230, 0.25), (235, 0.25), (245, 0.25), (250, 0.25), (260, 0.25), (270, 0.25), (280, 0.25)] # Even more complex, higher, 7 notes
        }

        # Define interaction sound sequences for 'hello' and 'monster'
        self.hello_patterns = {
            0: [(440, 0.1, 0.0)],
            1: [(440, 0.1, 0.05), (550, 0.1, 0.0)],
            2: [(500, 0.08, 0.05), (600, 0.08, 0.05), (550, 0.08, 0.0)],
            3: [(550, 0.07, 0.04), (650, 0.07, 0.04), (600, 0.07, 0.04), (700, 0.07, 0.0)],
            4: [(600, 0.06, 0.03), (700, 0.06, 0.03), (650, 0.06, 0.03), (750, 0.06, 0.03), (800, 0.06, 0.0)],
            5: [(650, 0.05, 0.02), (750, 0.05, 0.02), (700, 0.05, 0.02), (800, 0.05, 0.02), (850, 0.05, 0.02), (900, 0.05, 0.0)],
            6: [(700, 0.04, 0.01), (800, 0.04, 0.01), (750, 0.04, 0.01), (850, 0.04, 0.01), (900, 0.04, 0.01), (950, 0.04, 0.01), (1000, 0.04, 0.0)],
            7: [(750, 0.03, 0.01), (850, 0.03, 0.01), (800, 0.03, 0.01), (900, 0.03, 0.01), (950, 0.03, 0.01), (1000, 0.03, 0.01), (1050, 0.03, 0.01), (1100, 0.03, 0.0)]
        }

        self.monster_patterns = {
            0: [(220, 0.15, 0.0)],
            1: [(220, 0.15, 0.08), (180, 0.15, 0.0)],
            2: [(180, 0.12, 0.06), (150, 0.12, 0.06), (200, 0.12, 0.0)],
            3: [(150, 0.1, 0.05), (120, 0.1, 0.05), (100, 0.1, 0.05), (160, 0.1, 0.0)],
            4: [(120, 0.09, 0.04), (90, 0.09, 0.04), (70, 0.09, 0.04), (130, 0.09, 0.04), (110, 0.09, 0.0)],
            5: [(100, 0.08, 0.03), (80, 0.08, 0.03), (60, 0.08, 0.03), (120, 0.08, 0.03), (100, 0.08, 0.03), (140, 0.08, 0.0)],
            6: [(80, 0.07, 0.02), (70, 0.07, 0.02), (50, 0.07, 0.02), (100, 0.07, 0.02), (90, 0.07, 0.02), (110, 0.07, 0.02), (130, 0.07, 0.0)],
            7: [(60, 0.06, 0.01), (50, 0.06, 0.01), (40, 0.06, 0.01), (90, 0.06, 0.01), (80, 0.06, 0.01), (100, 0.06, 0.01), (120, 0.06, 0.01), (140, 0.06, 0.0)]
        }


    def _trigger_monster_response(self, interaction_type: str):
        # Increment interaction count
        self.interaction_count += 1
        
        # Check if we should advance the monster_state
        if self.monster_state + 1 < len(self.state_thresholds) and \
           self.interaction_count >= self.state_thresholds[self.monster_state + 1]:
            self.monster_state += 1

        # Play sound sequence based on interaction type and state
        current_state_pattern = None
        if interaction_type == 'hello':
            current_state_pattern = self.hello_patterns.get(self.monster_state, self.hello_patterns[0])
        elif interaction_type == 'monster':
            current_state_pattern = self.monster_patterns.get(self.monster_state, self.monster_patterns[0])
        
        if current_state_pattern:
            # Reset and start new sequence
            self.current_active_sound_sequence = []
            for freq, dur, delay in current_state_pattern:
                self.current_active_sound_sequence.append([freq, dur, delay, delay]) # [freq, dur, current_delay, original_delay]
            self.current_sound_sequence_idx = 0
            # Play the first note immediately if available
            if self.current_active_sound_sequence:
                note = self.current_active_sound_sequence[0]
                Sound.play_tone(int(note[0]), note[1])
                note[2] = note[3] # Reset delay to original, will decrement in update
                self.current_sound_sequence_idx = 1
            else:
                self.current_active_sound_sequence = [] # Clear if empty pattern


        # Generate particles
        num_particles = self.particle_burst_size + self.monster_state * 3
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = self.particle_speed_base + random.uniform(-10, 20) + self.monster_state * 5
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)
            life = self.particle_life_base + random.uniform(-0.5, 1.0) + self.monster_state * 0.5
            self.particles.append([self.center_x, self.center_y, vx, vy, life, life])

        # Generate energy lines (more as state increases)
        if self.monster_state >= 2:
            num_lines = self.monster_state * 1
            for _ in range(num_lines):
                if len(self.particles) > 1: # Need at least two particles to connect
                    p1 = random.choice(self.particles)
                    p2 = random.choice(self.particles)
                    # Ensure they are not the same particle and close enough
                    if p1 is not p2 and math.dist((p1[0], p1[1]), (p2[0], p2[1])) < 150 + self.monster_state * 10:
                        life = self.line_life_base + self.monster_state * 0.3
                        self.energy_lines.append([p1[0], p1[1], p2[0], p2[1], life, life])
        
        # Generate floating forms for higher states
        if self.monster_state >= 5 and random.random() < 0.7:
            num_forms = random.randint(1, 2)
            for _ in range(num_forms):
                x = random.randint(50, self.width - 50)
                y = random.randint(50, self.height - 50)
                radius = random.randint(5, 15) + self.monster_state * 2
                life = 3.0 + self.monster_state * 0.5
                self.floating_forms.append([x, y, radius, life, life])

                
        # Trim excess particles/lines/forms if any
        self.particles = self.particles[-self.max_particles:]
        self.energy_lines = self.energy_lines[-self.max_energy_lines:]
        self.floating_forms = self.floating_forms[-self.max_floating_forms:]


    def update(self, delta: float):
        self.ambient_pulse_timer += delta
        current_time = self.ambient_pulse_timer # Use this as a general time reference

        # Handle user input
        if current_time - self.last_interaction_time > self.interaction_cooldown:
            if Input.is_key_pressed('h'):
                self._trigger_monster_response('hello')
                self.last_interaction_time = current_time
            elif Input.is_key_pressed('m'):
                self._trigger_monster_response('monster')
                self.last_interaction_time = current_time

        # Update and play interaction sound sequence
        if self.current_active_sound_sequence and self.current_sound_sequence_idx < len(self.current_active_sound_sequence):
            # The note that was just played already decremented its delay, we only check for subsequent notes
            previous_note_index = self.current_sound_sequence_idx - 1
            if previous_note_index >= 0:
                self.current_active_sound_sequence[previous_note_index][2] -= delta
                if self.current_active_sound_sequence[previous_note_index][2] <= 0:
                    # Time to play the next note in the sequence
                    note = self.current_active_sound_sequence[self.current_sound_sequence_idx]
                    Sound.play_tone(int(note[0]), note[1])
                    note[2] = note[3] # Reset its internal delay timer to original
                    self.current_sound_sequence_idx += 1
        elif self.current_active_sound_sequence and self.current_sound_sequence_idx >= len(self.current_active_sound_sequence):
             # Sequence finished playing, clear it
            self.current_active_sound_sequence = []


        # Update ambient soundscape
        if current_time - self.last_ambient_sound_time > self.ambient_sound_interval:
            # Play a random note from the current ambient pattern
            current_ambient_pattern = self.ambient_patterns.get(self.monster_state, self.ambient_patterns[0])
            if current_ambient_pattern:
                note_to_play = random.choice(current_ambient_pattern)
                Sound.play_tone(int(note_to_play[0] + random.uniform(-2, 2)), note_to_play[1])
            
            # Slightly vary interval for more organic feel
            self.ambient_sound_interval = 2.0 - (self.monster_state * 0.15) + random.uniform(-0.5, 0.5)
            self.ambient_sound_interval = max(0.5, self.ambient_sound_interval) # Ensure it doesn't get too fast
            self.last_ambient_sound_time = current_time

        # Update particles
        new_particles = []
        for p in self.particles:
            p[0] += p[2] * delta # x
            p[1] += p[3] * delta # y
            p[4] -= delta # life_timer
            if p[4] > 0:
                if 0 <= p[0] < self.width and 0 <= p[1] < self.height:
                    new_particles.append(p)
        self.particles = new_particles

        # Update energy lines
        new_energy_lines = []
        for line in self.energy_lines:
            line[4] -= delta # life_timer
            if line[4] > 0:
                new_energy_lines.append(line)
        self.energy_lines = new_energy_lines

        # Update floating forms
        new_floating_forms = []
        for form in self.floating_forms:
            form[3] -= delta # life_timer
            if form[3] > 0:
                # Add some subtle movement
                form[0] += math.sin(current_time * 0.5 + form[0] * 0.01) * 5 * delta
                form[1] += math.cos(current_time * 0.7 + form[1] * 0.01) * 5 * delta
                new_floating_forms.append(form)
        self.floating_forms = new_floating_forms

        # As monster state increases, continuously add some ambient particles
        if self.monster_state >= 1 and random.random() < (0.05 + self.monster_state * 0.01) * delta * 60: # Chance per frame
            angle = random.uniform(0, 2 * math.pi)
            speed = self.particle_speed_base / 2 + self.monster_state * 2
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)
            life = self.particle_life_base / 2 + self.monster_state * 0.2
            self.particles.append([self.center_x, self.center_y, vx, vy, life, life])
            self.particles = self.particles[-self.max_particles:]


    def draw(self):
        # Draw ambient pulse (always present)
        pulse_factor = (math.sin(self.ambient_pulse_timer * self.ambient_pulse_speed * 2 * math.pi) + 1) / 2 # 0 to 1
        current_radius = int(self.ambient_pulse_min_radius + pulse_factor * (self.ambient_pulse_max_radius - self.ambient_pulse_min_radius))
        
        # Increase pulse intensity/size based on monster state
        current_radius += self.monster_state * 5
        
        Render.draw_circle(self.center_x, self.center_y, current_radius, filled=False)

        # Draw particles
        for p in self.particles:
            fade_alpha = p[4] / p[5] # Remaining life / Max life, for visual discretion
            if fade_alpha > 0.1: # Only draw if sufficiently "bright"
                Render.turn_on_pixel(int(p[0]), int(p[1]))
                # Render larger particles for higher states
                if self.monster_state >= 3:
                     Render.draw_circle(int(p[0]), int(p[1]), 1, filled=True)
                if self.monster_state >= 5:
                     Render.draw_circle(int(p[0]), int(p[1]), 2, filled=False)


        # Draw energy lines
        for line in self.energy_lines:
            fade_alpha = line[4] / line[5]
            if fade_alpha > 0.1:
                Render.draw_line(int(line[0]), int(line[1]), int(line[2]), int(line[3]))
        
        # Additional visual elements based on monster state
        if self.monster_state >= 3:
            # Draw a pulsating core or eye
            core_radius = 5 + int(pulse_factor * (5 + self.monster_state * 2))
            Render.draw_circle(self.center_x, self.center_y, core_radius, filled=True)

        if self.monster_state >= 4:
            # Draw abstract geometric shapes or a grid growing from the center
            num_spokes = 4 + self.monster_state * 2
            for i in range(num_spokes):
                angle = i * (2 * math.pi / num_spokes) + self.ambient_pulse_timer * 0.1
                x_end = self.center_x + int(math.cos(angle) * (100 + self.monster_state * 10))
                y_end = self.center_y + int(math.sin(angle) * (100 + self.monster_state * 10))
                Render.draw_line(self.center_x, self.center_y, x_end, y_end)

        if self.monster_state >= 5:
            # Draw floating geometric forms
            for form in self.floating_forms:
                fade_alpha = form[3] / form[4]
                if fade_alpha > 0.1:
                    Render.draw_circle(int(form[0]), int(form[1]), int(form[2] * fade_alpha), filled=False)
                    # Add a smaller filled circle inside for more depth
                    Render.draw_circle(int(form[0]), int(form[1]), int(form[2] * 0.3 * fade_alpha), filled=True)

        if self.monster_state >= 6:
            # Draw a more complex, evolving central form
            shape_sides = 3 + (self.monster_state % 4)
            angle_step = 2 * math.pi / shape_sides
            current_rotation = self.ambient_pulse_timer * 0.2
            outer_radius = 40 + self.monster_state * 5 + int(pulse_factor * 10)
            
            # Draw the outer polygon
            for i in range(shape_sides):
                x1 = self.center_x + int(math.cos(i * angle_step + current_rotation) * outer_radius)
                y1 = self.center_y + int(math.sin(i * angle_step + current_rotation) * outer_radius)
                x2 = self.center_x + int(math.cos((i + 1) * angle_step + current_rotation) * outer_radius)
                y2 = self.center_y + int(math.sin((i + 1) * angle_step + current_rotation) * outer_radius)
                Render.draw_line(x1, y1, x2, y2)
            
            # Draw an inner, rotating rectangle
            inner_rect_size = 20 + self.monster_state * 3
            rect_x = self.center_x + int(math.cos(current_rotation * 1.5) * 10) - inner_rect_size // 2
            rect_y = self.center_y + int(math.sin(current_rotation * 1.3) * 10) - inner_rect_size // 2
            Render.draw_rect(rect_x, rect_y, inner_rect_size, inner_rect_size, filled=False)


    def get_instructions(self) -> str:
        return "Press 'H' to say Hello. Press 'M' to acknowledge the Monster. Listen to its evolving soundscape."

    def get_next_idea(self) -> list[str]:
        return ["Pattern Weaving", "Neural Tendrils"]
