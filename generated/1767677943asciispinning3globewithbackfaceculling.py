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
        self.POINT_COUNT = 500 # Initial number of points on the sphere
        self.points = []
        self.rotation_y = 0.0 # Current Y-axis rotation
        self.rotation_x = 0.0 # Current X-axis rotation (for subtle tilt)
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

        self.fragment_spread_factor = 0.0 # For stage 3, fragments spread out

        self._initialize_globe_points()

    def _initialize_globe_points(self):
        self.points = []
        for _ in range(self.POINT_COUNT):
            # Generate random points on a sphere using inverse transform sampling
            phi = math.acos(2 * random.random() - 1) # Polar angle (0 to pi)
            theta = 2 * math.pi * random.random()      # Azimuthal angle (0 to 2*pi)

            x = self.GLOBE_RADIUS * math.sin(phi) * math.cos(theta)
            y = self.GLOBE_RADIUS * math.sin(phi) * math.sin(theta)
            z = self.GLOBE_RADIUS * math.cos(phi)

            # Start with very faint characters for the initial stage
            self.points.append({'original_pos': (x, y, z), 'char_idx': random.randint(0, self.max_char_idx // 4)})

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
        # Simple perspective projection
        # Camera implicitly at (0, 0, -focal_length) looking towards origin
        # Z-depth for perspective calculation, relative to the focal plane at origin
        z_projected = z + self.focal_length 

        if z_projected <= 0: # Point is behind or at the focal plane
            return None, None, None

        scale_factor = self.focal_length / z_projected
        screen_x = self.CENTER_X + (x * scale_factor)
        screen_y = self.CENTER_Y + (y * scale_factor)

        return int(screen_x), int(screen_y), z_projected

    def update(self, delta: float):
        self.stage_timer += delta

        # Dream progression logic
        if self.stage == 0: # Genesis: A few faint fragments appear, slowly rotating
            self.rotation_y += self.rotation_speed_y * delta * 0.5
            self.rotation_x += self.rotation_speed_x * delta * 0.2
            if self.stage_timer > self.stage_duration[0]:
                self.stage = 1
                self.stage_timer = 0.0
                # Coalescence: More points, slightly brighter base
                self.POINT_COUNT = 1500
                self._initialize_globe_points()
                for p in self.points:
                    p['char_idx'] = random.randint(self.max_char_idx // 4, self.max_char_idx // 2)

        elif self.stage == 1: # Coalescence: More fragments form a discernible sphere, becoming brighter
            self.rotation_y += self.rotation_speed_y * delta
            self.rotation_x += self.rotation_speed_x * delta
            if self.stage_timer > self.stage_duration[1]:
                self.stage = 2
                self.stage_timer = 0.0
                # Flow: All points get a good base brightness
                for p in self.points:
                    p['char_idx'] = random.randint(self.max_char_idx // 2, self.max_char_idx * 3 // 4)

        elif self.stage == 2: # Flow: Characters subtly shift, like currents of thought
            self.rotation_y += self.rotation_speed_y * delta * 1.2 # Faster spin
            self.rotation_x += self.rotation_speed_x * delta * 0.8 # Slower wobble
            # Randomly change character index for some points to simulate flow/flicker
            if random.random() < 0.3: # Chance per frame to update some points
                for p in self.points:
                    if random.random() < 0.05: # Small chance per point to change
                        p['char_idx'] = random.randint(self.max_char_idx // 2, self.max_char_idx)
            if self.stage_timer > self.stage_duration[2]:
                self.stage = 3
                self.stage_timer = 0.0
                # Insight: All points glow brightly initially
                for p in self.points:
                    p['char_idx'] = self.max_char_idx # Max brightness
                self.fragment_spread_factor = 0.0 # Reset spread

        elif self.stage == 3: # Insight: Sphere glows intensely, then dissipates
            # Initial glow phase
            if self.stage_timer < 2.0: # Glow for 2 seconds
                self.rotation_y += self.rotation_speed_y * delta * 0.5
                self.rotation_x += self.rotation_speed_x * delta * 0.5
            else: # Dissipation phase
                self.fragment_spread_factor += delta * 15.0 # Increase spread speed
                self.rotation_y += self.rotation_speed_y * delta * 0.1 # Slow down spin
                self.rotation_x += self.rotation_speed_x * delta * 0.05
                # Fade characters in point data over time
                for p in self.points:
                    if p['char_idx'] > 0:
                        p['char_idx'] = max(0, p['char_idx'] - int(delta * 5)) # Fade speed
            
            if self.stage_timer > self.stage_duration[3]:
                # End of dream cycle, loop back to genesis
                self.stage = 0
                self.stage_timer = 0.0
                self.POINT_COUNT = 500 # Reset point count
                self._initialize_globe_points() # Reinitialize for genesis
                self.fragment_spread_factor = 0.0
                self.rotation_y = 0.0
                self.rotation_x = 0.0

    def draw(self):
        # Prevent drawing during very brief transition moments for smoother restart
        if self.stage == 0 and self.stage_timer < 0.5:
            return
        if self.stage == 3 and self.stage_timer > self.stage_duration[3] - 0.5 and self.fragment_spread_factor > self.GLOBE_RADIUS * 3:
            return

        for point_data in self.points:
            orig_x, orig_y, orig_z = point_data['original_pos']

            temp_x, temp_y, temp_z = orig_x, orig_y, orig_z

            # Apply spreading for stage 3 dissipation
            if self.stage == 3 and self.stage_timer >= 2.0: # Dissipation phase
                vec_len = math.sqrt(orig_x**2 + orig_y**2 + orig_z**2)
                if vec_len > 0.001: # Avoid division by zero for normalization
                    # Normalize vector from origin to point and scale by spread factor
                    norm_x = orig_x / vec_len
                    norm_y = orig_y / vec_len
                    norm_z = orig_z / vec_len
                    
                    temp_x += norm_x * self.fragment_spread_factor
                    temp_y += norm_y * self.fragment_spread_factor
                    temp_z += norm_z * self.fragment_spread_factor
                else: # Handle points originally at or very near the origin
                    # Just add a small random spread
                    temp_x += (random.random() - 0.5) * self.fragment_spread_factor * 0.1
                    temp_y += (random.random() - 0.5) * self.fragment_spread_factor * 0.1
                    temp_z += (random.random() - 0.5) * self.fragment_spread_factor * 0.1

            # Rotate the point (temp_x, temp_y, temp_z are the potentially spread points)
            rotated_x, rotated_y, rotated_z = self._rotate_point(
                temp_x, temp_y, temp_z, self.rotation_x, self.rotation_y
            )

            # Backface culling: If the point's Z-coordinate after rotation is positive, it's on the "back" side.
            # (Assuming camera is looking down the -Z axis from a positive Z position, so negative Z is front)
            if rotated_z > 0:
                continue

            # Project the point
            screen_x, screen_y, projected_z_distance = self._project_point(rotated_x, rotated_y, rotated_z)

            if screen_x is None: # Point was behind projection plane or too far
                continue

            # Check screen boundaries, allowing characters to partially go off for smoother edges
            if not (-16 < screen_x < self.SCREEN_WIDTH and -16 < screen_y < self.SCREEN_HEIGHT):
                continue
            
            # Get the current base character index for this point (this value is updated in `update`)
            current_point_char_idx = point_data['char_idx']

            # If the point has completely faded, skip drawing it
            if current_point_char_idx <= 0:
                continue

            # Modify char_index based on projected Z-depth (closer = brighter/denser character)
            # Visible range for rotated_z is approximately [-MAX_ABS_Z, 0] due to culling.
            # normalized_depth: 0.0 (far visible, z~0) to 1.0 (near, z~-MAX_ABS_Z)
            max_z_for_depth_calc = self.GLOBE_RADIUS + self.fragment_spread_factor
            if max_z_for_depth_calc < 0.001: max_z_for_depth_calc = 0.001 # Prevent division by zero

            normalized_depth = abs(rotated_z) / max_z_for_depth_calc
            normalized_depth = min(1.0, max(0.0, normalized_depth)) # Clamp to [0, 1]

            # Depth influence: closer points add more brightness to the base char_idx
            depth_influence = int(normalized_depth * (self.max_char_idx * 0.4)) # Depth can add up to 40% of max brightness
            
            final_char_index = current_point_char_idx + depth_influence
            final_char_index = min(final_char_index, self.max_char_idx) # Cap at max brightness

            # Stage-specific visual adjustments (beyond the base_char_idx setting in update)
            if self.stage == 0: # Genesis: Very faint overall appearance
                final_char_index = int(final_char_index * 0.2)
            elif self.stage == 1: # Coalescence: Faint but building up
                final_char_index = int(final_char_index * 0.5)
            elif self.stage == 2: # Flow: Dynamic and somewhat brighter, with subtle flickering
                if random.random() < 0.005: # Small chance for individual point flicker
                    final_char_index = random.randint(0, self.max_char_idx)
                else:
                    final_char_index = int(final_char_index * (0.8 + random.random() * 0.4)) # Slight random variation

            # Ensure final_char_index is within valid bounds for self.depth_chars
            final_char_index = min(max(0, final_char_index), self.max_char_idx)
            char_to_draw = self.depth_chars[final_char_index]
            Render.draw_text(char_to_draw, screen_x, screen_y)

    def get_instructions(self) -> str:
        return "Observe the evolving sphere of thought."

    def get_next_idea(self) -> list[str]:
        # Dream ideas for further iteration
        return ["Sonic Pulses", "Fractal Growth"]