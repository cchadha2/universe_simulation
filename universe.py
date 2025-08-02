import random
import math
from typing import List, Tuple
from objects import Star, Planet, Asteroid, Nebula, BlackHole
from physics import PhysicsEngine
from utils import calculate_distance, random_position, random_velocity

class Universe:
    """Represents the entire universe with all celestial objects."""

    TIME_STEP = 5
    # Tunes the relative amount of objects in the universe.
    UNIVERSE_SIZE = 3000
   
    def __init__(self):
        self.objects: dict = {}
        self.physics_engine = PhysicsEngine()
        self.time = 0
        self.generation_seed = random.randint(1, 1000000)
        self.max_star_count = self.UNIVERSE_SIZE // 100
        self.max_planet_count = self.UNIVERSE_SIZE // 10
        self.max_asteroid_count = self.UNIVERSE_SIZE // 5
        self.max_nebula_count = self.UNIVERSE_SIZE // 1000
        self.max_black_hole_count = self.UNIVERSE_SIZE // 1000
        self.time_step = self.TIME_STEP
        
    def generate_universe(self):
        """Procedurally generate the entire universe."""
        random.seed(self.generation_seed)
        self.objects.clear()
        
        # Generate stars
        self._generate_stars()
        
        # Generate planets (some orbiting stars)
        self._generate_planets()
        
        # Generate asteroids
        self._generate_asteroids()
        
        # Generate nebulae
        self._generate_nebulae()
        
        # Generate black holes
        self._generate_black_holes()
        
        # Set up some stable orbits
        self._setup_stable_orbits()
        
        print(f"Generated universe with {len(self.objects)} objects")
    
    def _generate_stars(self):
        """Generate stars throughout the universe."""
        for i in range(random.randint(1, self.max_star_count)):
            name = f"Star-{i+1:03d}"
            position = random_position()
            velocity = random_velocity()
            
            star = Star(name, position, velocity)
            self.objects[star.name] = star
    
    def _generate_planets(self):
        """Generate planets, some orbiting stars."""
        for i in range(random.randint(1, self.max_planet_count)):
            name = f"Planet-{i+1:03d}"
            
            # 70% chance to orbit a nearby star
            if random.random() < 0.7 and len([obj for obj in self.objects if isinstance(obj, Star)]) > 0:
                # Find a nearby star
                stars = [obj for obj in self.objects if isinstance(obj, Star)]
                parent_star = random.choice(stars)
                
                # Position planet near the star
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(50, 300)
                position = (
                    parent_star.position[0] + distance * math.cos(angle),
                    parent_star.position[1] + distance * math.sin(angle)
                )
                
                # Calculate orbital velocity
                orbital_velocity = self.physics_engine.calculate_orbital_velocity(parent_star.mass, distance)
                velocity = (
                    parent_star.velocity[0] - orbital_velocity * math.sin(angle),
                    parent_star.velocity[1] + orbital_velocity * math.cos(angle)
                )
                
                planet = Planet(name, position, velocity, parent_star)
            else:
                # Free-floating planet
                position = random_position()
                velocity = random_velocity()
                planet = Planet(name, position, velocity)
            
            self.objects[planet.name] = planet
    
    def _generate_asteroids(self):
        """Generate asteroids throughout the universe."""
        for i in range(random.randint(1, self.max_asteroid_count)):
            name = f"Asteroid-{i+1:03d}"
            position = random_position()
            velocity = random_velocity()
            
            asteroid = Asteroid(name, position, velocity)
            self.objects[asteroid.name] = asteroid

    def _generate_nebulae(self):
        """Generate nebulae in the universe."""
        for i in range(self.max_nebula_count):
            name = f"Nebula-{i+1:02d}"
            position = random_position()
            velocity = random_velocity()
            
            nebula = Nebula(name, position, velocity)
            self.objects[nebula.name] = nebula
    
    def _generate_black_holes(self):
        """Generate a few black holes."""
        black_hole_count = random.randint(1, self.max_black_hole_count)
        for i in range(black_hole_count):
            name = f"BlackHole-{i+1:02d}"
            position = random_position()
            velocity = (0, 0)
            
            black_hole = BlackHole(name, position, velocity)
            self.objects[black_hole.name] = black_hole
    
    def _setup_stable_orbits(self):
        """Set up some stable orbits for planets around stars."""
        planets = [obj for obj in self.objects if isinstance(obj, Planet) and obj.parent_star is not None]
        
        for planet in planets:
            if planet.parent_star:
                # Calculate distance to parent star
                distance = calculate_distance(planet.position, planet.parent_star.position)
                
                # Set up stable orbit
                self.physics_engine.create_stable_orbit(planet.parent_star, planet, distance)
    
    def update(self):
        """Update the universe for one time step."""
        # Calculate gravitational forces
        self.physics_engine.calculate_gravitational_forces(self.objects.values())
        
        # Update object positions and velocities
        self.physics_engine.update_objects(self.objects.values(), self.time_step)
        
        # Check for collisions
        collisions = self.physics_engine.check_collisions(self.objects.values())
        
        # Handle collisions by removing the smaller object
        objects_to_remove = []
        for obj1, obj2 in collisions:
            obj_to_remove = self.physics_engine.handle_collision(obj1, obj2)
            if obj_to_remove:
                objects_to_remove.append(obj_to_remove)

        for obj in objects_to_remove:
            if self.objects.get(obj.name):
                self.objects.pop(obj.name)
               
        self.time += self.time_step

    def increase_time_step(self):
        self.time_step += 5

    def decrease_time_step(self):
        self.time_step -= 5
    
    def get_nearest_object(self, position: Tuple[float, float]) -> Tuple:
        """Get the nearest object to a position."""
        from utils import calculate_distance
        
        nearest_obj = None
        min_distance = float('inf')
        
        for obj in self.objects.values():
            distance = calculate_distance(position, obj.position)
            if distance < min_distance:
                min_distance = distance
                nearest_obj = obj
        
        return nearest_obj, min_distance
    
    def get_object_info(self, obj) -> dict:
        """Get detailed information about an object."""
        info = {
            'name': obj.name,
            'type': type(obj).__name__,
            'mass': f"{obj.mass:.2e} kg",
            'position': f"({obj.position[0]:.1f}, {obj.position[1]:.1f})",
            'velocity': f"({obj.velocity[0]:.1f}, {obj.velocity[1]:.1f})",
            'speed': f"{math.sqrt(obj.velocity[0]**2 + obj.velocity[1]**2):.1f} m/s"
        }
        
        if isinstance(obj, Star):
            info.update({
                'luminosity': f"{obj.luminosity:.2f} solar luminosities",
                'temperature': f"{obj.temperature:.0f} K",
                'age': f"{obj.age:.2e} years"
            })
        elif isinstance(obj, Planet):
            info.update({
                'atmosphere': obj.atmosphere,
                'water': obj.water,
                'temperature': f"{obj.temperature:.0f} K"
            })
        elif isinstance(obj, Asteroid):
            info.update({
                'composition': obj.composition
            })
        elif isinstance(obj, Nebula):
            info.update({
                'density': f"{obj.density:.2f}"
            })
        elif isinstance(obj, BlackHole):
            info.update({
                'event_horizon_radius': obj.event_horizon_radius
            })
        
        return info
    
    def reset(self):
        """Reset the universe with new generation."""
        self.generation_seed = random.randint(1, 1000000)
        self.time = 0
        self.generate_universe()
    
    def get_statistics(self) -> dict:
        """Get universe statistics."""
        stats = {
            'total_objects': len(self.objects.values()),
            'stars': len([obj for obj in self.objects.values() if isinstance(obj, Star)]),
            'planets': len([obj for obj in self.objects.values() if isinstance(obj, Planet)]),
            'asteroids': len([obj for obj in self.objects.values() if isinstance(obj, Asteroid)]),
            'nebulae': len([obj for obj in self.objects.values() if isinstance(obj, Nebula)]),
            'black_holes': len([obj for obj in self.objects.values() if isinstance(obj, BlackHole)]),
            'time': f"{self.time} years",
            'time_step': f"{self.time_step} years"
        }
        
        return stats 