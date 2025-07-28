# Paint Spraying Simulation

A comprehensive paint spraying simulation using Isaac Warp and OpenUSD, featuring realistic particle physics, paint accumulation tracking, and visualization capabilities.

## 🎯 Features

- **Realistic Physics**: Particle-based spray simulation using Isaac Warp
- **Paint Accumulation**: Real-time tracking of paint coverage on wall surfaces
- **Visual Output**: Progress screenshots, texture maps, and coverage analysis
- **USD Support**: Export to Universal Scene Description format for 3D viewing
- **CPU Optimized**: Designed for efficient CPU-based computation
- **Modular Design**: Clean, maintainable code structure

## 📋 Requirements

### System Requirements
- Python 3.8 or higher
- CPU-based simulation (GPU support available with modifications)
- At least 4GB RAM recommended

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

## 🚀 Installation

1. **Clone or download the project files:**
   ```bash
   # Ensure you have all three Python files in the same directory:
   # - spray_parameters.py
   # - spray_simulator.py  
   # - main.py
   ```

2. **Install dependencies:**
   ```bash
   pip install usd-core warp-lang numpy pillow matplotlib
   ```

3. **Verify installation:**
   ```bash
   python -c "import warp as wp; import numpy as np; from pxr import Usd; print('All dependencies installed successfully!')"
   ```

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

### Expected Output:
```
Paint Spraying Simulation (Modular Version - CPU Optimized)
============================================================

Simulation Configuration:
- Spray Width: 0.4
- Spray Density: 300 particles/frame
- Paint Intensity: 0.15
- Fan Angle: 20.0°
- Nozzle Distance: 0.6

Running simulation for 15.0 seconds with 0.1s time steps...
Starting spray painting simulation...
```

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

## 🔧 Configuration

### Modifying Spray Parameters

Edit the `configure_spray_parameters()` function in `main.py`:

```python
def configure_spray_parameters() -> SprayParameters:
    spray_params = SprayParameters()
    
    # Customize these values:
    spray_params.spray_width = 0.4        # Width of spray pattern
    spray_params.spray_density = 300      # Particles per frame
    spray_params.paint_intensity = 0.15   # Paint accumulation rate
    spray_params.fan_angle = 20.0         # Spray cone angle (degrees)
    spray_params.nozzle_distance = 0.6    # Distance from wall
    
    return spray_params
```

### Simulation Duration

Modify the simulation duration in `main.py`:

```python
# Run simulation with specified duration and time step
duration = 15.0  # seconds (change this value)
dt = 0.1        # time step (smaller = more accurate, slower)
```

## 📊 Output Files

### Generated Files:
- **Screenshots**: `progress_*.png` - Simulation progress visualization
- **Textures**: `paint_*.png` - Paint coverage texture maps
- **USD Files**: `scene_*.usda` - 3D scenes for viewing in USD viewers
- **Summary**: `simulation_summary.png` - Final analysis visualization
- **Parameters**: `simulation_params.json` - Complete simulation settings

### Viewing Results:

1. **Images**: Open PNG files in any image viewer
2. **USD Files**: Use `usdview` (if available):
   ```bash
   usdview spray_simulation_output/usd/scene_final.usda
   ```
3. **Summary**: Check `simulation_summary.png` for complete analysis

## 🎛️ Advanced Usage

### Custom Wall Dimensions

Modify the `WallMesh` initialization in `spray_simulator.py`:

```python
self.wall = WallMesh(width=4.0, height=3.0, resolution=128)
```

### Performance Tuning

For better performance on slower systems:
- Reduce `spray_density` (fewer particles)
- Increase `dt` (larger time steps)
- Reduce wall `resolution` (lower texture quality)

For higher quality:
- Increase `spray_density` (more particles)
- Decrease `dt` (smaller time steps)  
- Increase wall `resolution` (higher texture quality)

## 🐛 Troubleshooting

### Common Issues:

1. **ImportError: No module named 'warp'**
   ```bash
   pip install warp-lang
   ```

2. **ImportError: No module named 'pxr'**
   ```bash
   pip install usd-core
   ```

3. **Slow Performance**
   - Reduce `spray_density` in parameters
   - Increase time step `dt`
   - Lower wall resolution

4. **No Paint Visible**
   - Increase `paint_intensity`
   - Check `nozzle_distance` (should be < 1.0)
   - Verify spray parameters are reasonable

5. **Memory Issues**
   - Reduce `spray_density`
   - Lower wall `resolution`
   - Reduce simulation `duration`

### Debug Mode:

Add print statements to track simulation progress:

```python
# In spray_simulator.py, add to simulation loop:
if step % 10 == 0:
    print(f"Frame {step}: Nozzle at {self.nozzle_position}")
```

## 🔬 Technical Details

### Simulation Pipeline:
1. **Particle Emission**: Generate spray particles from nozzle position
2. **Physics Update**: Update particle positions using Warp kernels
3. **Collision Detection**: Check for wall intersections
4. **Paint Accumulation**: Add paint to wall texture at hit locations
5. **Visualization**: Generate progress images and statistics

### Key Components:
- **Warp Kernels**: GPU-style parallel computation on CPU
- **Paint Coverage**: 2D texture map tracking accumulation
- **USD Export**: Industry-standard 3D scene format
- **Real-time Visualization**: Progress tracking and analysis

## 📝 License

This project is provided as-is for educational and research purposes.

## 🤝 Contributing

Feel free to modify and extend the simulation for your needs:
- Add new spray patterns
- Implement different paint types
- Add gravity effects
- Create custom wall geometries

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all dependencies are installed correctly
3. Ensure Python version compatibility (3.8+)
4. Check system resources (RAM, CPU)

---

**Happy Painting! 🎨**
