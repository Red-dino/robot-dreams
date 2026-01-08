import math
import random
from generated.helpers import Render, Input, Sound


import math
import random

# Constants for the simulation
WIDTH = 400
HEIGHT = 300
CENTER_X = WIDTH // 2
CENTER_Y = HEIGHT // 2

# Chronon properties
CHRONON_MAX_LIFE = 6.0  # seconds
CHRONON_RADIUS = 2
MAX_CHRONONS = 120 # Increased maximum chronons for more density

# Strand properties
STRAND_MAX_STRENGTH = 1.0
STRAND_DECAY_RATE = 0.5 # strength decay per second if chronons are far
STRAND_CONNECT_DIST = 45 # max distance for chronons to form a strand
STRAND_MIN_CONNECT_DIST = 10 # min distance to keep a strong strand

# Physics properties
BASE_ATTRACTION_STRENGTH = 12.0 # Initial attraction force
MAX_ATTRACTION_STRENGTH = 60.0 # Increased max attraction
MIN_ATTRACTION_STRENGTH = 0.5
ATTRACTION_CHANGE_RATE = 7.0 # per second

BASE_ROTATIONAL_FORCE = 0.0 # Initial rotational force
MAX_ROTATIONAL_FORCE = 6.0 # Increased max rotation
MIN_ROTATIONAL_FORCE = -6.0
ROTATIONAL_CHANGE_RATE = 2.5 # per second

VELOCITY_DAMPING = 0.97 # applied each frame
BOUNCE_COEFFICIENT = 0.7 # How much velocity is retained after bouncing off walls

# Stages
STAGE_DRIFTING = 0
STAGE_EMERGING_STRANDS = 1
STAGE_PATTERN_WEAVING = 2
STAGE_RESONANT_TAPESTRY = 3
STAGE_CHRONO_RIPPLE = 4

# Stage timings and thresholds
STAGE_1_DURATION = 10.0 # If user doesn't interact, auto-progress
STAGE_2_COMPLEXITY_THRESHOLD = 70 # Increased complexity needed
STAGE_3_COMPLEXITY_THRESHOLD = 250 # Increased complexity needed
STAGE_4_DURATION_MAX = 18.0 # Max time in resonant stage before ripple

# Sound frequencies for stages
DRIFT_TONE = 200
EMERGE_TONE = 300
WEAVE_TONE = 450
RESONANT_CHORD_BASE = 440 # A4
RESONANT_CHORD = [RESONANT_CHORD_BASE, RESONANT_CHORD_BASE * 1.25, RESONANT_CHORD_BASE * 1.5] # A4, C#5, E5 for A major triad
RIPPLE_GLISSANDO_START = 1000
RIPPLE_GLISSANDO_END = 80

class Chronon:
    _id_counter = 0

    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = CHRONON_MAX_LIFE
        self.id = Chronon._id_counter
        Chronon._id_counter += 1

class Strand:
    def __init__(self, c1_id, c2_id):
        self.c1_id = c1_id
        self.c2_id = c2_id
        self.strength = STRAND_MAX_STRENGTH

class Program:
    def __init__(self):
        self.chronons = []
        self.strands = []
        self.chronon_map = {} # for quick lookup by ID

        self.attraction_strength = BASE_ATTRACTION_STRENGTH
        self.rotational_force = BASE_ROTATIONAL_FORCE

        self.stage = STAGE_DRIFTING
        self.stage_timer = 0.0
        self.complexity_score = 0.0
        self.last_sound_time = 0.0 # For resonant chord pulsing
        self.last_spawn_time = 0.0 # To limit rapid spawns

        self.message = ""

        self._spawn_initial_chronons(5)
        Sound.play_tone(DRIFT_TONE, 0.2)

    def _spawn_initial_chronons(self, count):
        for _ in range(count):
            self._spawn_chronon()

    def _spawn_chronon(self, x=None, y=None, velocity_boost=False):
        if len(self.chronons) >= MAX_CHRONONS:
            return

        if x is None: x = random.uniform(50, WIDTH - 50)
        if y is None: y = random.uniform(50, HEIGHT - 50)
        
        vx = random.uniform(-15, 15)
        vy = random.uniform(-15, 15)

        if velocity_boost:
            vx *= 1.5
            vy *= 1.5

        new_chronon = Chronon(x, y, vx, vy)
        self.chronons.append(new_chronon)
        self.chronon_map[new_chronon.id] = new_chronon
        if self.stage != STAGE_CHRONO_RIPPLE: # Avoid spamming sound during reset
             Sound.play_tone(120 + random.randint(0, 80), 0.03) # Slightly varied tone and shorter duration


    def _update_physics(self, delta):
        # Apply attraction force between chronons
        for i, c1 in enumerate(self.chronons):
            for j, c2 in enumerate(self.chronons):
                if i >= j: continue

                dx = c2.x - c1.x
                dy = c2.y - c1.y
                dist_sq = dx*dx + dy*dy
                dist = math.sqrt(dist_sq)

                if dist < 1.0: dist = 1.0 # Prevent division by zero

                # Simple inverse-square attraction, scaled by strength
                # Increased multiplier for stronger base attraction
                force_magnitude = self.attraction_strength / dist_sq * 15
                fx = force_magnitude * dx / dist
                fy = force_magnitude * dy / dist

                c1.vx += fx * delta
                c1.vy += fy * delta
                c2.vx -= fx * delta
                c2.vy -= fy * delta

            # Apply rotational force around center
            center_dx = c1.x - CENTER_X
            center_dy = c1.y - CENTER_Y
            # Calculate perpendicular vector for rotation
            rot_fx = -center_dy * self.rotational_force
            rot_fy = center_dx * self.rotational_force
            c1.vx += rot_fx * delta
            c1.vy += rot_fy * delta


        # Update chronon positions and apply damping
        for c in self.chronons:
            c.x += c.vx * delta
            c.y += c.vy * delta
            c.vx *= VELOCITY_DAMPING
            c.vy *= VELOCITY_DAMPING

            # Keep chronons within bounds and bounce
            if c.x < 0: c.x = 0; c.vx *= -BOUNCE_COEFFICIENT
            if c.x > WIDTH: c.x = WIDTH; c.vx *= -BOUNCE_COEFFICIENT
            if c.y < 0: c.y = 0; c.vy *= -BOUNCE_COEFFICIENT
            if c.y > HEIGHT: c.y = HEIGHT; c.vy *= -BOUNCE_COEFFICIENT

            c.life -= delta

        # Remove dead chronons
        self.chronons = [c for c in self.chronons if c.life > 0]
        self.chronon_map = {c.id: c for c in self.chronons}

    def _update_strands(self, delta):
        new_strands = []
        active_chronon_pairs = set()

        # Try to form new strands or reinforce existing ones
        for i, c1 in enumerate(self.chronons):
            for j, c2 in enumerate(self.chronons):
                if i >= j: continue

                dx = c2.x - c1.x
                dy = c2.y - c1.y
                dist_sq = dx*dx + dy*dy
                dist = math.sqrt(dist_sq)

                if dist < STRAND_CONNECT_DIST:
                    # Check if this pair already has a strand
                    existing_strand = None
                    for s in self.strands:
                        if (s.c1_id == c1.id and s.c2_id == c2.id) or \
                           (s.c1_id == c2.id and s.c2_id == c1.id):
                            existing_strand = s
                            break

                    if existing_strand:
                        existing_strand.strength = STRAND_MAX_STRENGTH # refresh strength
                        active_chronon_pairs.add(tuple(sorted((c1.id, c2.id))))
                    elif dist < STRAND_MIN_CONNECT_DIST + (STRAND_CONNECT_DIST - STRAND_MIN_CONNECT_DIST) * (self.attraction_strength / MAX_ATTRACTION_STRENGTH): # Only form new strands if fairly close, adjusted by attraction
                        new_strand = Strand(c1.id, c2.id)
                        new_strands.append(new_strand)
                        active_chronon_pairs.add(tuple(sorted((c1.id, c2.id))))

        self.strands.extend(new_strands)

        # Decay and remove old strands
        temp_strands = []
        for s in self.strands:
            pair = tuple(sorted((s.c1_id, s.c2_id)))
            if pair in active_chronon_pairs:
                # If active, strength is maintained or already maxed
                temp_strands.append(s)
            else:
                s.strength -= STRAND_DECAY_RATE * delta
                if s.strength > 0:
                    temp_strands.append(s)
        self.strands = temp_strands

        # Calculate complexity score
        self.complexity_score = len(self.strands) * 1.0 + len(self.chronons) * 0.75 # Adjusted weights


    def _update_stage(self, delta):
        self.stage_timer += delta

        if self.stage == STAGE_DRIFTING:
            self.message = "Stage 1: Whispers of Light"
            # Auto-progress if nothing happens or user spawns some chronons
            if self.stage_timer > STAGE_1_DURATION or len(self.chronons) > 15: # Lowered threshold slightly
                self.stage = STAGE_EMERGING_STRANDS
                self.stage_timer = 0.0
                self.attraction_strength = BASE_ATTRACTION_STRENGTH * 1.8 # Boost attraction more
                Sound.play_tone(EMERGE_TONE, 0.2)

        elif self.stage == STAGE_EMERGING_STRANDS:
            self.message = "Stage 2: Faint Connections"
            # User needs to increase attraction or get chronons to connect
            if self.complexity_score > STAGE_2_COMPLEXITY_THRESHOLD:
                self.stage = STAGE_PATTERN_WEAVING
                self.stage_timer = 0.0
                Sound.play_tone(WEAVE_TONE, 0.2)

        elif self.stage == STAGE_PATTERN_WEAVING:
            self.message = "Stage 3: Pattern Weaving"
            # User needs to create more complex patterns
            if self.complexity_score > STAGE_3_COMPLEXITY_THRESHOLD:
                self.stage = STAGE_RESONANT_TAPESTRY
                self.stage_timer = 0.0
                self.attraction_strength = MAX_ATTRACTION_STRENGTH * 0.8 # make it more stable
                self.rotational_force = MAX_ROTATIONAL_FORCE * 0.6
                Sound.play_tone(RESONANT_CHORD[0], 0.1)
                Sound.play_tone(RESONANT_CHORD[1], 0.1)
                Sound.play_tone(RESONANT_CHORD[2], 0.1)
                self.last_sound_time = self.stage_timer # Initialize for pulsing

        elif self.stage == STAGE_RESONANT_TAPESTRY:
            self.message = "Stage 4: Resonant Tapestry"
            if self.stage_timer > STAGE_4_DURATION_MAX:
                self.stage = STAGE_CHRONO_RIPPLE
                self.stage_timer = 0.0
                self.message = "Chrono-Ripple! Resetting..."
                # Sound.play_tone(RIPPLE_GLISSANDO_START, 0.1) # Starting tone for glissando, handled by ripple stage

            # Play resonant chord pulses periodically
            if self.stage_timer >= self.last_sound_time + 1.2 and self.stage_timer < STAGE_4_DURATION_MAX - 1.0: # Shorter interval, stop before end
                Sound.play_tone(RESONANT_CHORD[0] + random.randint(-15, 15), 0.08) # Slightly varied pitch and duration
                Sound.play_tone(RESONANT_CHORD[1] + random.randint(-15, 15), 0.08)
                Sound.play_tone(RESONANT_CHORD[2] + random.randint(-15, 15), 0.08)
                self.last_sound_time = self.stage_timer


        elif self.stage == STAGE_CHRONO_RIPPLE:
            # Glissando down
            ripple_duration = 2.5 # Total time for the glissando and reset
            
            if self.stage_timer < ripple_duration:
                # Calculate current frequency for glissando
                # Linearly interpolate from start to end frequency over ripple_duration
                current_freq = RIPPLE_GLISSANDO_START + (RIPPLE_GLISSANDO_END - RIPPLE_GLISSANDO_START) * (self.stage_timer / ripple_duration)
                Sound.play_tone(int(current_freq), 0.05) # Play rapidly descending tones

            # Clear everything and restart
            if self.stage_timer > ripple_duration:
                self.chronons = []
                self.strands = []
                self.chronon_map = {}
                self.attraction_strength = BASE_ATTRACTION_STRENGTH + random.uniform(-7, 7) # Slightly different start
                self.rotational_force = BASE_ROTATIONAL_FORCE + random.uniform(-1.5, 1.5)
                self.stage = STAGE_DRIFTING
                self.stage_timer = 0.0
                self.complexity_score = 0.0
                self._spawn_initial_chronons(7 + random.randint(0, 8)) # Spawn more initial chronons
                Sound.play_tone(DRIFT_TONE, 0.2)


    def update(self, delta: float):
        # Handle input
        if Input.is_key_pressed('space') and (self.stage_timer - self.last_spawn_time > 0.1 or self.stage == STAGE_DRIFTING): # Limit rapid spawns
            # Spawn a few chronons or give a boost
            for _ in range(random.randint(1, 4)): # Spawn more per press
                self._spawn_chronon(velocity_boost=True)
            for c in self.chronons: # Boost existing chronons
                c.vx += random.uniform(-15, 15)
                c.vy += random.uniform(-15, 15)
            
            Sound.play_tone(750 + random.randint(0, 400), 0.04) # Slightly higher pitched, shorter sound
            self.last_spawn_time = self.stage_timer


        if Input.is_key_pressed('w'):
            self.attraction_strength += ATTRACTION_CHANGE_RATE * delta
            if self.attraction_strength > MAX_ATTRACTION_STRENGTH:
                self.attraction_strength = MAX_ATTRACTION_STRENGTH

        if Input.is_key_pressed('s'):
            self.attraction_strength -= ATTRACTION_CHANGE_RATE * delta
            if self.attraction_strength < MIN_ATTRACTION_STRENGTH:
                self.attraction_strength = MIN_ATTRACTION_STRENGTH


        if Input.is_key_pressed('a'):
            self.rotational_force -= ROTATIONAL_CHANGE_RATE * delta
            if self.rotational_force < MIN_ROTATIONAL_FORCE:
                self.rotational_force = MIN_ROTATIONAL_FORCE

        if Input.is_key_pressed('d'):
            self.rotational_force += ROTATIONAL_CHANGE_RATE * delta
            if self.rotational_force > MAX_ROTATIONAL_FORCE:
                self.rotational_force = MAX_ROTATIONAL_FORCE

        self._update_physics(delta)
        self._update_strands(delta)
        self._update_stage(delta)

    def draw(self):
        # Draw strands first (background)
        for s in self.strands:
            c1 = self.chronon_map.get(s.c1_id)
            c2 = self.chronon_map.get(s.c2_id)
            if c1 and c2:
                # Strand intensity based on strength
                # For this white-only context, we can vary 'thickness' or 'flicker'
                line_count = int(s.strength * 4) + 1 # 1 to 5 lines for more pronounced weaving
                for i in range(line_count):
                    # Slight offset for multi-line effect
                    offset_x = (i - line_count // 2) * 0.5
                    offset_y = (i - line_count // 2) * 0.5
                    Render.draw_line(int(c1.x + offset_x), int(c1.y + offset_y),
                                     int(c2.x + offset_x), int(c2.y + offset_y))

        # Draw chronons (foreground)
        for c in self.chronons:
            # Chronon intensity based on life
            radius = int(c.life / CHRONON_MAX_LIFE * CHRONON_RADIUS)
            if radius < 1: radius = 1
            # Add a flicker effect or pulse for resonant stage
            if self.stage == STAGE_RESONANT_TAPESTRY:
                flicker_scale = 1.0 + math.sin(self.stage_timer * 8 + c.id) * 0.2 # Pulsing effect
                Render.draw_circle(int(c.x), int(c.y), int(radius * flicker_scale), filled=True)
            else:
                Render.draw_circle(int(c.x), int(c.y), radius, filled=True)

        # Draw UI/instructions
        Render.draw_text(self.message, 10, 10)
        Render.draw_text(f"Complexity: {int(self.complexity_score)}", 10, 30)
        Render.draw_text(f"Attraction: {self.attraction_strength:.1f}", 10, 50)
        Render.draw_text(f"Rotation: {self.rotational_force:.1f}", 10, 70)


    def get_instructions(self) -> str:
        return "Space: Spawn/Boost Chronons | W/S: Adjust Attraction | A/D: Adjust Rotation"

    def get_next_idea(self) -> list[str]:
        return ["Gravity Wells", "Fractal Loops"]
