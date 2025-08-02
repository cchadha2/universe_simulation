# Universe Simulation

A procedurally generated universe simulation with interactive GUI, featuring stars, planets, and other celestial objects with realistic gravitational physics.

https://github.com/user-attachments/assets/f35ad07c-166d-433e-ba84-ee07f995e215

## Features

- **Procedural Generation**: Randomly generates stars, planets, asteroids, and other celestial objects
- **Physics Engine**: Realistic gravitational calculations and orbital mechanics
- **Interactive GUI**: Zoom in/out, pan around the universe, and examine objects
- **Real-time Simulation**: Watch celestial bodies orbit and interact with each other

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the simulation:
```bash
python main.py
```

## Controls

- **Mouse**: Click and drag to pan around the universe
- **Mouse Wheel**: Zoom in/out
- **Space**: Pause/resume simulation
- **R**: Reset the universe with new procedural generation
- **ESC**: Quit the application

## Project Structure

- `main.py`: Main application entry point
- `physics.py`: Physics engine for gravitational calculations
- `universe.py`: Universe generation and management
- `objects.py`: Celestial object classes (stars, planets, etc.)
- `gui.py`: Graphical user interface
- `utils.py`: Utility functions and constants 
