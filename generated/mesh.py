import math
import random
from generated.helpers import Render, Input, Sound

class GridPoint:
    def __init__(self, ox, oy):
        self.original_x = ox
        self.original_y = oy
        self.current_x = ox
        self.current_y = oy
        self.is_glowing = False
        self.glow_timer = 0.0
        self.max_glow_duration = 0.0
        self.max_glow_radius = 0.0 # Stores the initial radius for fading calculation

    def update(self, global_time, center_x, center_y, base_amplitude, frequency_multiplier, wave_speed_factor, distortion_strength):
        dx = self.original_x - center_x
        dy = self.original_y - center_y
        dist_from_center = math.sqrt(dx*dx + dy*dy)

        # Base global pulse, affecting the whole grid uniformly in magnitude
        global_pulse_magnitude = math.sin(global_time * frequency_multiplier) * base_amplitude * (1 - distortion_strength * 0.5)

        # Propagating ripple effect, demonstrating continuous sinusoidal movement
        ripple_phase = (global_time * frequency_multiplier * wave_speed_factor) + (dist_from_center * 0.05 * wave_speed_factor)
        ripple_magnitude = math.sin(ripple_phase) * base_amplitude * distortion_strength * 0.5

        total_displacement_magnitude = global_pulse_magnitude + ripple_magnitude

        if dist_from_center == 0:
            self.current_x = self.original_x
            self.current_y = self.original_y
            return

        norm_dx = dx / dist_from_center
        norm_dy = dy / dist_from_center

        self.current_x = self.original_x + norm_dx * total_displacement_magnitude
        self.current_y = self.original_y + norm_dy * total_displacement_magnitude

    def start_glow(self, duration, max_radius):
        self.is_glowing = True
        self.glow_timer = duration
        self.max_glow_duration = duration
        self.max_glow_radius = max_radius

    def update_glow(self, delta):
        if self.is_glowing:
            self.glow_timer -= delta
            if self.glow_timer <= 0:
                self.is_glowing = False 
                self.glow_timer = 0.0
                self.max_glow_duration = 0.0
                self.max_glow_radius = 0.0

class Program:
    def __init__(self):
        self.time = 0.0
        self.grid_size_x = 20 # Number of points horizontally
        self.grid_size_y = 15 # Number of points vertically
        self.cell_spacing = 20 # Pixels between original points

        self.center_x = 400 // 2
        self.center_y = 300 // 2

        self.grid = []
        # Calculate offset to center the grid visually within the 400x300 window
        start_x_offset = (400 - (self.grid_size_x - 1) * self.cell_spacing) / 2
        start_y_offset = (300 - (self.grid_size_y - 1) * self.cell_spacing) / 2

        for y_idx in range(self.grid_size_y):
            row = []
            for x_idx in range(self.grid_size_x):
                original_x = start_x_offset + x_idx * self.cell_spacing
                original_y = start_y_offset + y_idx * self.cell_spacing
                row.append(GridPoint(original_x, original_y))
            self.grid.append(row)

        self.current_base_amplitude = 12.0
        self.current_frequency_multiplier = 1.5
        self.current_wave_speed_factor = 1.0
        self.current_distortion_strength = 1.0 # Full ripple effect

        self.glow_trigger_chance_per_node_per_sec = 0.06 # Frequent
        self.current_glow_duration = 1.2 # Longer glow duration
        self.current_glow_max_radius = 4.0 # Larger glow radius

    def update(self, delta: float):
        self.time += delta

        # Update all grid points with current stage parameters
        for y_idx in range(self.grid_size_y):
            for x_idx in range(self.grid_size_x):
                point = self.grid[y_idx][x_idx]
                point.update(self.time, self.center_x, self.center_y,
                                               self.current_base_amplitude, self.current_frequency_multiplier,
                                               self.current_wave_speed_factor, self.current_distortion_strength)

                point.update_glow(delta) # Update glow timer for each point

                # Randomly trigger new glows for non-glowing points
                # Chance is proportional to delta time to make it frame-rate independent
                if not point.is_glowing and random.random() < self.glow_trigger_chance_per_node_per_sec * delta:
                    point.start_glow(self.current_glow_duration, self.current_glow_max_radius)

    def draw(self):
        # Draw grid lines connecting adjacent points
        for y_idx in range(self.grid_size_y):
            for x_idx in range(self.grid_size_x):
                current_point = self.grid[y_idx][x_idx]

                # Draw horizontal lines to the right
                if x_idx < self.grid_size_x - 1:
                    next_point_x = self.grid[y_idx][x_idx + 1]
                    Render.draw_line(int(current_point.current_x), int(current_point.current_y),
                                     int(next_point_x.current_x), int(next_point_x.current_y))

                # Draw vertical lines downwards
                if y_idx < self.grid_size_y - 1:
                    next_point_y = self.grid[y_idx + 1][x_idx]
                    Render.draw_line(int(current_point.current_x), int(current_point.current_y),
                                     int(next_point_y.current_x), int(next_point_y.current_y))

        # Draw glowing points on top of the lines
        for y_idx in range(self.grid_size_y):
            for x_idx in range(self.grid_size_x):
                point = self.grid[y_idx][x_idx]
                if point.is_glowing:
                    # Calculate current radius, fading from max_glow_radius down to 0
                    current_radius = int(point.max_glow_radius * (point.glow_timer / point.max_glow_duration))
                    if current_radius > 0: # Only draw if radius is positive
                        Render.draw_circle(int(point.current_x), int(point.current_y), current_radius, filled=True)

    def get_instructions(self) -> str:
        return "Brain pattern steady... connection restarted or errored."

    def get_next_idea(self) -> list[str]:
        return []