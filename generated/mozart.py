import math
import random
from generated.helpers import Render, Input, Sound

import random
import math

class Program:
    def __init__(self):
        self.motifs = []
        self.spawn_timer = 0.0
        self.progression_timer = 0.0
        self.stage = 0

        # Stage parameters define the composition's unfolding
        self.stage_data = [
            {'spawn_interval': 2.0, 'motif_types': ['pulsar'], 'progression_threshold': 25.0, 'bpm': 60},
            {'spawn_interval': 1.5, 'motif_types': ['pulsar', 'arpeggio'], 'progression_threshold': 50.0, 'bpm': 80},
            {'spawn_interval': 1.0, 'motif_types': ['pulsar', 'arpeggio', 'chord'], 'progression_threshold': 80.0, 'bpm': 100},
            {'spawn_interval': 0.7, 'motif_types': ['pulsar', 'arpeggio', 'chord', 'cadenza'], 'progression_threshold': 120.0, 'bpm': 120},
            {'spawn_interval': 0.5, 'motif_types': ['pulsar', 'arpeggio', 'chord', 'cadenza', 'counterpoint'], 'progression_threshold': float('inf'), 'bpm': 140} # Final stage
        ]

        self.current_spawn_interval = self.stage_data[0]['spawn_interval']
        self.available_motif_types = self.stage_data[0]['motif_types']
        self.current_bpm = self.stage_data[0]['bpm']

        self.last_space_press = False # Tracks 'space' key state for rising edge detection

        # Dream narrative messages
        self.dream_messages = [
            "A single, steady pulse begins...",
            "Melodies weave from the silence...",
            "Harmony lends its resonant voice...",
            "Cadenzas blossom, full of fleeting grace...",
            "A symphony of forms, a maestro's dream..."
        ]
        self.current_message = self.dream_messages[0]
        self.message_display_timer = 0.0
        self.message_duration = 4.0 # How long messages stay on screen

        self.beat_timer = 0.0
        self.beat_interval = 60.0 / self.current_bpm # Seconds per beat

    def update(self, delta: float):
        self.spawn_timer += delta
        self.progression_timer += delta
        self.message_display_timer += delta
        self.beat_timer += delta

        # Handle automatic progression if threshold is met
        if self.stage < len(self.stage_data) - 1 and self.progression_timer >= self.stage_data[self.stage]['progression_threshold']:
            self.advance_stage()

        # Handle user-initiated progression by pressing SPACE
        if Input.is_key_pressed('space'):
            if not self.last_space_press: # Only trigger on the initial press
                if self.stage < len(self.stage_data) - 1:
                    self.advance_stage()
        self.last_space_press = Input.is_key_pressed('space')

        # Spawn new motifs based on interval
        if self.spawn_timer >= self.current_spawn_interval:
            self.spawn_motif()
            self.spawn_timer = 0.0

        # Trigger a 'beat' visual or sound effect periodically
        if self.beat_timer >= self.beat_interval:
            # Sound.play_tone(150, 0.05) # Subtle baseline beat
            self.beat_timer = 0.0

        # Update and filter existing motifs
        new_motifs = []
        for motif in self.motifs:
            motif.update(delta)
            if motif.is_alive():
                new_motifs.append(motif)
        self.motifs = new_motifs

    def advance_stage(self):
        self.stage += 1
        if self.stage < len(self.stage_data):
            self.current_spawn_interval = self.stage_data[self.stage]['spawn_interval']
            self.available_motif_types = self.stage_data[self.stage]['motif_types']
            self.current_bpm = self.stage_data[self.stage]['bpm']
            self.beat_interval = 60.0 / self.current_bpm
            self.current_message = self.dream_messages[self.stage]
            self.message_display_timer = 0.0 # Reset message timer for new message
            Sound.play_tone(440 + self.stage * 80, 0.15) # Stage transition tone

    def spawn_motif(self):
        # Center region for spawning, but with some randomness
        cx, cy = 200, 150
        x = cx + random.randint(-80, 80)
        y = cy + random.randint(-60, 60)
        
        motif_type = random.choice(self.available_motif_types)

        if motif_type == 'pulsar':
            age = random.uniform(1.0, 2.0)
            radius = random.uniform(10, 30)
            Sound.play_tone(random.choice([261, 329, 392]), 0.1) # C, E, G
            self.motifs.append(PulsarMotif(x, y, age, radius))
        elif motif_type == 'arpeggio':
            age = random.uniform(1.5, 3.0)
            num_points = random.randint(3, 5)
            length = random.uniform(40, 70)
            # Arpeggio tones
            Sound.play_tone(random.choice([392, 440, 493]), 0.08) # G, A, B
            self.motifs.append(ArpeggioMotif(x, y, age, num_points, length))
        elif motif_type == 'chord':
            age = random.uniform(1.2, 2.5)
            # Chord tones
            freq1 = random.choice([261, 293, 329, 349, 392]) # C, D, E, F, G
            freq2 = freq1 * 1.25 # approx major third
            freq3 = freq1 * 1.5 # approx perfect fifth
            Sound.play_tone(freq1, 0.15)
            Sound.play_tone(freq2, 0.15)
            Sound.play_tone(freq3, 0.15)
            self.motifs.append(ChordMotif(x, y, age, random.uniform(20, 40)))
        elif motif_type == 'cadenza':
            age = random.uniform(0.8, 1.8)
            num_flourishes = random.randint(8, 15)
            # Rapid high tones for cadenza
            for _ in range(3): Sound.play_tone(random.uniform(500, 800), 0.05)
            self.motifs.append(CadenzaMotif(x, y, age, num_flourishes))
        elif motif_type == 'counterpoint':
            age = random.uniform(2.0, 4.0)
            offset_x = random.uniform(-30, 30)
            offset_y = random.uniform(-30, 30)
            # Two distinct melodic lines (octave apart)
            Sound.play_tone(random.choice([261, 329, 392]), 0.1)
            Sound.play_tone(random.choice([523, 659, 784]), 0.1)
            self.motifs.append(CounterpointMotif(x + offset_x, y + offset_y, age, random.uniform(50, 80)))


    def draw(self):
        # Draw all active motifs
        for motif in self.motifs:
            motif.draw()
        
        # Display the current dream message
        if self.message_display_timer < self.message_duration:
            text_width = len(self.current_message) * 8
            Render.draw_text(self.current_message, int(400 / 2 - text_width / 2), 299 - 30)

    def get_instructions(self) -> str:
        return "Press SPACE to advance the composition."

    def get_next_idea(self) -> list[str]:
        return ["Rhythmic Complexity", "Interacting Agents", "Color Harmonies"]

# Base class for all musical motifs
class MusicalMotif:
    def __init__(self, x, y, max_age):
        self.x = x
        self.y = y
        self.max_age = max_age
        self.age = 0.0

    def update(self, delta):
        self.age += delta

    def is_alive(self):
        return self.age < self.max_age

    def draw(self):
        pass

# PulsarMotif: A rhythmic beat, expanding and contracting circle
class PulsarMotif(MusicalMotif):
    def __init__(self, x, y, max_age, max_radius):
        super().__init__(x, y, max_age)
        self.max_radius = max_radius

    def draw(self):
        progress = self.age / self.max_age
        current_radius = self.max_radius * (1 - abs(2 * progress - 1)) # Triangle wave for smooth pulsing
        if current_radius > 0.5:
            Render.draw_circle(int(self.x), int(self.y), int(current_radius), filled=False)

# ArpeggioMotif: A melodic line, a path of fading points
class ArpeggioMotif(MusicalMotif):
    def __init__(self, x, y, max_age, num_points, length):
        super().__init__(x, y, max_age)
        self.num_points = num_points
        self.length = length
        self.angle_offset = random.uniform(0, 2 * math.pi)

    def draw(self):
        progress = self.age / self.max_age
        fade_factor = 1.0 - progress

        if fade_factor > 0:
            for i in range(self.num_points):
                point_progress = (progress * self.num_points + i) % self.num_points / self.num_points
                if point_progress > progress: continue # Only draw points that have "appeared"

                # Path for the arpeggio (a gentle curve)
                px = self.x + self.length * math.cos(self.angle_offset + point_progress * math.pi * 2) * (1 - point_progress)
                py = self.y + self.length * math.sin(self.angle_offset + point_progress * math.pi * 2) * (1 - point_progress)

                # Each point fades after appearing
                point_fade = max(0, 1 - (progress * self.num_points - i) / 2.0)
                if point_fade > 0.1:
                    Render.draw_circle(int(px), int(py), int(2 * point_fade), filled=True)

# ChordMotif: Multiple shapes appearing synchronously, then fading
class ChordMotif(MusicalMotif):
    def __init__(self, x, y, max_age, radius):
        super().__init__(x, y, max_age)
        self.radius = radius
        self.num_shapes = random.randint(3, 5) # Represent notes in a chord
        self.shape_type = random.choice(['rect', 'circle', 'line'])

    def draw(self):
        progress = self.age / self.max_age
        scale_factor = math.sin(math.pi * progress) # Grows then shrinks

        if scale_factor > 0.1:
            for i in range(self.num_shapes):
                angle = (i / self.num_shapes) * 2 * math.pi + self.age * 0.5
                sx = self.x + self.radius * 0.7 * math.cos(angle) * scale_factor
                sy = self.y + self.radius * 0.7 * math.sin(angle) * scale_factor

                size = max(1, int(5 * scale_factor)) # Size scales with overall progress

                if self.shape_type == 'rect':
                    Render.draw_rect(int(sx - size / 2), int(sy - size / 2), size, size, filled=True)
                elif self.shape_type == 'circle':
                    Render.draw_circle(int(sx), int(sy), size, filled=True)
                elif self.shape_type == 'line':
                    Render.draw_line(int(sx - size), int(sy), int(sx + size), int(sy))

# CadenzaMotif: A rapid flourish of lines or dots
class CadenzaMotif(MusicalMotif):
    def __init__(self, x, y, max_age, num_flourishes):
        super().__init__(x, y, max_age)
        self.num_flourishes = num_flourishes
        self.base_angle = random.uniform(0, 2 * math.pi)

    def draw(self):
        progress = self.age / self.max_age
        scale_factor = math.sin(math.pi * progress) # Peaks in the middle, fades out
        
        if scale_factor > 0.1:
            for i in range(self.num_flourishes):
                # Spiraling outward effect
                angle = self.base_angle + (i / self.num_flourishes) * math.pi * 6 * progress
                length = (i / self.num_flourishes) * 50 * scale_factor
                
                fx = self.x + length * math.cos(angle)
                fy = self.y + length * math.sin(angle)
                
                # Draw small circles or lines
                Render.draw_circle(int(fx), int(fy), 1, filled=True)

# CounterpointMotif: Two intertwining melodic lines (similar to arpeggio but interacting)
class CounterpointMotif(MusicalMotif):
    def __init__(self, x, y, max_age, max_separation):
        super().__init__(x, y, max_age)
        self.max_separation = max_separation
        self.base_angle = random.uniform(0, 2 * math.pi)
        self.amplitude = random.uniform(10, 25) # For wavy motion
        self.frequency = random.uniform(3, 7) # For wavy motion

    def draw(self):
        progress = self.age / self.max_age
        alpha_fade = 1.0 - progress

        if alpha_fade > 0.05:
            # First line
            prev_x1, prev_y1 = None, None
            # Second line
            prev_x2, prev_y2 = None, None

            num_segments = 20 # For smooth lines
            for i in range(num_segments + 1):
                segment_progress = i / num_segments

                # Position along the main 'path' of the motif
                path_x = self.x + self.max_separation * (segment_progress - 0.5) * math.cos(self.base_angle)
                path_y = self.y + self.max_separation * (segment_progress - 0.5) * math.sin(self.base_angle)

                # Wavy offset for each line, creating counterpoint
                wave_offset1 = self.amplitude * math.sin(segment_progress * self.frequency * math.pi + progress * math.pi * 2)
                wave_offset2 = self.amplitude * math.cos(segment_progress * self.frequency * math.pi + progress * math.pi * 2 + math.pi / 2) # Phase shifted

                # Perpendicular direction for the wave
                perp_angle = self.base_angle + math.pi / 2
                
                curr_x1 = path_x + wave_offset1 * math.cos(perp_angle)
                curr_y1 = path_y + wave_offset1 * math.sin(perp_angle)

                curr_x2 = path_x + wave_offset2 * math.cos(perp_angle)
                curr_y2 = path_y + wave_offset2 * math.sin(perp_angle)

                if prev_x1 is not None:
                    Render.draw_line(int(prev_x1), int(prev_y1), int(curr_x1), int(curr_y1))
                    Render.draw_line(int(prev_x2), int(prev_y2), int(curr_x2), int(curr_y2))
                
                prev_x1, prev_y1 = curr_x1, curr_y1
                prev_x2, prev_y2 = curr_x2, curr_y2