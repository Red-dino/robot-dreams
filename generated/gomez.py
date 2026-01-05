import math
import random
from generated.helpers import Render, Input, Sound


import math
import random

class GorillaPart:
    def __init__(self, base_x, base_y, initial_r, final_r, grow_speed):
        self.base_x = base_x # Original, un-animated X position
        self.base_y = base_y # Original, un-animated Y position
        self.x = base_x      # Current animated X position
        self.y = base_y      # Current animated Y position
        self.initial_r = initial_r
        self.final_r = final_r
        self.grow_speed = grow_speed
        self.current_r = initial_r
        self.pulse_offset = 0.0
        self.active = False
        self.filled = False
        self.target_pulse_strength = 0.0
        self.current_pulse_strength = 0.0

    def update(self, delta):
        if not self.active:
            return

        # Grow towards final_r
        if self.current_r < self.final_r:
            self.current_r = min(self.final_r, self.current_r + self.grow_speed * delta)

        # Update pulse strength
        if self.target_pulse_strength > self.current_pulse_strength:
            self.current_pulse_strength = min(self.target_pulse_strength, self.current_pulse_strength + delta * 10)
        else:
            self.current_pulse_strength = max(0.0, self.current_pulse_strength - delta * 2)
        
        # Calculate pulse offset
        self.pulse_offset = self.final_r * 0.2 * self.current_pulse_strength
    
    def trigger_pulse(self, strength=1.0):
        self.target_pulse_strength = strength

    def set_animated_position(self, new_x, new_y):
        self.x = new_x
        self.y = new_y

class Program:
    def __init__(self):
        self.parts = []
        # Define Gorilla Parts (base_x, base_y, initial_radius, final_radius, growth_speed)
        part_data = [
            (200, 150, 2, 20, 5), # 0: Chest (Core)
            (200, 100, 2, 15, 5), # 1: Head
            (150, 150, 2, 10, 5), # 2: Left Shoulder
            (250, 150, 2, 10, 5), # 3: Right Shoulder
            (150, 170, 2, 12, 5), # 4: Left Upper Arm
            (250, 170, 2, 12, 5), # 5: Right Upper Arm
            (150, 210, 2, 10, 5), # 6: Left Lower Arm
            (250, 210, 2, 10, 5), # 7: Right Lower Arm
            (200, 200, 2, 15, 5), # 8: Hips
            (170, 230, 2, 12, 5), # 9: Left Upper Leg
            (230, 230, 2, 12, 5), # 10: Right Upper Leg
            (170, 270, 2, 10, 5), # 11: Left Lower Leg
            (230, 270, 2, 10, 5)  # 12: Right Lower Leg
        ]
        for data in part_data:
            self.parts.append(GorillaPart(*data))

        self.connections = []
        # Define connections between parts (indices)
        self.connections.append((0, 1)) # Chest - Head
        self.connections.append((0, 2)) # Chest - L Shoulder
        self.connections.append((0, 3)) # Chest - R Shoulder
        self.connections.append((0, 8)) # Chest - Hips
        self.connections.append((2, 4)) # L Shoulder - L Upper Arm
        self.connections.append((3, 5)) # R Shoulder - R Upper Arm
        self.connections.append((4, 6)) # L Upper Arm - L Lower Arm
        self.connections.append((5, 7)) # R Upper Arm - R Lower Arm
        self.connections.append((8, 9)) # Hips - L Upper Leg
        self.connections.append((8, 10)) # Hips - R Upper Leg
        self.connections.append((9, 11)) # L Upper Leg - L Lower Leg
        self.connections.append((10, 12)) # R Upper Leg - R Lower Leg

        self.stage = 0
        self.stage_timer = 0.0
        # Durations for each stage: growth, pulse interaction, then walking
        self.stage_durations = [3.0, 3.0, 4.0, 5.0, 10.0, 15.0, float('inf')] # New stage 6 (walking)
        self.stage_hums = [100, 150, 200, 250, 300, 350, 400] # Base hum frequencies for each stage

        self.gomez_rhythm_interval = 1.0 # Time between automatic Gomez beats
        self.gomez_rhythm_timer = 1.0 # Initial delay for first beat
        self.gomez_rhythm_freq = 440 # Base frequency for Gomez beat tone
        self.gomez_rhythm_tone_duration = 0.1 # Duration of a single Gomez beat tone

        self.is_gomez_pulse_playing = False # True if a Gomez tone is currently sounding
        self.gomez_pulse_play_timer = 0.0 # Time since current Gomez tone started

        self.last_hum_play_time = 0.0 # To play the base hum for a duration periodically
        self.hum_interval = 2.0 # How often to play the hum
        self.hum_duration = 0.5 # Duration of the hum tone

        # Walking animation variables
        self.walk_phase = 0.0 # Current phase in the walk cycle (0 to 2*PI)
        self.walk_speed = 3.0 # How fast the animation cycle runs
        self.limb_swing_amplitude = 15 # Max pixels a limb swings horizontally
        self.body_bob_amplitude = 5 # Max pixels body bobs vertically
        self.limb_y_amplitude = 5 # Max pixels legs/arms move vertically up/down
        self.global_x_offset = 0 # For moving the whole gorilla across the screen
        self.global_y_offset = 0 # Currently unused, but keeps flexibility

        # Initially activate the chest (core)
        self.parts[0].active = True
        self.parts[0].filled = False

    def update(self, delta: float):
        self.stage_timer += delta

        # Stage transition logic
        if self.stage < len(self.stage_durations) - 1 and self.stage_timer >= self.stage_durations[self.stage]:
            self.stage += 1
            self.stage_timer = 0.0
            self._activate_stage_parts()

        # Gomez rhythm timer for automatic beats (active during formation and beat phase)
        if self.stage < 6: # Stops automatic beats once walking begins
            self.gomez_rhythm_timer -= delta
            if self.gomez_rhythm_timer <= 0:
                self._trigger_gomez_pulse(1.0)
                self.gomez_rhythm_timer = self.gomez_rhythm_interval

        # Gomez pulse sound duration management
        if self.is_gomez_pulse_playing:
            self.gomez_pulse_play_timer += delta
            if self.gomez_pulse_play_timer >= self.gomez_rhythm_tone_duration:
                self.is_gomez_pulse_playing = False
                self.gomez_pulse_play_timer = 0.0

        # Periodic hum (background sound for progression)
        if self.stage < 6 and (self.stage_timer - self.last_hum_play_time) >= self.hum_interval:
            Sound.play_tone(self.stage_hums[self.stage], self.hum_duration)
            self.last_hum_play_time = self.stage_timer
        elif self.stage == 6: # Continuous, slightly varied hum for walking
            if (self.stage_timer - self.last_hum_play_time) >= 0.2: # More frequent, shorter hums
                Sound.play_tone(self.stage_hums[self.stage] + random.randint(-20, 20), 0.1)
                self.last_hum_play_time = self.stage_timer

        # Handle walking animation if in the walking stage
        if self.stage == 6:
            self.walk_phase = (self.walk_phase + self.walk_speed * delta) % (2 * math.pi)
            self._apply_walking_animation()
            # Move the entire gorilla across the screen, looping
            self.global_x_offset = (self.global_x_offset + delta * 15) % 450 # move 15 pixels/sec, loop after 450

        # User input for Stage 5 (manual Gomez beat)
        if self.stage == 5 and Input.is_key_pressed('space'):
            if not self.is_gomez_pulse_playing: # Prevent spamming
                self._trigger_gomez_pulse(2.0, force_freq_multiplier=1.5, force_duration_multiplier=1.5)

        # Update all gorilla parts (growth, pulse)
        for part in self.parts:
            part.update(delta)

    def draw(self):
        # Draw connections first (lines)
        for idx1, idx2 in self.connections:
            p1 = self.parts[idx1]
            p2 = self.parts[idx2]
            if p1.active and p2.active:
                Render.draw_line(int(p1.x + self.global_x_offset), int(p1.y + self.global_y_offset),
                                 int(p2.x + self.global_x_offset), int(p2.y + self.global_y_offset))

        # Draw parts (circles)
        for part in self.parts:
            if part.active:
                Render.draw_circle(int(part.x + self.global_x_offset), int(part.y + self.global_y_offset),
                                   int(part.current_r + part.pulse_offset), part.filled)
        
        # Draw ground line in walking stage
        if self.stage == 6:
            Render.draw_line(0, 290, 399, 290) # A simple ground line

    def _activate_stage_parts(self):
        # Stage 0: Chest (already active in __init__)
        if self.stage == 1: # Head, Shoulders
            for i in [1, 2, 3]: self.parts[i].active = True
        elif self.stage == 2: # Upper arms, Hips
            for i in [4, 5, 8]: self.parts[i].active = True
        elif self.stage == 3: # Lower arms, Legs (Full Body Outline)
            for i in [6, 7, 9, 10, 11, 12]: self.parts[i].active = True
        elif self.stage == 4: # Solidification
            for part in self.parts: part.filled = True
        elif self.stage == 5: # Gomez's Beat - fully formed, filled, user interaction
            pass # No new parts activated, just a new phase
        elif self.stage == 6: # Gomez Walks
            # Ensure all parts are fully grown and filled
            for part in self.parts:
                part.current_r = part.final_r
                part.filled = True
            self.global_x_offset = -50 # Start Gomez off-screen slightly to the left

    def _apply_walking_animation(self):
        # Body bob (chest, head, hips)
        body_bob = math.sin(self.walk_phase * 2) * self.body_bob_amplitude * 0.5 # Faster bob
        self.parts[0].set_animated_position(self.parts[0].base_x, self.parts[0].base_y + body_bob) # Chest
        self.parts[1].set_animated_position(self.parts[1].base_x, self.parts[1].base_y + body_bob * 1.2) # Head bobs a bit more
        self.parts[8].set_animated_position(self.parts[8].base_x, self.parts[8].base_y + body_bob * 0.8) # Hips bobs less

        # Legs (opposite motion, left leg forward when right leg back)
        leg_swing_x = math.sin(self.walk_phase) * self.limb_swing_amplitude
        leg_lift_y = abs(math.sin(self.walk_phase)) * self.limb_y_amplitude # Lift foot when swinging forward

        # Left Leg (9: Upper, 11: Lower)
        self.parts[9].set_animated_position(self.parts[9].base_x + leg_swing_x, self.parts[9].base_y + leg_lift_y)
        self.parts[11].set_animated_position(self.parts[11].base_x + leg_swing_x * 1.2, self.parts[11].base_y + leg_lift_y * 1.5)

        # Right Leg (10: Upper, 12: Lower)
        self.parts[10].set_animated_position(self.parts[10].base_x - leg_swing_x, self.parts[10].base_y + leg_lift_y)
        self.parts[12].set_animated_position(self.parts[12].base_x - leg_swing_x * 1.2, self.parts[12].base_y + leg_lift_y * 1.5)

        # Arms (opposite to legs, left arm back when left leg forward)
        arm_swing_x = math.sin(self.walk_phase + math.pi) * self.limb_swing_amplitude # Pi phase offset for opposite
        arm_swing_y = abs(math.sin(self.walk_phase + math.pi)) * self.limb_y_amplitude * 0.5 # Slight vertical arm motion

        # Left Arm (2: Shoulder, 4: Upper, 6: Lower)
        self.parts[2].set_animated_position(self.parts[2].base_x + arm_swing_x * 0.5, self.parts[2].base_y + body_bob) # Shoulder moves less
        self.parts[4].set_animated_position(self.parts[4].base_x + arm_swing_x, self.parts[4].base_y + body_bob + arm_swing_y)
        self.parts[6].set_animated_position(self.parts[6].base_x + arm_swing_x * 1.2, self.parts[6].base_y + body_bob + arm_swing_y * 1.5)

        # Right Arm (3: Shoulder, 5: Upper, 7: Lower)
        self.parts[3].set_animated_position(self.parts[3].base_x - arm_swing_x * 0.5, self.parts[3].base_y + body_bob)
        self.parts[5].set_animated_position(self.parts[5].base_x - arm_swing_x, self.parts[5].base_y + body_bob + arm_swing_y)
        self.parts[7].set_animated_position(self.parts[7].base_x - arm_swing_x * 1.2, self.parts[7].base_y + body_bob + arm_swing_y * 1.5)

        # Head can also have a slight side-to-side wobble
        head_wobble_x = math.sin(self.walk_phase * 3 + math.pi/2) * 2 # Faster, smaller wobble
        # Keep its Y-bob from earlier, only modify X
        self.parts[1].set_animated_position(self.parts[1].base_x + head_wobble_x, self.parts[1].y) 

    def _trigger_gomez_pulse(self, strength, force_freq_multiplier=1.0, force_duration_multiplier=1.0):
        # Trigger visual pulse on all active parts
        for part in self.parts:
            if part.active:
                part.trigger_pulse(strength)

        # Play sound if not already playing a forced pulse (to prevent overlapping sounds)
        if not self.is_gomez_pulse_playing:
            freq = self.gomez_rhythm_freq * force_freq_multiplier
            duration = self.gomez_rhythm_tone_duration * force_duration_multiplier
            Sound.play_tone(int(freq), duration)
            self.is_gomez_pulse_playing = True
            self.gomez_pulse_play_timer = 0.0

    def get_instructions(self) -> str:
        if self.stage < 5:
            return "Witness the ethereal Gomez Gorilla emerge."
        elif self.stage == 5:
            return "Press 'space' to evoke Gomez's primal beat. Soon he will walk..."
        elif self.stage == 6:
            return "Gomez strides with purpose, traversing the dreamscape."
        return "" # Should not be reached

    def get_next_idea(self) -> list[str]:
        return ["Jungle Growth", "Astral Roar", "Evolving Path", "Deeper Woods"]
