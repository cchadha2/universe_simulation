#!/usr/bin/env python3
"""
Universe Simulation - Main Application

A procedurally generated universe simulation with interactive GUI,
featuring stars, planets, and other celestial objects with realistic gravitational physics.
"""

import time
from universe import Universe
from gui import GUI

def main():
    """Main application entry point."""
    print("Initializing Universe Simulation...")
    
    # Create universe and GUI
    universe = Universe()
    gui = GUI()
    
    # Generate initial universe
    print("Generating universe...")
    universe.generate_universe()
    
    # Main simulation loop
    running = True
    
    print("Starting simulation...")
    print("Controls:")
    print("  Mouse: Pan around the universe")
    print("  Mouse Wheel: Zoom in/out")
    print("  Left Click: Select object")
    print("  Right Click: Center camera on object")
    print("  Space: Pause/Resume")
    print("  R: Reset universe")
    print("  G: Toggle grid")
    print("  T: Toggle trails")
    print("  I: Toggle info panel")
    print("  ESC: Quit")
    
    try:
        while running:
            # Handle events
            running, paused = gui.handle_events(universe)
            
            # Handle pause toggle
            if not running:
                break

            # Render frame
            gui.render(universe)

            # Update simulation if not paused
            if not paused:
                universe.update()
            
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user.")
    except Exception as e:
        print(f"Error during simulation: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Shutting down...")
        gui.quit()
        print("Goodbye!")

if __name__ == "__main__":
    main() 