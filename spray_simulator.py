#!/usr/bin/env python3
"""
Spray Simulator Module
=====================
Main simulation engine using Isaac Warp for spray painting.
"""

import numpy as np
import warp as wp
import os
import json
import matplotlib.pyplot as plt
from typing import Tuple, List
from spray_parameters import SprayParameters, WallMesh

# Initialize Warp with CPU device
wp.init()
device = wp.get_device("cpu")
print(f"Using device: {device}")

# OpenUSD imports
try:
    from pxr import Usd, UsdGeom, Sdf, Gf, UsdShade, Vt
    USD_AVAILABLE = True
except ImportError:
    print("OpenUSD not found. Install with: pip install usd-core")
    USD_AVAILABLE = False


@wp.kernel
def spray_emission_kernel(
    positions: wp.array(dtype=wp.vec3),
    velocities: wp.array(dtype=wp.vec3),
    nozzle_pos: wp.vec3,
    spray_dir: wp.vec3,
    spray_width: float,
    spray_speed: float,
    fan_angle: float,
    random_seed: int
):
    """Warp kernel for spray particle emission"""
    tid = wp.tid()
    
    # Create random state for this thread
    rng = wp.rand_init(random_seed + tid, tid)
    
    # Generate random direction within spray fan
    angle_rad = wp.randf(rng, -fan_angle, fan_angle) * 3.14159 / 180.0
    spread_x = wp.randf(rng, -spray_width, spray_width) * 0.5
    spread_y = wp.randf(rng, -spray_width, spray_width) * 0.5
    
    # Create spread vectors
    right = wp.vec3(1.0, 0.0, 0.0)
    up = wp.vec3(0.0, 1.0, 0.0)
    
    # Calculate final direction with spread
    cos_angle = wp.cos(angle_rad)
    sin_angle = wp.sin(angle_rad)
    
    # Apply spread in x and y directions
    direction = spray_dir + right * spread_x + up * spread_y
    direction = wp.normalize(direction)
    
    # Add some random starting offset
    offset_x = wp.randf(rng, -0.1, 0.1)
    offset_y = wp.randf(rng, -0.1, 0.1)
    start_pos = nozzle_pos + wp.vec3(offset_x, offset_y, 0.0)
    
    # Set particle position and velocity
    positions[tid] = start_pos
    velocities[tid] = direction * spray_speed


@wp.kernel
def spray_update_kernel(
    positions: wp.array(dtype=wp.vec3),
    velocities: wp.array(dtype=wp.vec3),
    active: wp.array(dtype=int),
    hit_wall: wp.array(dtype=int),
    dt: float,
    wall_z: float
):
    """Warp kernel for updating spray particles"""
    tid = wp.tid()
    
    if active[tid] == 0:
        return
    
    old_pos = positions[tid]
    
    # Update position
    new_pos = old_pos + velocities[tid] * dt
    positions[tid] = new_pos
    
    # Check if particle crossed the wall plane
    if old_pos[2] > wall_z and new_pos[2] <= wall_z:
        # Particle hit the wall
        hit_wall[tid] = 1
        active[tid] = 0
    elif new_pos[2] < wall_z - 0.5 or wp.length(new_pos) > 10.0:
        # Particle went too far or out of bounds
        active[tid] = 0


class SpraySimulator:
    """Main spray painting simulator"""
    def __init__(self, spray_params: SprayParameters):
        self.params = spray_params
        self.wall = WallMesh()
        
        # Warp arrays for particle simulation (CPU device)
        self.max_particles = spray_params.spray_density
        self.positions = wp.zeros(self.max_particles, dtype=wp.vec3, device=device)
        self.velocities = wp.zeros(self.max_particles, dtype=wp.vec3, device=device)
        self.active = wp.zeros(self.max_particles, dtype=int, device=device)
        self.hit_wall = wp.zeros(self.max_particles, dtype=int, device=device)
        
        # Simulation state
        self.time = 0.0
        self.frame = 0
        self.nozzle_position = np.array([-1.8, -1.2, self.params.nozzle_distance])
        self.spray_direction = np.array([0.0, 0.0, -1.0])
        
        # Create output directory
        self.output_dir = "spray_simulation_output"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f"{self.output_dir}/textures", exist_ok=True)
        os.makedirs(f"{self.output_dir}/usd", exist_ok=True)
        os.makedirs(f"{self.output_dir}/screenshots", exist_ok=True)
        
    def emit_spray(self, random_seed: int):
        """Emit spray particles from nozzle"""
        # Reset particle states
        self.active.fill_(1)
        self.hit_wall.fill_(0)
        
        # Launch emission kernel
        wp.launch(
            spray_emission_kernel,
            dim=self.max_particles,
            inputs=[
                self.positions,
                self.velocities,
                wp.vec3(self.nozzle_position),
                wp.vec3(self.spray_direction),
                self.params.spray_width,
                8.0,  # spray speed (increased)
                self.params.fan_angle,
                random_seed
            ],
            device=device
        )
        
    def update_particles(self, dt: float):
        """Update particle positions and check for wall collisions"""
        wp.launch(
            spray_update_kernel,
            dim=self.max_particles,
            inputs=[
                self.positions,
                self.velocities,
                self.active,
                self.hit_wall,
                dt,
                0.0  # wall z position
            ],
            device=device
        )
        
    def collect_paint_hits(self) -> np.ndarray:
        """Collect positions where paint hit the wall"""
        positions_numpy = self.positions.numpy()
        hit_wall_numpy = self.hit_wall.numpy()
        
        # Find particles that hit the wall
        hit_positions = []
        for i in range(len(positions_numpy)):
            if hit_wall_numpy[i] == 1:
                pos = positions_numpy[i]
                # Project position onto wall plane (z=0)
                wall_pos = np.array([pos[0], pos[1], 0.0])
                hit_positions.append(wall_pos)
        
        return np.array(hit_positions) if hit_positions else np.empty((0, 3))
    
    def move_nozzle(self, dt: float):
        """Move spray nozzle across the wall"""
        # Simple left-to-right motion
        speed = 0.8  # units per second (increased speed)
        self.nozzle_position[0] += speed * dt
        
        # Reset to left side when reaching right edge
        if self.nozzle_position[0] > 1.8:
            self.nozzle_position[0] = -1.8
            self.nozzle_position[1] += 0.4  # Move up
            
        # Reset to bottom when reaching top
        if self.nozzle_position[1] > 1.2:
            self.nozzle_position[1] = -1.2
    
    def create_usd_scene(self, filename: str):
        """Create USD scene with wall and paint texture"""
        if not USD_AVAILABLE:
            print("OpenUSD not available, skipping USD file creation")
            return
            
        try:
            # Create USD stage
            stage = Usd.Stage.CreateNew(filename)
            
            # Create wall mesh
            wall_prim = UsdGeom.Mesh.Define(stage, "/Wall")
            
            # Set mesh data
            wall_prim.CreatePointsAttr(Vt.Vec3fArray(self.wall.vertices.tolist()))
            wall_prim.CreateFaceVertexIndicesAttr(Vt.IntArray(self.wall.faces.flatten().tolist()))
            wall_prim.CreateFaceVertexCountsAttr(Vt.IntArray([3, 3]))  # Two triangles
            
            # Create UV coordinates for texture mapping - FIXED API usage
            uv_coords = [(0, 0), (1, 0), (1, 1), (0, 1)]
            # Use CreatePrimvarsAPI instead of CreatePrimvar
            primvars_api = UsdGeom.PrimvarsAPI(wall_prim)
            st_primvar = primvars_api.CreatePrimvar("st", Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.vertex)
            st_primvar.Set(uv_coords)
            
            # Create material with paint texture
            material_prim = UsdShade.Material.Define(stage, "/PaintMaterial")
            shader = UsdShade.Shader.Define(stage, "/PaintMaterial/PaintShader")
            shader.CreateIdAttr("UsdPreviewSurface")
            
            # Save current texture
            texture_filename = f"paint_{self.frame:04d}.png"
            texture_path = f"{self.output_dir}/textures/{texture_filename}"
            self.wall.save_texture(texture_path)
            
            # Create texture reader
            texture_reader = UsdShade.Shader.Define(stage, "/PaintMaterial/TextureReader")
            texture_reader.CreateIdAttr("UsdUVTexture")
            texture_reader.CreateInput("file", Sdf.ValueTypeNames.Asset).Set(texture_filename)
            
            # Connect texture to material
            shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).ConnectToSource(
                texture_reader.CreateOutput("rgb", Sdf.ValueTypeNames.Color3f)
            )
            
            # Bind material to wall
            UsdShade.MaterialBindingAPI(wall_prim).Bind(material_prim)
            
            # Create spray nozzle for visualization
            nozzle_prim = UsdGeom.Sphere.Define(stage, "/SprayNozzle")
            nozzle_prim.CreateRadiusAttr(0.05)
            
            # Set nozzle position using transform
            nozzle_xform = UsdGeom.Xformable(nozzle_prim)
            nozzle_xform.AddTranslateOp().Set(Gf.Vec3f(self.nozzle_position))
            
            # Set up camera
            camera_prim = UsdGeom.Camera.Define(stage, "/Camera")
            camera_xform = UsdGeom.Xformable(camera_prim)
            camera_xform.AddTranslateOp().Set(Gf.Vec3f(0, 0, 3))
            
            # Save stage
            stage.Save()
            print(f"Saved USD scene: {filename}")
            
        except Exception as e:
            print(f"Error creating USD scene: {e}")
            print("Continuing without USD file...")
        
    def save_progress_image(self, filename: str):
        """Save a visualization of current progress"""
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # Plot paint coverage
            ax1.imshow(self.wall.paint_coverage, cmap='Reds', origin='lower')
            ax1.set_title(f'Paint Coverage - Frame {self.frame}')
            ax1.set_xlabel('X')
            ax1.set_ylabel('Y')
            
            # Plot nozzle position and coverage stats
            ax2.scatter(self.nozzle_position[0], self.nozzle_position[1], 
                       c='blue', s=100, marker='o', label='Nozzle')
            ax2.set_xlim(-2.5, 2.5)
            ax2.set_ylim(-2, 2)
            ax2.set_title(f'Nozzle Position\nCoverage: {np.sum(self.wall.paint_coverage > 0.1) / self.wall.paint_coverage.size * 100:.1f}%')
            ax2.set_xlabel('X')
            ax2.set_ylabel('Y')
            ax2.legend()
            ax2.grid(True)
            
            plt.tight_layout()
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            plt.close()
            print(f"Saved progress image: {filename}")
            
        except Exception as e:
            print(f"Error saving progress image: {e}")
        
    def run_simulation(self, duration: float = 10.0, dt: float = 0.1):
        """Run the complete spray painting simulation"""
        print("Starting spray painting simulation...")
        print(f"Duration: {duration}s, Time step: {dt}s")
        print(f"Output directory: {self.output_dir}")
        print(f"Spray density: {self.params.spray_density} particles/frame")
        
        # Save initial state
        self.save_progress_image(f"{self.output_dir}/screenshots/progress_initial.png")
        if USD_AVAILABLE:
            self.create_usd_scene(f"{self.output_dir}/usd/scene_initial.usda")
        
        # Simulation loop
        steps = int(duration / dt)
        save_interval = max(1, steps // 10)  # Save 10 intermediate states
        
        for step in range(steps):
            self.time += dt
            self.frame = step
            
            # Print progress
            if step % 20 == 0:
                coverage_percent = np.sum(self.wall.paint_coverage > 0.1) / self.wall.paint_coverage.size * 100
                print(f"Step {step}/{steps} - Time: {self.time:.1f}s - Coverage: {coverage_percent:.1f}%")
            
            # Emit spray particles
            self.emit_spray(step * 1000)  # Different seed each frame
            
            # Update particles multiple times per frame for better collision detection
            sub_dt = dt / 5.0
            for _ in range(5):
                self.update_particles(sub_dt)
            
            # Collect paint hits and update wall
            hit_positions = self.collect_paint_hits()
            if len(hit_positions) > 0:
                self.wall.add_paint(hit_positions, self.params.paint_intensity)
                print(f"Frame {step}: {len(hit_positions)} paint hits")
            
            # Move nozzle
            self.move_nozzle(dt)
            
            # Save intermediate results
            if step % save_interval == 0 or step == steps - 1:
                print(f"Saving frame {step}/{steps}...")
                
                # Save progress image
                self.save_progress_image(f"{self.output_dir}/screenshots/progress_{step:04d}.png")
                
                # Save USD scene
                if USD_AVAILABLE:
                    self.create_usd_scene(f"{self.output_dir}/usd/scene_{step:04d}.usda")
        
        # Save final state
        self.save_progress_image(f"{self.output_dir}/screenshots/progress_final.png")
        self.wall.save_texture(f"{self.output_dir}/textures/paint_final.png")
        
        if USD_AVAILABLE:
            self.create_usd_scene(f"{self.output_dir}/usd/scene_final.usda")
        
        # Save simulation parameters
        params_dict = {
            'spray_width': self.params.spray_width,
            'spray_range': self.params.spray_range,
            'spray_density': self.params.spray_density,
            'paint_intensity': self.params.paint_intensity,
            'nozzle_distance': self.params.nozzle_distance,
            'fan_angle': self.params.fan_angle,
            'duration': duration,
            'dt': dt,
            'frames': steps,
            'device': str(device)
        }
        
        with open(f"{self.output_dir}/simulation_params.json", 'w') as f:
            json.dump(params_dict, f, indent=2)
        
        print(f"\nSimulation complete!")
        print(f"Total paint coverage: {np.sum(self.wall.paint_coverage > 0.1) / self.wall.paint_coverage.size * 100:.1f}%")
        print(f"Output saved to: {self.output_dir}")
        
        if USD_AVAILABLE:
            print("\nTo view results in usdview:")
            print(f"usdview {self.output_dir}/usd/scene_final.usda")
        
        return self.output_dir
