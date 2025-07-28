#!/usr/bin/env python3
"""
Spray Parameters Module
======================
Configuration classes for spray painting simulation parameters.
"""

import numpy as np
import math
from typing import Tuple
from PIL import Image


class SprayParameters:
    """Configuration for spray painting parameters"""
    def __init__(self):
        self.spray_width = 0.5          # Width of spray fan at 1 unit distance
        self.spray_range = 2.0          # Maximum spray distance
        self.spray_density = 500        # Number of spray particles per frame (reduced for CPU)
        self.paint_intensity = 0.15     # Paint accumulation per particle hit (increased)
        self.nozzle_distance = 0.8      # Distance from nozzle to wall (reduced)
        self.fan_angle = 25.0           # Spray fan angle in degrees (reduced)


class WallMesh:
    """Represents the wall surface and paint accumulation"""
    def __init__(self, width: float = 4.0, height: float = 3.0, resolution: int = 128):
        self.width = width
        self.height = height
        self.resolution = resolution
        
        # Create paint coverage texture (0 = no paint, 1 = full coverage)
        self.paint_coverage = np.zeros((resolution, resolution), dtype=np.float32)
        
        # Create mesh vertices and faces
        self.vertices, self.faces = self._create_mesh()
        
    def _create_mesh(self):
        """Create wall mesh vertices and faces"""
        # Create a simple quad for the wall
        vertices = np.array([
            [-self.width/2, -self.height/2, 0],  # Bottom left
            [self.width/2, -self.height/2, 0],   # Bottom right
            [self.width/2, self.height/2, 0],    # Top right
            [-self.width/2, self.height/2, 0]    # Top left
        ], dtype=np.float32)
        
        faces = np.array([
            [0, 1, 2],  # First triangle
            [0, 2, 3]   # Second triangle
        ], dtype=np.int32)
        
        return vertices, faces
    
    def world_to_texture(self, world_pos: np.ndarray) -> Tuple[int, int]:
        """Convert world position to texture coordinates"""
        # Normalize world position to [0, 1]
        u = (world_pos[0] + self.width/2) / self.width
        v = (world_pos[1] + self.height/2) / self.height
        
        # Convert to texture coordinates
        x = int(u * self.resolution)
        y = int(v * self.resolution)
        
        # Clamp to valid range
        x = max(0, min(x, self.resolution - 1))
        y = max(0, min(y, self.resolution - 1))
        
        return x, y
    
    def add_paint(self, positions: np.ndarray, intensity: float):
        """Add paint to the wall at specified positions"""
        if len(positions) == 0:
            return
            
        for pos in positions:
            # Check if position is on the wall surface (z should be close to 0)
            if abs(pos[2]) < 0.2:  # Increased tolerance
                x, y = self.world_to_texture(pos)
                # Add paint with falloff
                self.paint_coverage[y, x] = min(1.0, self.paint_coverage[y, x] + intensity)
                
                # Add some blur/spread effect with larger radius
                spread_radius = 2
                for dx in range(-spread_radius, spread_radius + 1):
                    for dy in range(-spread_radius, spread_radius + 1):
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.resolution and 0 <= ny < self.resolution:
                            distance = math.sqrt(dx*dx + dy*dy)
                            spread_intensity = intensity * 0.3 * max(0, 1 - distance / spread_radius)
                            self.paint_coverage[ny, nx] = min(1.0, self.paint_coverage[ny, nx] + spread_intensity)

    def save_texture(self, filename: str):
        """Save current paint coverage as texture"""
        # Convert to 8-bit image with color mapping
        paint_rgb = np.zeros((self.resolution, self.resolution, 3), dtype=np.uint8)
        
        # Create paint color (red paint)
        for y in range(self.resolution):
            for x in range(self.resolution):
                coverage = self.paint_coverage[y, x]
                if coverage > 0:
                    # Red paint with varying intensity
                    paint_rgb[y, x] = [int(255 * coverage), int(50 * coverage), int(50 * coverage)]
                else:
                    # Wall color (light gray)
                    paint_rgb[y, x] = [200, 200, 200]
        
        # Save as PNG
        image = Image.fromarray(paint_rgb)
        image.save(filename)
        print(f"Saved texture: {filename}")
