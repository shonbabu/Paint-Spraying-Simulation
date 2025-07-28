#!/usr/bin/env python3
"""
Main Script for Paint Spraying Simulation
=========================================

This script runs the complete paint spraying simulation using modular components.

Dependencies:
- pip install usd-core warp-lang numpy pillow matplotlib

Usage:
    python main.py
"""

import os
import matplotlib.pyplot as plt
from spray_parameters import SprayParameters
from spray_simulator import SpraySimulator


def create_summary_visualization(simulator: SpraySimulator, output_dir: str):
    """Create a summary visualization of the simulation results"""
    try:
        print("\nCreating summary visualization...")
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Load and display key frames
        initial_path = f"{output_dir}/screenshots/progress_initial.png"
        final_path = f"{output_dir}/screenshots/progress_final.png"
        
        if os.path.exists(initial_path) and os.path.exists(final_path):
            initial_img = plt.imread(initial_path)
            final_img = plt.imread(final_path)
            
            axes[0, 0].imshow(initial_img)
            axes[0, 0].set_title('Initial State')
            axes[0, 0].axis('off')
            
            axes[0, 1].imshow(final_img)
            axes[0, 1].set_title('Final State')
            axes[0, 1].axis('off')
        
        # Paint coverage analysis
        axes[1, 0].imshow(simulator.wall.paint_coverage, cmap='Reds', origin='lower')
        axes[1, 0].set_title('Final Paint Coverage')
        axes[1, 0].set_xlabel('X')
        axes[1, 0].set_ylabel('Y')
        
        # Coverage histogram
        coverage_flat = simulator.wall.paint_coverage.flatten()
        painted_areas = coverage_flat[coverage_flat > 0]
        if len(painted_areas) > 0:
            axes[1, 1].hist(painted_areas, bins=50, alpha=0.7, color='red')
            axes[1, 1].set_title('Paint Coverage Distribution')
            axes[1, 1].set_xlabel('Coverage Level')
            axes[1, 1].set_ylabel('Frequency')
        else:
            axes[1, 1].text(0.5, 0.5, 'No paint detected', ha='center', va='center')
            axes[1, 1].set_title('Paint Coverage Distribution')
        
        plt.tight_layout()
        summary_path = f"{output_dir}/simulation_summary.png"
        plt.savefig(summary_path, dpi=150, bbox_inches='tight')
        print(f"Summary saved: {summary_path}")
        plt.close()
        
    except Exception as e:
        print(f"Could not create summary visualization: {e}")


def configure_spray_parameters() -> SprayParameters:
    """Configure and return optimized spray parameters"""
    spray_params = SprayParameters()
    
    # Optimize parameters for CPU performance
    spray_params.spray_width = 0.4
    spray_params.spray_density = 300  # Reduced for CPU performance
    spray_params.paint_intensity = 0.15  # Increased for better visibility
    spray_params.fan_angle = 20.0  # Reduced for more focused spray
    spray_params.nozzle_distance = 0.6  # Closer to wall
    
    return spray_params


def print_results_summary(output_dir: str):
    """Print a summary of simulation results and output locations"""
    print(f"\nSimulation Results:")
    print(f"- Screenshots: {output_dir}/screenshots/")
    print(f"- Textures: {output_dir}/textures/")
    print(f"- USD files: {output_dir}/usd/")
    print(f"- Parameters: {output_dir}/simulation_params.json")
    print(f"- Summary: {output_dir}/simulation_summary.png")


def main():
    """Main function to run the spray painting simulation"""
    print("Paint Spraying Simulation (Modular Version - CPU Optimized)")
    print("=" * 60)
    
    # Configure spray parameters
    spray_params = configure_spray_parameters()
    
    # Print configuration
    print(f"\nSimulation Configuration:")
    print(f"- Spray Width: {spray_params.spray_width}")
    print(f"- Spray Density: {spray_params.spray_density} particles/frame")
    print(f"- Paint Intensity: {spray_params.paint_intensity}")
    print(f"- Fan Angle: {spray_params.fan_angle}°")
    print(f"- Nozzle Distance: {spray_params.nozzle_distance}")
    
    # Create and run simulator
    simulator = SpraySimulator(spray_params)
    
    # Run simulation with specified duration and time step
    duration = 15.0  # seconds
    dt = 0.1  # time step
    
    print(f"\nRunning simulation for {duration} seconds with {dt}s time steps...")
    output_dir = simulator.run_simulation(duration=duration, dt=dt)
    
    # Create summary visualization
    create_summary_visualization(simulator, output_dir)
    
    # Print results summary
    print_results_summary(output_dir)
    
    # Final statistics
    total_coverage = simulator.wall.paint_coverage.sum()
    coverage_percentage = (simulator.wall.paint_coverage > 0.1).sum() / simulator.wall.paint_coverage.size * 100
    
    print(f"\nFinal Statistics:")
    print(f"- Total Paint Accumulation: {total_coverage:.2f}")
    print(f"- Wall Coverage: {coverage_percentage:.1f}%")
    print(f"- Simulation Frames: {simulator.frame + 1}")
    print(f"- Total Simulation Time: {simulator.time:.1f}s")
    
    print("\nSimulation completed successfully!")
    print("Check the output directory for all generated files.")


if __name__ == "__main__":
    main()
