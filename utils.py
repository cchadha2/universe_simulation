import math
import pygame
from typing import Tuple, List

# Color definitions
COLORS = {
    'star': (255, 255, 0),      # Yellow
    'planet': (0, 100, 255),    # Blue
    'asteroid': (128, 128, 128), # Gray
    'nebula': (255, 100, 255),  # Pink
    'black_hole': (20, 20, 20),    # Dark gray
    'background': (0, 0, 0),   # Black
    'grid': (50, 50, 50),       # Dark gray
    'text': (255, 255, 255),    # White
}

def calculate_distance(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
    """Calculate the distance between two positions."""
    dx = pos1[0] - pos2[0]
    dy = pos1[1] - pos2[1]
    return math.sqrt(dx**2 + dy**2)

def world_to_screen(world_pos: Tuple[float, float], camera_pos: Tuple[float, float], zoom: float, screen_size: Tuple[int, int]) -> Tuple[int, int]:
    """Convert world coordinates to screen coordinates."""
    screen_x = (world_pos[0] - camera_pos[0]) * zoom + screen_size[0] // 2
    screen_y = (world_pos[1] - camera_pos[1]) * zoom + screen_size[1] // 2
    return (int(screen_x), int(screen_y))

def screen_to_world(screen_pos: Tuple[int, int], camera_pos: Tuple[float, float], zoom: float, screen_size: Tuple[int, int]) -> Tuple[float, float]:
    """Convert screen coordinates to world coordinates."""
    world_x = (screen_pos[0] - screen_size[0] // 2) / zoom + camera_pos[0]
    world_y = (screen_pos[1] - screen_size[1] // 2) / zoom + camera_pos[1]
    return (world_x, world_y)

def draw_text(surface: pygame.Surface, text: str, font: pygame.font.Font, color: Tuple[int, int, int], pos: Tuple[int, int]):
    """Draw text on the surface."""
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, pos)

def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value between min and max."""
    return max(min_val, min(value, max_val)) 