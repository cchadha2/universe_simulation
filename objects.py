import random
import pygame
from typing import Tuple, List
from utils import COLORS

class CelestialObject:
    """Base class for all celestial objects."""

    SOLAR_MASS = 2e30
    
    def __init__(self, name: str, mass: float, position: Tuple[float, float], 
                 velocity: Tuple[float, float], color: Tuple[int, int, int], size: int):
        self.name = name
        self.mass = mass
        self.position = list(position)
        self.velocity = list(velocity)
        self.color = color
        self.size = size
        self.force = [0.0, 0.0]  # Current gravitational force
        self.trail = []  # Position history for trail effect
        self.max_trail_length = 50
        
    def update_position(self, dt: float):
        """Update position based on velocity."""
        self.position[0] += self.velocity[0] * dt
        self.position[1] += self.velocity[1] * dt
        
        # Add current position to trail
        self.trail.append(tuple(self.position))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
    
    def update_velocity(self, dt: float):
        """Update velocity based on gravitational force."""
        if self.mass > 0 and not isinstance(self, BlackHole):
            acceleration_x = self.force[0] / self.mass
            acceleration_y = self.force[1] / self.mass
            self.velocity[0] += acceleration_x * dt
            self.velocity[1] += acceleration_y * dt
    
    def reset_force(self):
        """Reset gravitational force to zero."""
        self.force = [0.0, 0.0]
    
    def add_force(self, force_x: float, force_y: float):
        """Add gravitational force to the object."""
        self.force[0] += force_x
        self.force[1] += force_y
    
    def draw(self, surface: pygame.Surface, camera_pos: Tuple[float, float], 
             zoom: float, screen_size: Tuple[int, int]):
        """Draw the object on the screen."""
        from utils import world_to_screen
        
        # Draw trail
        if len(self.trail) > 1:
            trail_points = []
            for trail_pos in self.trail:
                screen_pos = world_to_screen(trail_pos, camera_pos, zoom, screen_size)
                trail_points.append(screen_pos)
            
            if len(trail_points) > 1:
                pygame.draw.lines(surface, self.color, False, trail_points, 1)
        
        # Draw object
        screen_pos = world_to_screen(self.position, camera_pos, zoom, screen_size)
        radius = max(1, int(self.size * zoom))
        pygame.draw.circle(surface, self.color, screen_pos, radius)

class Star(CelestialObject):
    """A star object with high mass and luminosity."""

    def __init__(self, name: str, position: Tuple[float, float], velocity: Tuple[float, float]):
        mass = random.uniform(0.5 * self.SOLAR_MASS, 10 * self.SOLAR_MASS)  
        size = random.randint(15, 30)  # Larger stars
        super().__init__(name, mass, position, velocity, COLORS['star'], size)
        self.luminosity = mass / 1e30  # Relative to solar luminosity
        self.temperature = random.uniform(3000, 50000)  # Kelvin
        self.age = random.uniform(0, 1e10)  # Years
        
    def draw(self, surface: pygame.Surface, camera_pos: Tuple[float, float], 
             zoom: float, screen_size: Tuple[int, int]):
        """Draw star with glow effect."""
        from utils import world_to_screen
        
        screen_pos = world_to_screen(self.position, camera_pos, zoom, screen_size)
        radius = max(2, int(self.size * zoom))
        
        # Draw glow effect
        glow_radius = radius * 2
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        for i in range(glow_radius):
            alpha = int(100 * (1 - i / glow_radius))
            color = (*self.color, alpha)
            pygame.draw.circle(glow_surface, color, (glow_radius, glow_radius), glow_radius - i)
        
        surface.blit(glow_surface, (screen_pos[0] - glow_radius, screen_pos[1] - glow_radius))
        
        # Draw core
        pygame.draw.circle(surface, self.color, screen_pos, radius)

class Planet(CelestialObject):
    """A planet object orbiting a star."""

    MERCURY_MASS = 0.33e24
    JUPITER_MASS = 1898e24

    MERCURY_DIAMETER = 4879 // 2000
    JUPITER_DIAMETER = 142_984 // 2000
    
    def __init__(self, name: str, position: Tuple[float, float], velocity: Tuple[float, float], 
                 parent_star: Star = None):
        mass = random.uniform(self.MERCURY_MASS - 2000, self.JUPITER_MASS + 2000)
        size = random.randint(self.MERCURY_DIAMETER - 2000, self.JUPITER_DIAMETER + 2000)
        super().__init__(name, mass, position, velocity, COLORS['planet'], size)
        self.parent_star = parent_star
        self.atmosphere = random.choice([True, False])
        self.water = random.choice([True, False])
        self.temperature = random.uniform(200, 400)  # Kelvin
        
    def draw(self, surface: pygame.Surface, camera_pos: Tuple[float, float], 
             zoom: float, screen_size: Tuple[int, int]):
        """Draw planet with atmosphere ring if applicable."""
        from utils import world_to_screen
        
        screen_pos = world_to_screen(self.position, camera_pos, zoom, screen_size)
        radius = max(1, int(self.size * zoom))
        
        # Draw atmosphere ring
        if self.atmosphere:
            atmosphere_radius = radius + 2
            pygame.draw.circle(surface, (100, 150, 255, 50), screen_pos, atmosphere_radius, 1)
        
        # Draw planet
        pygame.draw.circle(surface, self.color, screen_pos, radius)
        
        # Draw water indicator
        if self.water:
            water_radius = max(1, radius // 2)
            pygame.draw.circle(surface, (0, 200, 255), screen_pos, water_radius)

class Asteroid(CelestialObject):
    """A small asteroid object."""
    
    def __init__(self, name: str, position: Tuple[float, float], velocity: Tuple[float, float]):
        mass = random.uniform(1e12, 1e15)  
        size = random.randint(2, 5)  # Larger asteroids
        super().__init__(name, mass, position, velocity, COLORS['asteroid'], size)
        self.composition = random.choice(['rock', 'ice', 'metal'])
        self.max_trail_length = 20  # Shorter trail for asteroids

class Nebula(CelestialObject):
    """A nebula - cloud of gas and dust."""
    
    def __init__(self, name: str, position: Tuple[float, float], velocity: Tuple[float, float]):
        mass = random.uniform(1e22, 1e24)  
        size = random.randint(20, 50)
        super().__init__(name, mass, position, velocity, COLORS['nebula'], size)
        self.density = random.uniform(0.1, 1.0)
        self.max_trail_length = 10  # Very short trail
        
    def draw(self, surface: pygame.Surface, camera_pos: Tuple[float, float], 
             zoom: float, screen_size: Tuple[int, int]):
        """Draw nebula as a cloud-like structure."""
        from utils import world_to_screen
        
        screen_pos = world_to_screen(self.position, camera_pos, zoom, screen_size)
        radius = max(5, int(self.size * zoom))
        
        # Draw multiple overlapping circles for cloud effect
        for i in range(5):
            offset_x = random.randint(-radius//3, radius//3)
            offset_y = random.randint(-radius//3, radius//3)
            cloud_radius = random.randint(radius//2, radius)
            alpha = random.randint(50, 150)
            
            cloud_surface = pygame.Surface((cloud_radius * 2, cloud_radius * 2), pygame.SRCALPHA)
            cloud_color = (*self.color, alpha)
            pygame.draw.circle(cloud_surface, cloud_color, (cloud_radius, cloud_radius), cloud_radius)
            
            surface.blit(cloud_surface, (screen_pos[0] - cloud_radius + offset_x, 
                                       screen_pos[1] - cloud_radius + offset_y))

class BlackHole(CelestialObject):
    """A black hole with extreme gravitational pull."""
    
    def __init__(self, name: str, position: Tuple[float, float], velocity: Tuple[float, float]):
        mass = random.uniform(self.SOLAR_MASS, 10e4 * self.SOLAR_MASS)  
        size = random.randint(5, 15)
        super().__init__(name, mass, position, velocity, COLORS['black_hole'], size)
        self.event_horizon_radius = size * 2
        
    def draw(self, surface: pygame.Surface, camera_pos: Tuple[float, float], 
             zoom: float, screen_size: Tuple[int, int]):
        """Draw black hole with event horizon."""
        from utils import world_to_screen
        
        screen_pos = world_to_screen(self.position, camera_pos, zoom, screen_size)
        radius = max(2, int(self.size * zoom))
        event_horizon_radius = max(4, int(self.event_horizon_radius * zoom))
        
        # Draw event horizon
        pygame.draw.circle(surface, (50, 50, 50), screen_pos, event_horizon_radius, 2)
        
        # Draw black hole core
        pygame.draw.circle(surface, self.color, screen_pos, radius)
        
        # Draw accretion disk
        disk_radius = event_horizon_radius + 5
        pygame.draw.circle(surface, (255, 100, 0), screen_pos, disk_radius, 1) 