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
        self.stage = 0  # 0: Seed, 1: Sprout, 2: Crystal, etc. Derived from DPS.

        # Define all 9 distinct upgrades. Each can be bought once.
        # Format: {'key': 'str', 'name': 'str', 'cost': float, 'dps_increase': float, 'bought': bool}
        self.upgrades = [
            {'key': '1', 'name': 'Cosmic Whisper', 'cost': 50.0, 'dps_increase': 2.0, 'bought': False},
            {'key': '2', 'name': 'Stardust Filter', 'cost': 150.0, 'dps_increase': 5.0, 'bought': False},
            {'key': '3', 'name': 'Gravity Well', 'cost': 400.0, 'dps_increase': 15.0, 'bought': False},
            {'key': '4', 'name': 'Nebula Weave', 'cost': 1000.0, 'dps_increase': 40.0, 'bought': False},
            {'key': '5', 'name': 'Singularity Coil', 'cost': 2500.0, 'dps_increase': 100.0, 'bought': False},
            {'key': '6', 'name': 'Astral Resonator', 'cost': 6000.0, 'dps_increase': 250.0, 'bought': False},
            {'key': '7', 'name': 'Quasar Lens', 'cost': 15000.0, 'dps_increase': 600.0, 'bought': False},
            {'key': '8', 'name': 'Galactic Engine', 'cost': 40000.0, 'dps_increase': 1500.0, 'bought': False},
            {'key': '9', 'name': 'Universal Conduit', 'cost': 100000.0, 'dps_increase': 4000.0, 'bought': False},
        ]

        # Define thresholds for visual stages based on total dust_per_second
        # Format: (DPS_threshold, "Stage Name")
        self.dps_stage_thresholds = [
            (0, "Seed of Existence"),
            (10, "Sprout of Potential"),
            (50, "Crystal of Insight"),
            (200, "Nebula of Creation"),
            (1000, "Star of Infinite"),
            (5000, "Galaxy of Dreams"),
            (15000, "Cosmic Being"),
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
        # Stores [x, y, life_elapsed, max_life, initial_angle] for Nebula (stage 3 and higher)
        self.nebula_particles = []
        self.star_flare_timer = 0.0
        self.galaxy_swirl_angle = 0.0 # For the Galaxy stage
        # For Cosmic Being stage: [start_x, start_y, end_x, end_y, life_elapsed, max_life, initial_angle]
        self.cosmic_being_energy_lines = [] 

    def update(self, delta: float):
        self.global_time += delta
        self.money += self.dust_per_second * delta
        self.pulsation_timer += delta * 5 # Controls speed of general pulsing animation
        self.focus_cooldown_timer = max(0.0, self.focus_cooldown_timer - delta)
        self.crystal_rotation += delta * 0.5 # Controls rotation speed for Crystal Stage
        self.star_flare_timer += delta * 2 # Controls animation speed for Star Stage flares
        self.galaxy_swirl_angle += delta * 0.1 # Controls galaxy swirl speed

        # Handle user input: 'space' key to "Focus Energy" for a dust burst
        if Input.is_key_pressed('space') and self.focus_cooldown_timer == 0.0:
            self.money += 10.0 # Grant 10 dust
            self.focus_cooldown_timer = self.focus_cooldown_duration # Reset cooldown
            Sound.play_tone(440, 0.05) # Play a short, distinct tone for interaction

        # Handle upgrade key presses (keys '1' through '9')
        for upgrade_data in self.upgrades:
            if not upgrade_data['bought'] and Input.is_key_pressed(upgrade_data['key']):
                if self.money >= upgrade_data['cost']:
                    self.money -= upgrade_data['cost']
                    self.dust_per_second += upgrade_data['dps_increase']
                    upgrade_data['bought'] = True
                    Sound.play_tone(880, 0.1) # Play a higher-pitched tone for successful upgrade
                    # No break here, as multiple upgrades could potentially be bought in a single frame
                    # if they are very cheap and the user holds down multiple keys, though unlikely with key_pressed.

        # Determine current visual stage based on dust_per_second
        new_stage = 0
        for i, (threshold, _) in enumerate(self.dps_stage_thresholds):
            if self.dust_per_second >= threshold:
                new_stage = i
            else:
                break
        self.stage = new_stage

        # Stage-specific update logic for animations and effects
        if self.stage >= 3: # Nebula Stage (or higher): manage swirling particles
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

        if self.stage == 6: # Cosmic Being Stage: Energy lines
            # Generate new energy lines periodically
            if random.random() < 0.3: # Higher chance to make it feel more active
                start_angle = random.uniform(0, 2 * math.pi)
                # [start_x, start_y, end_x, end_y, life_elapsed, max_life, initial_angle]
                self.cosmic_being_energy_lines.append([self.CENTER_X, self.CENTER_Y, self.CENTER_X, self.CENTER_Y, 0.0, random.uniform(0.3, 0.8), start_angle])
            
            new_energy_lines = []
            for line in self.cosmic_being_energy_lines:
                line[4] += delta
                if line[4] < line[5]:
                    progress = line[4] / line[5]
                    # Lines expand from the center outwards
                    current_length = 20 + progress * 60 # Grow from 20 to 80 pixels
                    
                    # Make them slightly wavy or curved over time
                    wavy_offset_angle = line[6] + math.sin(line[4] * 10) * 0.2
                    x_wavy_offset = int(current_length * math.cos(wavy_offset_angle))
                    y_wavy_offset = int(current_length * math.sin(wavy_offset_angle))

                    line[2] = self.CENTER_X + x_wavy_offset
                    line[3] = self.CENTER_Y + y_wavy_offset
                    new_energy_lines.append(line)
            self.cosmic_being_energy_lines = new_energy_lines

        # Play a subtle, continuous background tone based on current dust generation rate
        if self.dust_per_second > 0 and (self.global_time - self.last_passive_sound_time) >= self.passive_sound_interval:
            base_freq = 100
            max_freq = 1500 # Increased max freq for more dramatic sound scaling
            # Scale frequency logarithmically to make progression feel smoother, especially at higher rates
            # Using a higher value for the log denominator to account for potentially much higher DPS now
            scaled_freq = base_freq + (math.log10(self.dust_per_second + 1) / math.log10(self.dps_stage_thresholds[-1][0] * 2 + 1)) * (max_freq - base_freq)
            scaled_freq = min(max(base_freq, scaled_freq), max_freq) # Clamp frequency within reasonable range
            Sound.play_tone(int(scaled_freq), 0.01) # Very short, subtle tone
            self.last_passive_sound_time = self.global_time

    def draw(self):
        # Base radius for the central entity, modulated by pulsation
        radius_base = 20
        pulsation_scale = 1 + math.sin(self.pulsation_timer) * 0.1 # Pulsates from 0.9 to 1.1 of base size
        current_radius = int(radius_base * pulsation_scale)

        # Draw the "Seed of Existence" based on its current stage
        current_stage_name = self.dps_stage_thresholds[self.stage][1]

        # All stages will have a central core, its size growing with stages
        core_radius = current_radius
        if self.stage >= 1: core_radius += 5
        if self.stage >= 2: core_radius += 5
        if self.stage >= 3: core_radius += 5
        if self.stage >= 4: core_radius += 5
        if self.stage >= 5: core_radius += 5
        if self.stage >= 6: core_radius += 5

        Render.draw_circle(self.CENTER_X, self.CENTER_Y, core_radius, filled=True)
        
        # Stage-specific visual elements
        if self.stage == 0: # Seed Stage
            pass # Already drew the core

        elif self.stage == 1: # Sprout Stage
            num_roots = 6
            for i in range(num_roots):
                angle = (2 * math.pi / num_roots) * i + math.sin(self.pulsation_timer * 0.2 + i) * 0.2
                x1 = self.CENTER_X + int(core_radius * math.cos(angle))
                y1 = self.CENTER_Y + int(core_radius * math.sin(angle))
                x2 = self.CENTER_X + int((core_radius + 20) * math.cos(angle))
                y2 = self.CENTER_Y + int((core_radius + 20) * math.sin(angle))
                Render.draw_line(x1, y1, x2, y2)

        elif self.stage == 2: # Crystal Stage
            num_facets = 6
            facet_outer_radius = core_radius + 10
            for i in range(num_facets):
                angle_base = (2 * math.pi / num_facets) * i + self.crystal_rotation
                p1x = self.CENTER_X + int(facet_outer_radius * math.cos(angle_base))
                p1y = self.CENTER_Y + int(facet_outer_radius * math.sin(angle_base))
                p2x = self.CENTER_X + int((facet_outer_radius * 0.7) * math.cos(angle_base + 0.5))
                p2y = self.CENTER_Y + int((facet_outer_radius * 0.7) * math.sin(angle_base + 0.5))
                p3x = self.CENTER_X + int((facet_outer_radius * 0.7) * math.cos(angle_base - 0.5))
                p3y = self.CENTER_Y + int((facet_outer_radius * 0.7) * math.sin(angle_base - 0.5))
                Render.draw_line(self.CENTER_X, self.CENTER_Y, p1x, p1y)
                Render.draw_line(p1x, p1y, p2x, p2y)
                Render.draw_line(p1x, p1y, p3x, p3y)
                Render.draw_line(p2x, p2y, p3x, p3y)

        elif self.stage == 3: # Nebula Stage
            # Particles drawn over the core
            for p in self.nebula_particles:
                if p[2] / p[3] < 0.7: 
                     Render.turn_on_pixel(int(p[0]), int(p[1]))

        elif self.stage == 4: # Star Stage
            num_flares = 8
            for i in range(num_flares):
                angle = (2 * math.pi / num_flares) * i + self.star_flare_timer * 0.2
                flare_length = 30 + math.sin(self.star_flare_timer + i) * 10 # Pulsating length
                x1 = self.CENTER_X + int(core_radius * math.cos(angle))
                y1 = self.CENTER_Y + int(core_radius * math.sin(angle))
                x2 = self.CENTER_X + int((core_radius + flare_length) * math.cos(angle))
                y2 = self.CENTER_Y + int((core_radius + flare_length) * math.sin(angle))
                Render.draw_line(x1, y1, x2, y2)

        elif self.stage == 5: # Galaxy Stage - A swirling spiral effect
            num_arms = 3
            arm_points = 50
            for arm_idx in range(num_arms):
                for i in range(arm_points):
                    # Spiral formula: r = a * theta
                    theta = (i / arm_points) * (4 * math.pi) # 4 full turns
                    base_angle = (2 * math.pi / num_arms) * arm_idx + self.galaxy_swirl_angle
                    
                    # Add some randomness or turbulence to the arm for a more "galaxy" feel
                    radius_offset = (math.sin(theta * 5 + self.pulsation_timer * 0.5) * 5)
                    
                    r = (i / arm_points) * (core_radius + 40) + radius_offset
                    x = self.CENTER_X + int(r * math.cos(theta + base_angle))
                    y = self.CENTER_Y + int(r * math.sin(theta + base_angle))
                    Render.turn_on_pixel(x, y)
            
            # Draw nebula particles as well, layered
            for p in self.nebula_particles:
                if p[2] / p[3] < 0.7: 
                     Render.turn_on_pixel(int(p[0]), int(p[1]))

        elif self.stage == 6: # Cosmic Being Stage - The core emits complex energy lines
            for line in self.cosmic_being_energy_lines:
                # Draw lines if they are within their active life
                if line[4] < line[5]:
                    Render.draw_line(int(line[0]), int(line[1]), int(line[2]), int(line[3]))
            
            # Also overlay star flares and nebula particles for a cumulative effect
            num_flares = 10
            for i in range(num_flares):
                angle = (2 * math.pi / num_flares) * i + self.star_flare_timer * 0.3
                flare_length = 40 + math.sin(self.star_flare_timer * 0.8 + i) * 20 
                x1 = self.CENTER_X + int(core_radius * math.cos(angle))
                y1 = self.CENTER_Y + int(core_radius * math.sin(angle))
                x2 = self.CENTER_X + int((core_radius + flare_length) * math.cos(angle))
                y2 = self.CENTER_Y + int((core_radius + flare_length) * math.sin(angle))
                Render.draw_line(x1, y1, x2, y2)
            
            for p in self.nebula_particles:
                if p[2] / p[3] < 0.7: 
                     Render.turn_on_pixel(int(p[0]), int(p[1]))


        Render.draw_text(current_stage_name, self.CENTER_X - len(current_stage_name) * 4, self.CENTER_Y + core_radius + 10) # Centered below the object


        # Draw UI elements: Cosmic Dust total and Dust per Second rate
        Render.draw_text(f"Cosmic Dust: {int(self.money)}", 10, 10)
        Render.draw_text(f"Dust/Sec: {self.dust_per_second:.1f}", 10, 30)

        # Display upgrade information
        Render.draw_text("Upgrades:", 10, self.SCREEN_HEIGHT - 150)
        y_offset = self.SCREEN_HEIGHT - 135
        for upgrade_data in self.upgrades:
            status = "Bought" if upgrade_data['bought'] else f"Cost: {int(upgrade_data['cost'])}"
            # Mark upgrades that can be afforded with an asterisk
            can_afford_indicator = "(*)" if not upgrade_data['bought'] and self.money >= upgrade_data['cost'] else ""
            Render.draw_text(f"'{upgrade_data['key']}': {upgrade_data['name']} ({status}) {can_afford_indicator}", 10, y_offset)
            y_offset += 15
            
        # Display the next stage threshold if not at the final stage
        if self.stage < len(self.dps_stage_thresholds) - 1:
            next_stage_threshold = self.dps_stage_thresholds[self.stage + 1][0]
            next_stage_name = self.dps_stage_thresholds[self.stage + 1][1]
            Render.draw_text(f"Next Stage @ {int(next_stage_threshold)} DPS: {next_stage_name}", 10, y_offset + 15)


    def get_instructions(self) -> str:
        instructions = "Press 'space' to Focus Energy (gain 10 dust).\n"
        instructions += "Press '1'-'9' to purchase upgrades to increase Dust/Sec."
        return instructions

    def get_next_idea(self) -> list[str]:
        # Zany, short follow-up ideas for further iteration
        return ["Celestial Orbs", "Time Warping"]
