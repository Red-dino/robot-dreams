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

        # Define all 9 distinct upgrades. Each can be bought multiple times.
        # Format: {'key': 'str', 'name': 'str', 'base_cost': float, 'cost_multiplier': float, 'dps_increase': float, 'level': int}
        self.upgrades = [
            {'key': '1', 'name': 'Cosmic Whisper', 'base_cost': 50.0, 'cost_multiplier': 1.15, 'dps_increase': 2.0, 'level': 0},
            {'key': '2', 'name': 'Stardust Filter', 'base_cost': 150.0, 'cost_multiplier': 1.16, 'dps_increase': 5.0, 'level': 0},
            {'key': '3', 'name': 'Gravity Well', 'base_cost': 400.0, 'cost_multiplier': 1.17, 'dps_increase': 15.0, 'level': 0},
            {'key': '4', 'name': 'Nebula Weave', 'base_cost': 1000.0, 'cost_multiplier': 1.18, 'dps_increase': 40.0, 'level': 0},
            {'key': '5', 'name': 'Singularity Coil', 'base_cost': 2500.0, 'cost_multiplier': 1.19, 'dps_increase': 100.0, 'level': 0},
            {'key': '6', 'name': 'Astral Resonator', 'base_cost': 6000.0, 'cost_multiplier': 1.20, 'dps_increase': 250.0, 'level': 0},
            {'key': '7', 'name': 'Quasar Lens', 'base_cost': 15000.0, 'cost_multiplier': 1.21, 'dps_increase': 600.0, 'level': 0},
            {'key': '8', 'name': 'Galactic Engine', 'base_cost': 40000.0, 'cost_multiplier': 1.22, 'dps_increase': 1500.0, 'level': 0},
            {'key': '9', 'name': 'Universal Conduit', 'base_cost': 100000.0, 'cost_multiplier': 1.23, 'dps_increase': 4000.0, 'level': 0},
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
            (50000, "Multiverse Shaper"), # New higher stage
            (200000, "Transcendent Entity"), # Even higher stage
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
        # Stores [x, y, life_elapsed, max_life, initial_angle, speed_mult] for Nebula (stage 3 and higher)
        self.nebula_particles = []
        self.star_flare_timer = 0.0
        self.galaxy_swirl_angle = 0.0 # For the Galaxy stage
        # For Cosmic Being stage: [start_x, start_y, end_x, end_y, life_elapsed, max_life, initial_angle]
        self.cosmic_being_energy_lines = [] 
        # For Multiverse Shaper stage: [x, y, radius, life_elapsed, max_life, growth_rate]
        self.shaper_orbs = []
        # For Transcendent Entity stage: [x, y, size, life_elapsed, max_life, angle]
        self.transcendent_fragments = []

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
            current_cost = upgrade_data['base_cost'] * (upgrade_data['cost_multiplier'] ** upgrade_data['level'])
            if Input.is_key_pressed(upgrade_data['key']):
                if self.money >= current_cost:
                    self.money -= current_cost
                    self.dust_per_second += upgrade_data['dps_increase']
                    upgrade_data['level'] += 1
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
            # Generate new particles periodically, frequency increases with stage
            particle_gen_chance = 0.2 + (self.stage - 3) * 0.05
            if random.random() < particle_gen_chance:
                angle = random.uniform(0, 2 * math.pi)
                speed_mult = 1.0 + (self.stage - 3) * 0.2 # Particles move faster in later stages
                # Particle data: [x, y, current_life, max_life, initial_spawn_angle, speed_multiplier]
                self.nebula_particles.append([self.CENTER_X, self.CENTER_Y, 0.0, random.uniform(0.5, 1.5), angle, speed_mult])
            
            # Update existing particles and filter out expired ones
            new_particles = []
            for p in self.nebula_particles:
                p[2] += delta # Increment particle's life elapsed
                if p[2] < p[3]: # If particle is still alive
                    # Calculate new position: move outward and swirl
                    progress = p[2] / p[3] # How far along in its life
                    dist_from_center = 10 + progress * 40 * p[5] # Expand outwards, speed depends on multiplier
                    swirl_angle_offset = p[4] + progress * 2 * math.pi * p[5] # Swirl in a circle as it expands
                    p[0] = self.CENTER_X + int(dist_from_center * math.cos(swirl_angle_offset))
                    p[1] = self.CENTER_Y + int(dist_from_center * math.sin(swirl_angle_offset))
                    new_particles.append(p)
            self.nebula_particles = new_particles # Update list with active particles

        if self.stage >= 6: # Cosmic Being Stage (or higher): Energy lines
            # Generate new energy lines periodically
            line_gen_chance = 0.3 + (self.stage - 6) * 0.05
            if random.random() < line_gen_chance:
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

        if self.stage >= 7: # Multiverse Shaper Stage (or higher): Growing Orbs
            # Generate new orbs
            orb_gen_chance = 0.1 + (self.stage - 7) * 0.02
            if random.random() < orb_gen_chance:
                # [x, y, radius, life_elapsed, max_life, growth_rate]
                spawn_radius = random.uniform(20, 80)
                spawn_angle = random.uniform(0, 2 * math.pi)
                spawn_x = self.CENTER_X + int(spawn_radius * math.cos(spawn_angle))
                spawn_y = self.CENTER_Y + int(spawn_radius * math.sin(spawn_angle))
                self.shaper_orbs.append([spawn_x, spawn_y, 1, 0.0, random.uniform(1.0, 2.5), random.uniform(5, 15)])
            
            new_orbs = []
            for orb in self.shaper_orbs:
                orb[3] += delta
                if orb[3] < orb[4]:
                    orb[2] = int(1 + orb[3] * orb[5]) # Radius grows over time
                    new_orbs.append(orb)
            self.shaper_orbs = new_orbs

        if self.stage == 8: # Transcendent Entity Stage: Pulsating Fragments
            # Generate new fragments
            fragment_gen_chance = 0.2
            if random.random() < fragment_gen_chance:
                spawn_angle = random.uniform(0, 2 * math.pi)
                spawn_x = self.CENTER_X + int(math.cos(spawn_angle) * random.uniform(10, 30))
                spawn_y = self.CENTER_Y + int(math.sin(spawn_angle) * random.uniform(10, 30))
                # [x, y, size, life_elapsed, max_life, angle]
                self.transcendent_fragments.append([spawn_x, spawn_y, 1, 0.0, random.uniform(0.8, 1.8), spawn_angle])
            
            new_fragments = []
            for frag in self.transcendent_fragments:
                frag[3] += delta
                if frag[3] < frag[4]:
                    progress = frag[3] / frag[4]
                    frag[2] = int(3 + math.sin(progress * math.pi) * 5) # Grow then shrink
                    
                    # Fragments slowly drift outwards
                    drift_distance = 1 + progress * 20
                    frag[0] = self.CENTER_X + int(math.cos(frag[5]) * drift_distance)
                    frag[1] = self.CENTER_Y + int(math.sin(frag[5]) * drift_distance)
                    new_fragments.append(frag)
            self.transcendent_fragments = new_fragments


        # Play a subtle, continuous background tone based on current dust generation rate
        if self.dust_per_second > 0 and (self.global_time - self.last_passive_sound_time) >= self.passive_sound_interval:
            base_freq = 100
            max_freq = 2000 # Increased max freq for more dramatic sound scaling
            # Using a higher value for the log denominator to account for potentially much higher DPS now
            # Take max DPS from last upgrade and highest stage threshold
            max_possible_dps_from_upgrades = sum([upg['dps_increase'] * 100 for upg in self.upgrades]) # Assume max 100 levels for each
            max_target_dps = max(self.dps_stage_thresholds[-1][0] * 2, max_possible_dps_from_upgrades)
            
            scaled_freq = base_freq + (math.log10(self.dust_per_second + 1) / math.log10(max_target_dps + 1)) * (max_freq - base_freq)
            scaled_freq = min(max(base_freq, scaled_freq), max_freq) # Clamp frequency within reasonable range
            Sound.play_tone(int(scaled_freq), 0.01) # Very short, subtle tone
            self.last_passive_sound_time = self.global_time

    def draw(self):
        # Base radius for the central entity, modulated by pulsation
        radius_base = 20
        pulsation_scale = 1 + math.sin(self.pulsation_timer) * 0.1 # Pulsates from 0.9 to 1.1 of base size
        current_radius = int(radius_base * pulsation_scale)

        # Get current stage name
        current_stage_name = self.dps_stage_thresholds[self.stage][1]

        # All stages will have a central core, its size growing with stages
        core_radius = current_radius + self.stage * 5
        Render.draw_circle(self.CENTER_X, self.CENTER_Y, core_radius, filled=True)
        
        # Stage-specific visual elements - higher stages build upon lower ones
        
        # General visual pulsation for all stages
        Render.draw_circle(self.CENTER_X, self.CENTER_Y, current_radius, filled=False) # Pulsating outer ring

        if self.stage >= 1: # Sprout Stage (and higher)
            num_roots = 6
            for i in range(num_roots):
                angle = (2 * math.pi / num_roots) * i + math.sin(self.pulsation_timer * 0.2 + i) * 0.2
                x1 = self.CENTER_X + int(core_radius * math.cos(angle))
                y1 = self.CENTER_Y + int(core_radius * math.sin(angle))
                x2 = self.CENTER_X + int((core_radius + 20 + self.stage * 2) * math.cos(angle)) # Grow roots with stage
                y2 = self.CENTER_Y + int((core_radius + 20 + self.stage * 2) * math.sin(angle))
                Render.draw_line(x1, y1, x2, y2)

        if self.stage >= 2: # Crystal Stage (and higher)
            num_facets = 6 + self.stage # More facets in later stages
            facet_outer_radius = core_radius + 10 + self.stage * 3
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

        if self.stage >= 3: # Nebula Stage (and higher)
            for p in self.nebula_particles:
                if p[2] / p[3] < 0.7: 
                     Render.turn_on_pixel(int(p[0]), int(p[1]))

        if self.stage >= 4: # Star Stage (and higher)
            num_flares = 8 + self.stage * 2
            for i in range(num_flares):
                angle = (2 * math.pi / num_flares) * i + self.star_flare_timer * 0.2
                flare_length = 30 + math.sin(self.star_flare_timer + i) * 10 # Pulsating length
                x1 = self.CENTER_X + int(core_radius * math.cos(angle))
                y1 = self.CENTER_Y + int(core_radius * math.sin(angle))
                x2 = self.CENTER_X + int((core_radius + flare_length + self.stage * 5) * math.cos(angle)) # Flares grow
                y2 = self.CENTER_Y + int((core_radius + flare_length + self.stage * 5) * math.sin(angle))
                Render.draw_line(x1, y1, x2, y2)

        if self.stage >= 5: # Galaxy Stage (and higher)
            num_arms = 3 + self.stage // 2 # More arms for later stages
            arm_points = 50
            for arm_idx in range(num_arms):
                for i in range(arm_points):
                    theta = (i / arm_points) * (4 * math.pi) # 4 full turns
                    base_angle = (2 * math.pi / num_arms) * arm_idx + self.galaxy_swirl_angle
                    radius_offset = (math.sin(theta * 5 + self.pulsation_timer * 0.5) * 5)
                    r = (i / arm_points) * (core_radius + 40 + self.stage * 7) + radius_offset
                    x = self.CENTER_X + int(r * math.cos(theta + base_angle))
                    y = self.CENTER_Y + int(r * math.sin(theta + base_angle))
                    Render.turn_on_pixel(x, y)

        if self.stage >= 6: # Cosmic Being Stage (and higher)
            for line in self.cosmic_being_energy_lines:
                if line[4] < line[5]:
                    Render.draw_line(int(line[0]), int(line[1]), int(line[2]), int(line[3]))

        if self.stage >= 7: # Multiverse Shaper Stage (and higher)
            for orb in self.shaper_orbs:
                if orb[3] < orb[4]:
                    Render.draw_circle(int(orb[0]), int(orb[1]), orb[2], filled=False)
        
        if self.stage == 8: # Transcendent Entity Stage
            for frag in self.transcendent_fragments:
                if frag[3] < frag[4]:
                    Render.draw_circle(int(frag[0]), int(frag[1]), frag[2], filled=True) # Filled fragments

        # Draw the stage name in the right half of the screen
        # Approx width of text is len * 8 (since font is 16px high, roughly 8px wide per char)
        text_approx_width = len(current_stage_name) * 8 
        # Calculate x to center in the right half of the screen
        text_x = self.CENTER_X + (self.SCREEN_WIDTH - self.CENTER_X) // 2 - text_approx_width // 2
        text_y = self.CENTER_Y + core_radius + 10
        Render.draw_text(current_stage_name, text_x, text_y)


        # Draw UI elements: Cosmic Dust total and Dust per Second rate
        Render.draw_text(f"Cosmic Dust: {int(self.money)}", 10, 10)
        Render.draw_text(f"Dust/Sec: {self.dust_per_second:.1f}", 10, 30)

        # Display upgrade information
        Render.draw_text("Upgrades:", 10, self.SCREEN_HEIGHT - 170) # Adjusted starting Y for more upgrades
        y_offset = self.SCREEN_HEIGHT - 155
        for upgrade_data in self.upgrades:
            current_cost = upgrade_data['base_cost'] * (upgrade_data['cost_multiplier'] ** upgrade_data['level'])
            # Mark upgrades that can be afforded with an asterisk
            can_afford_indicator = "(*)" if self.money >= current_cost else ""
            Render.draw_text(f"'{upgrade_data['key']}': {upgrade_data['name']} (Lv {upgrade_data['level']}) - Cost: {int(current_cost)} {can_afford_indicator}", 10, y_offset)
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
        return ["Reality Bending", "Ethereal Forms"]
