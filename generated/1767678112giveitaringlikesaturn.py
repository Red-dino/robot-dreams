import math
import random
from generated.helpers import Render, Input, Sound

import math
import random

class Program:
    def __init__(self):
        self.SCREEN_WIDTH = 400
        self.SCREEN_HEIGHT = 300
        self.CENTER_X = self.SCREEN_WIDTH // 2
        self.CENTER_Y = self.SCREEN_HEIGHT // 2

        self.GLOBE_RADIUS = 80
        self.GLOBE_POINT_COUNT_BASE = 500 # Initial number of points on the sphere
        self.globe_points = []

        self.RING_INNER_RADIUS = 100
        self.RING_OUTER_RADIUS = 130
        self.RING_THICKNESS = 5.0 # Perceived Z-thickness for the ring
        self.RING_POINT_COUNT_BASE = 800 # Initial number of points on the ring
        self.RING_TILT_ANGLE_BASE = math.radians(20) # Static tilt angle relative to global XY plane
        self.ring_points = []

        self.rotation_y = 0.0 # Current Y-axis rotation for the entire system
        self.rotation_x = 0.0 # Current X-axis rotation (for subtle tilt of entire system)
        self.rotation_speed_y = 0.3 # Radians per second
        self.rotation_speed_x = 0.05 # Radians per second for tilt

        self.focal_length = 250 # For perspective projection
        
        # ASCII characters from 'far' to 'near' (less dense to more dense)
        self.depth_chars = " .,-~:;=!*#$@"
        self.max_char_idx = len(self.depth_chars) - 1

        # Dream progression
        self.stage = 0 # 0: Genesis, 1: Coalescence, 2: Flow, 3: Insight & Dissipation
        self.stage_timer = 0.0
        self.stage_duration = [8.0, 10.0, 12.0, 15.0] # Durations for each stage

        self.fragment_spread_factor_globe = 0.0 # For stage 3, fragments spread out
        self.fragment_spread_factor_ring = 0.0 # Separate spread for ring

        self._initialize_points() # Initialize both globe and ring points

    def _initialize_points(self):
        self.globe_points = []
        for _ in range(self.GLOBE_POINT_COUNT_BASE):
            phi = math.acos(2 * random.random() - 1)
            theta = 2 * math.pi * random.random()
            x = self.GLOBE_RADIUS * math.sin(phi) * math.cos(theta)
            y = self.GLOBE_RADIUS * math.sin(phi) * math.sin(theta)
            z = self.GLOBE_RADIUS * math.cos(phi)
            self.globe_points.append({'original_pos': (x, y, z), 'char_idx': random.randint(0, self.max_char_idx // 8)}) # Very faint initially

        self.ring_points = []
        for _ in range(self.RING_POINT_COUNT_BASE):
            theta = 2 * math.pi * random.random()
            # Uniform distribution for points within annulus area
            r = math.sqrt(random.uniform(self.RING_INNER_RADIUS**2, self.RING_OUTER_RADIUS**2))
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            z = random.uniform(-self.RING_THICKNESS / 2, self.RING_THICKNESS / 2) # Give it some slight Z depth for perceived thickness
            self.ring_points.append({'original_pos': (x, y, z), 'char_idx': random.randint(0, self.max_char_idx // 8)}) # Also faint

    def _rotate_point(self, x, y, z, rot_x, rot_y):
        # Rotate around Y-axis
        rotated_x_y = x * math.cos(rot_y) - z * math.sin(rot_y)
        rotated_z_y = x * math.sin(rot_y) + z * math.cos(rot_y)
        rotated_y_y = y # Y is unchanged in Y-axis rotation

        # Rotate around X-axis (using the previously Y-rotated points)
        final_y = rotated_y_y * math.cos(rot_x) - rotated_z_y * math.sin(rot_x)
        final_z = rotated_y_y * math.sin(rot_x) + rotated_z_y * math.cos(rot_x)
        final_x = rotated_x_y # X is unchanged in X-axis rotation

        return final_x, final_y, final_z

    def _project_point(self, x, y, z):
        z_projected = z + self.focal_length 

        if z_projected <= 0:
            return None, None, None

        scale_factor = self.focal_length / z_projected
        screen_x = self.CENTER_X + (x * scale_factor)
        screen_y = self.CENTER_Y + (y * scale_factor)

        return int(screen_x), int(screen_y), z_projected

    def update(self, delta: float):
        self.stage_timer += delta

        # Update global rotations for both globe and ring
        self.rotation_y += self.rotation_speed_y * delta
        self.rotation_x += self.rotation_speed_x * delta

        # Dream progression logic
        if self.stage == 0: # Genesis: Faint fragments appear
            # Initial state already set by _initialize_points
            self.rotation_y *= 0.5 # Slower spin
            self.rotation_x *= 0.5 # Slower wobble
            if self.stage_timer > self.stage_duration[0]:
                self.stage = 1
                self.stage_timer = 0.0
                # Coalescence: More points, slightly brighter base
                self.GLOBE_POINT_COUNT_BASE = 1500
                self.RING_POINT_COUNT_BASE = 2500
                self._initialize_points() # Reinitialize with more points
                for p in self.globe_points:
                    p['char_idx'] = random.randint(self.max_char_idx // 4, self.max_char_idx // 2)
                for p in self.ring_points:
                    p['char_idx'] = random.randint(self.max_char_idx // 6, self.max_char_idx // 3) # Ring slightly less bright initially

        elif self.stage == 1: # Coalescence: More fragments form discernible shapes, becoming brighter
            if self.stage_timer > self.stage_duration[1]:
                self.stage = 2
                self.stage_timer = 0.0
                # Flow: All points get a good base brightness
                for p in self.globe_points:
                    p['char_idx'] = random.randint(self.max_char_idx // 2, self.max_char_idx * 3 // 4)
                for p in self.ring_points:
                    p['char_idx'] = random.randint(self.max_char_idx // 3, self.max_char_idx // 2)

        elif self.stage == 2: # Flow: Characters subtly shift, like currents of thought
            self.rotation_y *= 1.2 # Faster spin
            self.rotation_x *= 0.8 # Slower wobble
            # Randomly change character index for some points to simulate flow/flicker
            if random.random() < 0.3:
                for p in self.globe_points:
                    if random.random() < 0.05:
                        p['char_idx'] = random.randint(0, self.max_char_idx)
                for p in self.ring_points:
                    if random.random() < 0.03: # Ring points flicker less intensely
                        p['char_idx'] = random.randint(0, self.max_char_idx * 2 // 3)
            if self.stage_timer > self.stage_duration[2]:
                self.stage = 3
                self.stage_timer = 0.0
                # Insight: All points glow brightly initially
                for p in self.globe_points:
                    p['char_idx'] = self.max_char_idx # Max brightness
                for p in self.ring_points:
                    p['char_idx'] = self.max_char_idx * 3 // 4 # Ring slightly less intense
                self.fragment_spread_factor_globe = 0.0 # Reset spread
                self.fragment_spread_factor_ring = 0.0

        elif self.stage == 3: # Insight: Sphere and ring glow intensely, then dissipate
            if self.stage_timer < 2.0: # Initial glow phase
                self.rotation_y *= 0.5
                self.rotation_x *= 0.5
            else: # Dissipation phase
                self.fragment_spread_factor_globe += delta * 15.0
                self.fragment_spread_factor_ring += delta * 20.0 # Ring dissipates faster/further
                self.rotation_y *= 0.1
                self.rotation_x *= 0.05
                for p in self.globe_points:
                    if p['char_idx'] > 0:
                        p['char_idx'] = max(0, p['char_idx'] - int(delta * 5))
                for p in self.ring_points:
                    if p['char_idx'] > 0:
                        p['char_idx'] = max(0, p['char_idx'] - int(delta * 8)) # Ring fades faster
            
            if self.stage_timer > self.stage_duration[3]:
                # End of dream cycle, loop back to genesis
                self.stage = 0
                self.stage_timer = 0.0
                self.GLOBE_POINT_COUNT_BASE = 500
                self.RING_POINT_COUNT_BASE = 800
                self._initialize_points()
                self.fragment_spread_factor_globe = 0.0
                self.fragment_spread_factor_ring = 0.0
                self.rotation_y = 0.0
                self.rotation_x = 0.0

    def draw(self):
        if self.stage == 0 and self.stage_timer < 0.5:
            return
        if self.stage == 3 and self.stage_timer > self.stage_duration[3] - 0.5 and (self.fragment_spread_factor_globe > self.GLOBE_RADIUS * 3 or self.fragment_spread_factor_ring > self.RING_OUTER_RADIUS * 3):
            return

        display_points_to_render = []

        # Process Globe Points
        for point_data in self.globe_points:
            orig_x, orig_y, orig_z = point_data['original_pos']
            temp_x, temp_y, temp_z = orig_x, orig_y, orig_z

            if self.stage == 3 and self.stage_timer >= 2.0:
                vec_len = math.sqrt(orig_x**2 + orig_y**2 + orig_z**2)
                if vec_len > 0.001:
                    norm_x, norm_y, norm_z = orig_x / vec_len, orig_y / vec_len, orig_z / vec_len
                    temp_x += norm_x * self.fragment_spread_factor_globe
                    temp_y += norm_y * self.fragment_spread_factor_globe
                    temp_z += norm_z * self.fragment_spread_factor_globe
                else:
                    temp_x += (random.random() - 0.5) * self.fragment_spread_factor_globe * 0.1
                    temp_y += (random.random() - 0.5) * self.fragment_spread_factor_globe * 0.1
                    temp_z += (random.random() - 0.5) * self.fragment_spread_factor_globe * 0.1

            rotated_x, rotated_y, rotated_z = self._rotate_point(
                temp_x, temp_y, temp_z, self.rotation_x, self.rotation_y
            )

            # Backface culling for globe: if point's Z-coordinate is positive, it's on the "back" side relative to camera at (0,0,-focal_length)
            if rotated_z > 0:
                continue

            screen_x, screen_y, projected_z_distance = self._project_point(rotated_x, rotated_y, rotated_z)

            if screen_x is None:
                continue
            if not (-16 < screen_x < self.SCREEN_WIDTH and -16 < screen_y < self.SCREEN_HEIGHT):
                continue
            
            current_point_char_idx = point_data['char_idx']
            if current_point_char_idx <= 0:
                continue

            max_z_for_depth_calc = self.GLOBE_RADIUS + self.fragment_spread_factor_globe
            normalized_depth = abs(rotated_z) / (max_z_for_depth_calc if max_z_for_depth_calc > 0.001 else 0.001)
            normalized_depth = min(1.0, max(0.0, normalized_depth))

            depth_influence = int(normalized_depth * (self.max_char_idx * 0.4))
            final_char_index = current_point_char_idx + depth_influence
            final_char_index = min(final_char_index, self.max_char_idx)

            if self.stage == 0:
                final_char_index = int(final_char_index * 0.2)
            elif self.stage == 1:
                final_char_index = int(final_char_index * 0.5)
            elif self.stage == 2:
                if random.random() < 0.005:
                    final_char_index = random.randint(0, self.max_char_idx)
                else:
                    final_char_index = int(final_char_index * (0.8 + random.random() * 0.4))

            final_char_index = min(max(0, final_char_index), self.max_char_idx)
            char_to_draw = self.depth_chars[final_char_index]
            display_points_to_render.append({'char': char_to_draw, 'x': screen_x, 'y': screen_y, 'z': projected_z_distance})

        # Process Ring Points
        for point_data in self.ring_points:
            orig_x, orig_y, orig_z = point_data['original_pos']
            temp_x, temp_y, temp_z = orig_x, orig_y, orig_z

            if self.stage == 3 and self.stage_timer >= 2.0:
                # Radial spread from the center of the ring
                dist_from_origin = math.sqrt(orig_x**2 + orig_y**2 + orig_z**2)
                if dist_from_origin > 0.001:
                    norm_x, norm_y, norm_z = orig_x / dist_from_origin, orig_y / dist_from_origin, orig_z / dist_from_origin
                    temp_x += norm_x * self.fragment_spread_factor_ring
                    temp_y += norm_y * self.fragment_spread_factor_ring
                    temp_z += norm_z * self.fragment_spread_factor_ring
                else: # Points at origin
                    temp_x += (random.random() - 0.5) * self.fragment_spread_factor_ring * 0.1
                    temp_y += (random.random() - 0.5) * self.fragment_spread_factor_ring * 0.1
                    temp_z += (random.random() - 0.5) * self.fragment_spread_factor_ring * 0.1
            
            # Apply fixed ring tilt first
            tilted_x, tilted_y, tilted_z = self._rotate_point(temp_x, temp_y, temp_z, self.RING_TILT_ANGLE_BASE, 0)
            
            # Then apply global system rotation
            rotated_x, rotated_y, rotated_z = self._rotate_point(
                tilted_x, tilted_y, tilted_z, self.rotation_x, self.rotation_y
            )

            screen_x, screen_y, projected_z_distance = self._project_point(rotated_x, rotated_y, rotated_z)

            if screen_x is None:
                continue
            if not (-16 < screen_x < self.SCREEN_WIDTH and -16 < screen_y < self.SCREEN_HEIGHT):
                continue
            
            current_point_char_idx = point_data['char_idx']
            if current_point_char_idx <= 0:
                continue

            max_z_for_depth_calc = self.RING_OUTER_RADIUS + self.fragment_spread_factor_ring
            normalized_depth = abs(rotated_z) / (max_z_for_depth_calc if max_z_for_depth_calc > 0.001 else 0.001)
            normalized_depth = min(1.0, max(0.0, normalized_depth))

            depth_influence = int(normalized_depth * (self.max_char_idx * 0.3)) # Ring might have less depth variation visually
            final_char_index = current_point_char_idx + depth_influence
            final_char_index = min(final_char_index, self.max_char_idx)

            if self.stage == 0:
                final_char_index = int(final_char_index * 0.1) # Even fainter than globe
            elif self.stage == 1:
                final_char_index = int(final_char_index * 0.3) # Less bright than globe
            elif self.stage == 2:
                if random.random() < 0.002: # Less frequent flicker for ring
                    final_char_index = random.randint(0, self.max_char_idx // 2)
                else:
                    final_char_index = int(final_char_index * (0.6 + random.random() * 0.2)) # Less overall brightness

            final_char_index = min(max(0, final_char_index), self.max_char_idx)
            char_to_draw = self.depth_chars[final_char_index]
            display_points_to_render.append({'char': char_to_draw, 'x': screen_x, 'y': screen_y, 'z': projected_z_distance})

        # Sort all points by projected Z-distance (farthest first, so closer points draw over them)
        display_points_to_render.sort(key=lambda p: p['z'], reverse=False)

        for p in display_points_to_render:
            Render.draw_text(p['char'], p['x'], p['y'])

    def get_instructions(self) -> str:
        return "Observe the evolving sphere and its rings of thought."

    def get_next_idea(self) -> list[str]:
        return ["Shifting Colors", "Interacting Fields"]