import math
import random
from generated.helpers import Render, Input, Sound


# The math and random modules are already imported and available for use.

class Program:
    # Constants for screen dimensions
    SCREEN_WIDTH = 400
    SCREEN_HEIGHT = 300
    CENTER_X = SCREEN_WIDTH // 2
    CENTER_Y = SCREEN_HEIGHT // 2

    def __init__(self):
        self.money = 0.0  # Represents Cosmic Dust
        self.dust_per_second = 1.0  # Initial dust generation rate
        self.stage = 0  # 0: Seed, 1: Sprout, 2: Crystal, 3: Nebula, 4: Star

        # Data for upgrades: (cost, next_dust_per_second)
        self.upgrade_info = [
            (100.0, 5.0),    # To Sprout (Stage 1)
            (500.0, 25.0),   # To Crystal (Stage 2)
            (2000.0, 100.0), # To Nebula (Stage 3)
            (10000.0, 500.0) # To Star (Stage 4)
        ]

        # Animation timers
        self.pulsation_timer = 0.0
        self.focus_cooldown_timer = 0.0
        self.focus_cooldown_duration = 1.0 # 1 second cooldown for 'space' key

        # Global time accumulator for consistent sound timing and other time-based logic
        self.global_time = 0.0
        self.last_passive_sound_time = 0.0
        self.passive_sound_interval = 0.1 # Interval for subtle background tones

        # Stage-specific animation variables
        self.crystal_rotation = 0.0
        self.nebula_particles = [] # Stores [x, y, life_elapsed, max_life, initial_angle] for stage 3
        self.star_flare_timer = 0.0

    def update(self, delta: float):
        self.global_time += delta
        self.money += self.dust_per_second * delta
        self.pulsation_timer += delta * 5 # Controls speed of general pulsing animation
        self.focus_cooldown_timer = max(0.0, self.focus_cooldown_timer - delta)
        self.crystal_rotation += delta * 0.5 # Controls rotation speed for Crystal Stage
        self.star_flare_timer += delta * 2 # Controls animation speed for Star Stage flares

        # Handle user input: 'space' key to "Focus Energy" for a dust burst
        if Input.is_key_pressed('space') and self.focus_cooldown_timer == 0.0:
            self.money += 10.0 # Grant 10 dust
            self.focus_cooldown_timer = self.focus_cooldown_duration # Reset cooldown
            Sound.play_tone(440, 0.05) # Play a short, distinct tone for interaction

        # Handle upgrade key presses (keys '1' through '4')
        # This loop ensures upgrades are sequential, tied to the current stage
        for i in range(len(self.upgrade_info)):
            if self.stage == i: # Only allow upgrade from the current stage
                upgrade_key = str(i + 1)
                cost, next_dps = self.upgrade_info[i]
                if Input.is_key_pressed(upgrade_key) and self.money >= cost:
                    self.money -= cost
                    self.dust_per_second = next_dps
                    self.stage += 1
                    Sound.play_tone(880, 0.1) # Play a higher-pitched tone for successful upgrade
                    break # Important: Only one upgrade per frame to prevent multiple upgrades from one press

        # Stage-specific update logic for animations and effects
        if self.stage == 3: # Nebula Stage: manage swirling particles
            # Generate new particles periodically
            if random.random() < 0.2: # 20% chance per frame to add a new particle
                angle = random.uniform(0, 2 * math.pi)
                # Particle data: [x, y, current_life, max_life, initial_spawn_angle]
                self.nebula_particles.append([self.CENTER_X, self.CENTER_Y, 0.0, random.uniform(0.5, 1.5), angle])
            
            # Update existing particles and filter out expired ones
            new_particles = []
            for p in self.nebula_particles:
                p[2] += delta # Increment particle's life elapsed
                if p[2] < p[3]: # If particle is still alive
                    # Calculate new position: move outward and swirl
                    progress = p[2] / p[3] # How far along in its life
                    dist_from_center = 10 + progress * 40 # Expand outwards from 10 to 50 pixels
                    swirl_angle_offset = p[4] + progress * 2 * math.pi # Swirl in a circle as it expands
                    p[0] = self.CENTER_X + int(dist_from_center * math.cos(swirl_angle_offset))
                    p[1] = self.CENTER_Y + int(dist_from_center * math.sin(swirl_angle_offset))
                    new_particles.append(p)
            self.nebula_particles = new_particles # Update list with active particles

        # Play a subtle, continuous background tone based on current dust generation rate
        if self.dust_per_second > 0 and (self.global_time - self.last_passive_sound_time) >= self.passive_sound_interval:
            base_freq = 100
            max_freq = 1000
            # Scale frequency logarithmically to make progression feel smoother, especially at higher rates
            scaled_freq = base_freq + (math.log10(self.dust_per_second + 1) / math.log10(self.upgrade_info[-1][1] + 1)) * (max_freq - base_freq)
            scaled_freq = min(max(base_freq, scaled_freq), max_freq) # Clamp frequency within reasonable range
            Sound.play_tone(int(scaled_freq), 0.01) # Very short, subtle tone
            self.last_passive_sound_time = self.global_time

    def draw(self):
        # Base radius for the central entity, modulated by pulsation
        radius_base = 20
        pulsation_scale = 1 + math.sin(self.pulsation_timer) * 0.1 # Pulsates from 0.9 to 1.1 of base size
        current_radius = int(radius_base * pulsation_scale)

        # Draw the "Seed of Existence" based on its current stage
        if self.stage == 0: # Seed Stage: A simple pulsating circle
            Render.draw_circle(self.CENTER_X, self.CENTER_Y, current_radius, filled=True)
            Render.draw_text("Seed of Existence", self.CENTER_X - 60, self.CENTER_Y + 30)

        elif self.stage == 1: # Sprout Stage: Central circle with radiating "roots" or "vines"
            Render.draw_circle(self.CENTER_X, self.CENTER_Y, current_radius + 5, filled=True) # Slightly larger core
            num_roots = 6
            for i in range(num_roots):
                # Roots sway subtly with animation timer
                angle = (2 * math.pi / num_roots) * i + math.sin(self.pulsation_timer * 0.2 + i) * 0.2
                x1 = self.CENTER_X + int((current_radius + 5) * math.cos(angle))
                y1 = self.CENTER_Y + int((current_radius + 5) * math.sin(angle))
                x2 = self.CENTER_X + int((current_radius + 30) * math.cos(angle))
                y2 = self.CENTER_Y + int((current_radius + 30) * math.sin(angle))
                Render.draw_line(x1, y1, x2, y2) # Draw each root
            Render.draw_text("Sprout of Potential", self.CENTER_X - 60, self.CENTER_Y + 40)

        elif self.stage == 2: # Crystal Stage: Central core with rotating geometric facets
            Render.draw_circle(self.CENTER_X, self.CENTER_Y, current_radius + 10, filled=True) # Larger core
            num_facets = 6
            facet_outer_radius = current_radius + 20
            for i in range(num_facets):
                # Rotate facets around the center
                angle_base = (2 * math.pi / num_facets) * i + self.crystal_rotation
                
                # Define points for a diamond-like facet originating from the center
                p1x = self.CENTER_X + int(facet_outer_radius * math.cos(angle_base))
                p1y = self.CENTER_Y + int(facet_outer_radius * math.sin(angle_base))
                p2x = self.CENTER_X + int((facet_outer_radius * 0.7) * math.cos(angle_base + 0.5))
                p2y = self.CENTER_Y + int((facet_outer_radius * 0.7) * math.sin(angle_base + 0.5))
                p3x = self.CENTER_X + int((facet_outer_radius * 0.7) * math.cos(angle_base - 0.5))
                p3y = self.CENTER_Y + int((facet_outer_radius * 0.7) * math.sin(angle_base - 0.5))

                # Draw lines to form the facet. Looks like a radiating crystal structure.
                Render.draw_line(self.CENTER_X, self.CENTER_Y, p1x, p1y)
                Render.draw_line(p1x, p1y, p2x, p2y)
                Render.draw_line(p1x, p1y, p3x, p3y)
                Render.draw_line(p2x, p2y, p3x, p3y) 
            Render.draw_text("Crystal of Insight", self.CENTER_X - 60, self.CENTER_Y + 50)

        elif self.stage == 3: # Nebula Stage: Large pulsating core with swirling ethereal particles
            Render.draw_circle(self.CENTER_X, self.CENTER_Y, current_radius + 15, filled=True) # Even larger core
            for p in self.nebula_particles:
                # Draw particles only if they are relatively young to simulate fading
                if p[2] / p[3] < 0.7: 
                     Render.turn_on_pixel(int(p[0]), int(p[1]))
            Render.draw_text("Nebula of Creation", self.CENTER_X - 60, self.CENTER_Y + 60)

        elif self.stage == 4: # Star Stage: Bright central star with radiating, pulsating flares
            star_core_radius = current_radius + 20 # Largest core
            Render.draw_circle(self.CENTER_X, self.CENTER_Y, star_core_radius, filled=True)
            num_flares = 8
            for i in range(num_flares):
                # Flares rotate and pulse in length
                angle = (2 * math.pi / num_flares) * i + self.star_flare_timer * 0.2
                flare_length = 50 + math.sin(self.star_flare_timer + i) * 15 # Pulsating length
                x1 = self.CENTER_X + int(star_core_radius * math.cos(angle))
                y1 = self.CENTER_Y + int(star_core_radius * math.sin(angle))
                x2 = self.CENTER_X + int((star_core_radius + flare_length) * math.cos(angle))
                y2 = self.CENTER_Y + int((star_core_radius + flare_length) * math.sin(angle))
                Render.draw_line(x1, y1, x2, y2) # Draw each flare
            Render.draw_text("Star of Infinite", self.CENTER_X - 60, self.CENTER_Y + 70)

        # Draw UI elements: Cosmic Dust total and Dust per Second rate
        Render.draw_text(f"Cosmic Dust: {int(self.money)}", 10, 10)
        Render.draw_text(f"Dust/Sec: {self.dust_per_second:.1f}", 10, 30)

        # Display upgrade information for the next available stage
        if self.stage < len(self.upgrade_info):
            next_cost, next_dps = self.upgrade_info[self.stage]
            upgrade_key = str(self.stage + 1)
            Render.draw_text(f"Upgrade to Stage {self.stage + 1} ('{upgrade_key}'): {int(next_cost)} Dust", 10, self.SCREEN_HEIGHT - 30)
            Render.draw_text(f"  -> {next_dps:.1f} Dust/Sec", 10, self.SCREEN_HEIGHT - 15)
        else:
            Render.draw_text("All stages manifested!", 10, self.SCREEN_HEIGHT - 30) # Message for final stage

    def get_instructions(self) -> str:
        instructions = "Press 'space' to Focus Energy (gain 10 dust).\n"
        if self.stage == 0:
            instructions += "Press '1' to Manifest Sprout."
        elif self.stage == 1:
            instructions += "Press '2' to Manifest Crystal."
        elif self.stage == 2:
            instructions += "Press '3' to Manifest Nebula."
        elif self.stage == 3:
            instructions += "Press '4' to Manifest Star."
        else:
            instructions += "The dream concludes." # Thematic message for reaching the end
        return instructions

    def get_next_idea(self) -> list[str]:
        # Zany, short follow-up ideas for further iteration
        return ["Cosmic Echoes", "Galactic Expansion"]
