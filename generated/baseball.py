import math
import random
from generated.helpers import Render, Input, Sound

import math
import random

class Program:
    def __init__(self):
        self.SCREEN_WIDTH = 400
        self.SCREEN_HEIGHT = 300

        self.game_state = "IDLE" # IDLE, PITCHING, RESULT
        self.level = 1
        self.score = 0
        self.strikes = 0
        self.max_strikes = 3
        self.hits_to_level_up = 5 # Hits required to increase level

        # Automatic pitching timer
        self.auto_pitch_timer = 3.0 # Initial delay before first pitch
        self.auto_pitch_interval_min = 2.0
        self.auto_pitch_interval_max = 4.0

        # Pitch path in 3D perspective
        self.pitch_speed_base = 80 # pixels per second (horizontal speed)
        self.current_pitch_speed = self.pitch_speed_base
        
        self.pitch_start_x = 50.0
        self.pitch_start_y = 260.0 # Pitch starts far away, lower on screen
        self.pitch_end_x = 350.0
        self.pitch_end_y = 180.0 # Pitch ends closer, higher on screen
        
        self.pitch_x = 0.0
        self.pitch_y = 0.0

        # Pitch curve parameters
        self.base_curve_magnitude = 25.0 # Base lateral deviation for curves
        self.current_curve_amplitude = 0.0 # Amplitude for the current pitch's curve
        self.curve_direction_multiplier = 1 # -1 or 1 for curve direction

        # Pitch radius scaling for 3D effect
        self.pitch_radius_min = 2
        self.pitch_radius_max = 30 # Much larger when close
        self.current_pitch_radius = self.pitch_radius_min

        self.swing_active = False
        self.swing_timer = 0.0
        self.swing_duration = 0.1 # seconds the swing hitbox is active

        # Hit window defines the perfect timing zone for the center of the pitch pulse
        self.hit_window_start_x = 290
        self.hit_window_end_x = 330
        self.hit_window_y = self.pitch_end_y # Hit window aligns with pitch_end_y
        self.hit_window_height = 50

        self.last_result_message = ""
        self.result_display_timer = 0.0
        self.result_display_duration = 1.5

        # Dream elements timers and intensities
        self.pitcher_form_timer = 0.0
        self.batter_form_timer = 0.0
        self.environment_pulse_intensity = 0.0 # 0.0 (off) to 1.0 (max)
        self.ambient_hum_frequency = 400 # Base frequency for background sound
        self.ambient_hum_duration_base = 0.5
        self._ambient_hum_countdown = random.uniform(0.5, 2.0)

    def reset_pitch(self):
        self.pitch_x = self.pitch_start_x
        self.pitch_y = self.pitch_start_y
        self.current_pitch_radius = self.pitch_radius_min
        self.swing_active = False
        self.swing_timer = 0.0
        self.game_state = "IDLE"
        self.last_result_message = "" # Clear message upon new pitch readiness
        self.auto_pitch_timer = random.uniform(self.auto_pitch_interval_min, self.auto_pitch_interval_max) # Reset for next automatic pitch
        self.current_curve_amplitude = 0.0 # Reset curve for next pitch

    def update(self, delta: float):
        # Update timers for dream effects
        self.pitcher_form_timer = (self.pitcher_form_timer + delta * 0.5) % (2 * math.pi)
        self.batter_form_timer = (self.batter_form_timer + delta * 0.7) % (2 * math.pi)
        if self.environment_pulse_intensity > 0:
            self.environment_pulse_intensity = max(0.0, self.environment_pulse_intensity - delta * 0.5)

        # Ambient hum sound effect
        self._ambient_hum_countdown -= delta
        if self._ambient_hum_countdown <= 0:
            if self.game_state == "IDLE":
                Sound.play_tone(int(self.ambient_hum_frequency + random.uniform(-50, 50)), self.ambient_hum_duration_base)
            self._ambient_hum_countdown = random.uniform(0.5, 2.0) # Reset countdown

        if self.game_state == "IDLE":
            self.auto_pitch_timer -= delta
            if self.auto_pitch_timer <= 0: # Automatic pitch
                self.game_state = "PITCHING"
                self.pitch_x = self.pitch_start_x
                self.pitch_y = self.pitch_start_y
                
                # Randomize speed based on level
                self.current_pitch_speed = (self.pitch_speed_base + self.level * 5) * random.uniform(0.8, 1.2)
                
                # Randomize curve based on level
                self.current_curve_amplitude = (self.base_curve_magnitude + self.level * 3) * random.uniform(0.5, 1.5)
                self.curve_direction_multiplier = random.choice([-1, 1])

                self.last_result_message = ""
                Sound.play_tone(1000, 0.1) # Pitch initiation sound
            return

        if self.game_state == "PITCHING":
            self.pitch_x += self.current_pitch_speed * delta

            # Calculate progress for 3D scaling and Y position
            progress = (self.pitch_x - self.pitch_start_x) / (self.pitch_end_x - self.pitch_start_x)
            progress = max(0.0, min(1.0, progress)) # Clamp progress between 0 and 1

            # Interpolate base Y position
            base_y = self.pitch_start_y + (self.pitch_end_y - self.pitch_start_y) * progress
            
            # Apply curve to Y position (sine wave peaks in the middle of the path)
            curve_offset = self.current_curve_amplitude * math.sin(progress * math.pi) * self.curve_direction_multiplier
            self.pitch_y = base_y + curve_offset

            # Interpolate radius for 3D effect (quadratic growth)
            self.current_pitch_radius = int(self.pitch_radius_min + (self.pitch_radius_max - self.pitch_radius_min) * (progress ** 2))

            if Input.is_key_pressed('space') and not self.swing_active:
                self.swing_active = True
                self.swing_timer = 0.0
                Sound.play_tone(2000, 0.05) # Swing sound

            if self.swing_active:
                self.swing_timer += delta
                if self.swing_timer >= self.swing_duration:
                    self.swing_active = False # Swing hitbox is gone

            # Check for hit
            # A hit occurs if the swing is active AND the pitch is within the hit window
            # both horizontally and vertically
            if self.swing_active and \
               self.hit_window_start_x <= self.pitch_x <= self.hit_window_end_x and \
               self.hit_window_y - self.hit_window_height / 2 <= self.pitch_y <= self.hit_window_y + self.hit_window_height / 2:
                self.score += 1
                self.last_result_message = "HARMONY!"
                self.environment_pulse_intensity = 1.0 # Trigger environmental pulse
                Sound.play_tone(2500, 0.2) # Hit sound
                if self.score % self.hits_to_level_up == 0: # Level up
                    self.level += 1
                    Sound.play_tone(3000, 0.1) # Level up sound
                self.game_state = "RESULT"
                self.result_display_timer = 0.0

            # Check if pitch passed without a hit
            elif self.pitch_x >= self.pitch_end_x:
                self.strikes += 1
                self.last_result_message = "DISSONANCE."
                Sound.play_tone(300, 0.2) # Miss sound
                
                if self.strikes >= self.max_strikes:
                    self.last_result_message = "VOID CONSUMES. Game Over."
                    Sound.play_tone(100, 0.5) # Game over sound
                    # Reset game state for Game Over
                    self.level = 1
                    self.score = 0
                    self.strikes = 0
                    self.current_pitch_speed = self.pitch_speed_base # Reset speed to base
                
                self.game_state = "RESULT"
                self.result_display_timer = 0.0

        if self.game_state == "RESULT":
            self.result_display_timer += delta
            if self.result_display_timer >= self.result_display_duration:
                self.reset_pitch()
                # If it was a game over, ensure message is cleared for next round
                if "VOID" in self.last_result_message:
                    self.last_result_message = ""

    def draw(self):
        # Dream background / environment pulse effect
        if self.environment_pulse_intensity > 0:
            # Draw concentric circles from the center, fading out
            base_radius = int(self.environment_pulse_intensity * 150)
            for i in range(5):
                r = base_radius - i * 20
                if r > 0:
                    Render.draw_circle(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2, r)

        # Pitcher - radiating geometric form (smaller, farther away)
        pitcher_cx, pitcher_cy = 50, 250 # Farther away visually
        base_size_pitcher = 20 # Smaller size
        rot_angle = self.pitcher_form_timer
        
        for i in range(min(self.level, 5)):
            size = base_size_pitcher + i * 2 + math.sin(rot_angle + i * math.pi/4) * 2
            Render.draw_rect(int(pitcher_cx - size / 2), int(pitcher_cy - size / 2), int(size), int(size))
            Render.draw_line(int(pitcher_cx - size/2), int(pitcher_cy + math.sin(rot_angle + i) * size/4), int(pitcher_cx + size/2), int(pitcher_cy + math.sin(rot_angle + i) * size/4))
            Render.draw_line(int(pitcher_cx + math.cos(rot_angle + i) * size/4), int(pitcher_cy - size/2), int(pitcher_cx + math.cos(rot_angle + i) * size/4), int(pitcher_cy + size/2))

        # Batter - vortex-like geometric form (larger, closer)
        batter_cx, batter_cy = 350, 180 # Closer visually
        base_size_batter = 40 # Larger size
        pulse_scale = 1 + math.sin(self.batter_form_timer * 2) * 0.1
        
        for i in range(min(self.level, 5)):
            current_size = (base_size_batter + i * 3) * pulse_scale
            p1x = int(batter_cx - current_size / 2)
            p1y = int(batter_cy)
            p2x = int(batter_cx + current_size / 2)
            p2y = int(batter_cy - current_size / 2)
            p3x = int(batter_cx + current_size / 2)
            p3y = int(batter_cy + current_size / 2)
            Render.draw_line(p1x, p1y, p2x, p2y)
            Render.draw_line(p2x, p2y, p3x, p3y)
            Render.draw_line(p3x, p3y, p1x, p1y)
            
            if i == 0:
                Render.draw_circle(batter_cx, batter_cy, int(current_size * 0.2))

        # Pitch visualization (moving, scaling pulse for 3D effect)
        if self.game_state == "PITCHING" or self.game_state == "RESULT":
            num_rings = min(self.level + 2, 7)
            # Use the calculated current_pitch_radius for the primary visual
            main_radius = self.current_pitch_radius
            
            # Re-calculate progress for ripple effect, relative to the main sphere's size
            progress = (self.pitch_x - self.pitch_start_x) / (self.pitch_end_x - self.pitch_start_x)
            progress = max(0.0, min(1.0, progress))

            for i in range(num_rings):
                # Rings ripple outwards from the main pitch sphere
                ripple_offset = (i / num_rings) * 0.3 # Each ring slightly behind previous
                current_ring_progress = progress - ripple_offset
                
                if current_ring_progress > 0:
                    ring_size_factor = 1 + (1 - current_ring_progress) * 0.5 # Larger when new, shrinks as it gets older
                    ring_radius_scaled = int(main_radius * ring_size_factor)
                    Render.draw_circle(int(self.pitch_x), int(self.pitch_y), ring_radius_scaled)


        # Draw the 'hit window' for player guidance
        Render.draw_rect(self.hit_window_start_x, int(self.hit_window_y - self.hit_window_height / 2), 
                         self.hit_window_end_x - self.hit_window_start_x, self.hit_window_height)

        # Swing visualization
        if self.swing_active:
            swing_progress = self.swing_timer / self.swing_duration
            swing_radius = int(20 + swing_progress * 30)
            Render.draw_circle(batter_cx, batter_cy, swing_radius)

        # UI elements
        Render.draw_text(f"Level: {self.level}", 10, 10)
        Render.draw_text(f"Harmony: {self.score}", 10, 30)
        Render.draw_text(f"Dissonance: {self.strikes}/{self.max_strikes}", 10, 50)

        # Result message
        if self.last_result_message:
            text_width_estimate = len(self.last_result_message) * 8
            Render.draw_text(self.last_result_message, self.SCREEN_WIDTH // 2 - text_width_estimate // 2, self.SCREEN_HEIGHT // 2)

    def get_instructions(self) -> str:
        return "A pulse will appear automatically. Press 'Space' to project a resonance wave and achieve Harmony."

    def get_next_idea(self) -> list[str]:
        return ["Chasing Spirals", "Harmonic Echoes", "Void Convergence"]