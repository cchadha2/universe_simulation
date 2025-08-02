import logging
import math
from typing import List 
from utils import calculate_distance
from objects import CelestialObject

logger = logging.getLogger(__name__)

class PhysicsEngine:
    """Physics engine for gravitational calculations and orbital mechanics."""

    # Scales down force applied for gravity calculation
    FORCE_CONSTANT = 1*10e-11

    G = 6.67430e-15  # Much smaller gravitational constant for stability
    
    def __init__(self):
        self.gravity_enabled = True
        self.collision_detection = True
        
    def calculate_gravitational_forces(self, objects: List[CelestialObject]):
        """Calculate gravitational forces between all objects."""
        if not self.gravity_enabled:
            return
            
        # Reset all forces
        for obj in objects:
            obj.reset_force()
        
        # Calculate gravitational forces between all pairs
        for i, obj1 in enumerate(objects):
            for j, obj2 in enumerate(objects):
                if i != j and obj1.mass > 0 and obj2.mass > 0:
                    distance = calculate_distance(obj1.position, obj2.position)
                    
                    if distance > 0:
                        # Calculate gravitational force
                        force_magnitude = self.calculate_gravitational_force(obj1.mass, obj2.mass, distance)
                        
                        # Calculate force direction
                        dx = obj2.position[0] - obj1.position[0]
                        dy = obj2.position[1] - obj1.position[1]
                        
                        # Normalize direction vector
                        length = math.sqrt(dx*dx + dy*dy)
                        if length > 0:
                            dx /= length
                            dy /= length
                            
                            # Apply force to both objects (equal and opposite)
                            force_x = force_magnitude * dx * self.FORCE_CONSTANT
                            force_y = force_magnitude * dy * self.FORCE_CONSTANT
                            
                            obj1.add_force(force_x, force_y)
                            obj2.add_force(-force_x, -force_y)

    def calculate_gravitational_force(self, mass1: float, mass2: float, distance: float) -> float:
        """Calculate gravitational force between two objects."""
        if distance == 0:
            return 0
        return self.G * mass1 * mass2 / (distance * distance)
    
    def update_objects(self, objects: List[CelestialObject], time_step):
        """Update positions and velocities of all objects."""
        dt = time_step
        
        # Update velocities based on forces
        for obj in objects:
            obj.update_velocity(dt)
        
        # Update positions based on velocities
        for obj in objects:
            obj.update_position(dt)
            
    def check_collisions(self, objects: List[CelestialObject]):
        """Check for collisions between objects."""
        if not self.collision_detection:
            return
            
        collisions = []
        
        for i, obj1 in enumerate(objects):
            for j, obj2 in enumerate(objects):
                if i < j:  # Avoid checking same pair twice
                    distance = calculate_distance(obj1.position, obj2.position)
                    collision_threshold = obj1.size + obj2.size
                    
                    if distance < collision_threshold:
                        collisions.append((obj1, obj2))
        
        return collisions
    
    def handle_collision(self, obj1: CelestialObject, obj2: CelestialObject):
        """Handle collision between two objects."""
        # Determine which object to remove (the smaller one)
        smaller_object = obj2 if obj1.mass >= obj2.mass else obj1
        print(f"Handling collision between {obj1.name} and {obj2.name}. Removing {smaller_object.name}")
        return smaller_object

    def calculate_orbital_velocity(self, central_mass: float, distance: float) -> float:
        """Calculate orbital velocity for a circular orbit."""
        if distance <= 0 or central_mass <= 0:
            return 0
        return math.sqrt(self.G * central_mass / distance)
    
    def create_stable_orbit(self, central_object: CelestialObject, 
                           orbiting_object: CelestialObject, 
                           orbital_distance: float):
        """Set up a stable circular orbit around a central object."""
        if central_object.mass <= 0 or orbital_distance <= 0:
            return
            
        # Calculate orbital velocity
        orbital_velocity = self.calculate_orbital_velocity(central_object.mass, orbital_distance)
        
        # Position the orbiting object at the specified distance
        angle = math.atan2(orbiting_object.position[1] - central_object.position[1],
                          orbiting_object.position[0] - central_object.position[0])
        
        orbiting_object.position[0] = central_object.position[0] + orbital_distance * math.cos(angle)
        orbiting_object.position[1] = central_object.position[1] + orbital_distance * math.sin(angle)
        
        # Set velocity for circular orbit (perpendicular to position vector)
        orbiting_object.velocity[0] = central_object.velocity[0] - orbital_velocity * math.sin(angle)
        orbiting_object.velocity[1] = central_object.velocity[1] + orbital_velocity * math.cos(angle)
