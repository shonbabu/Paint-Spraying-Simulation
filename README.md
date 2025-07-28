# Paint Spraying Simulation

A comprehensive paint spraying simulation using Isaac Warp and OpenUSD, featuring realistic particle physics, paint accumulation tracking, and visualization capabilities.

Features

- **Realistic Physics**: Particle-based spray simulation using Isaac Warp
- **Paint Accumulation**: Real-time tracking of paint coverage on wall surfaces
- **Visual Output**: Progress screenshots, texture maps, and coverage analysis
- **USD Support**: Export to Universal Scene Description format for 3D viewing
- **CPU Optimized**: Designed for efficient CPU-based computation
- **Modular Design**: Clean, maintainable code structure



### Dependencies
```bash
pip install usd-core warp-lang numpy pillow matplotlib
```

#### Detailed Dependencies:
- **usd-core**: OpenUSD library for 3D scene creation and export
- **warp-lang**: NVIDIA's high-performance Python framework for simulation
- **numpy**: Numerical computing library
- **pillow**: Image processing library
- **matplotlib**: Plotting and visualization library


## 🏃‍♂️ Running the Simulation

### Basic Usage
```bash
python main.py
```

### What Happens When You Run:
1. **Initialization**: Sets up simulation parameters and creates output directories
2. **Simulation Loop**: Runs paint spraying simulation with particle physics
3. **Visualization**: Generates progress images and coverage analysis  
4. **Export**: Creates USD files and texture maps
5. **Summary**: Shows final statistics and output locations


## 📁 Project Structure

```
paint-spraying-simulation/
├── main.py                     # Main entry point
├── spray_parameters.py         # Configuration and wall mesh classes
├── spray_simulator.py          # Core simulation engine
├── README.md                   # This file
└── spray_simulation_output/    # Generated output directory
    ├── screenshots/            # Progress visualization images
    ├── textures/              # Paint coverage texture maps
    ├── usd/                   # USD scene files
    ├── simulation_params.json # Simulation configuration
    └── simulation_summary.png # Final results summary
```
```

## 📊 Output Files

### Generated Files:
- **Screenshots**: `progress_*.png` - Simulation progress visualization
- **Textures**: `paint_*.png` - Paint coverage texture maps
- **USD Files**: `scene_*.usda` - 3D scenes for viewing in USD viewers
- **Summary**: `simulation_summary.png` - Final analysis visualization
- **Parameters**: `simulation_params.json` - Complete simulation settings

