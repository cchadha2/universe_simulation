import pygame
import math
from typing import Tuple, Optional
from utils import COLORS, world_to_screen, screen_to_world, draw_text, clamp

class GUI:
    """Graphical user interface for the universe simulation."""
    
    def __init__(self, screen_size: Tuple[int, int] = (1200, 800)):
        pygame.init()
        self.screen_size = screen_size
        self.screen = pygame.display.set_mode(screen_size)
        pygame.display.set_caption("Universe Simulation")
        
        # Camera settings
        self.camera_pos = [0.0, 0.0]
        self.zoom = 0.1  # Start with a good zoom level to see objects
        self.min_zoom = 0.05
        self.max_zoom = 10  # Limit max zoom to prevent objects going off-screen
        
        # UI settings
        self.font_small = pygame.font.Font(None, 24)
        self.font_large = pygame.font.Font(None, 36)
        self.font_title = pygame.font.Font(None, 48)
        
        # Interaction settings
        self.dragging = False
        self.drag_start = None
        self.selected_object = None
        self.show_info = False
        self.show_grid = False
        self.show_trails = True
        self.paused = False
        
        # Performance settings
        self.max_visible_objects = 1000
        
    def handle_events(self, universe):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False, False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    universe.reset()
                elif event.key == pygame.K_v:  # Reset view
                    self.reset_view()
                elif event.key == pygame.K_g:
                    self.show_grid = not self.show_grid
                elif event.key == pygame.K_t:
                    self.show_trails = not self.show_trails
                elif event.key == pygame.K_i:
                    self.show_info = not self.show_info
                elif event.key == pygame.K_2:
                    universe.increase_time_step()
                elif event.key == pygame.K_1:
                    universe.decrease_time_step()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.handle_left_click(event.pos, universe)
                elif event.button == 3:  # Right click
                    # Start right-click drag for camera movement
                    self.dragging = True
                    self.drag_start = event.pos
                elif event.button == 4:  # Mouse wheel up
                    self.zoom_in(event.pos)
                elif event.button == 5:  # Mouse wheel down
                    self.zoom_out(event.pos)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:
                    self.dragging = False
                    self.drag_start = None
            
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging and self.drag_start:
                    self.handle_right_drag(event.pos)
        
        return True, self.paused
    
    def handle_left_click(self, pos: Tuple[int, int], universe):
        """Handle left mouse click for object selection."""
        world_pos = screen_to_world(pos, self.camera_pos, self.zoom, self.screen_size)
        nearest_obj, distance = universe.get_nearest_object(world_pos)
        
        # Select object if it's close enough (within 50 pixels on screen)
        screen_distance = distance * self.zoom
        if nearest_obj and screen_distance < 50:
            self.selected_object = nearest_obj
            self.show_info = True
        else:
            self.selected_object = None
            self.show_info = False
    
    def handle_right_drag(self, pos: Tuple[int, int]):
        """Handle right mouse drag for camera movement."""
        if self.drag_start:
            # Calculate the difference in screen coordinates
            dx = self.drag_start[0] - pos[0]
            dy = self.drag_start[1] - pos[1]
            
            # Convert screen difference to world coordinates
            world_dx = dx / self.zoom
            world_dy = dy / self.zoom
            
            # Move camera in the opposite direction of the drag
            self.camera_pos[0] += world_dx
            self.camera_pos[1] += world_dy
            
            # Update drag start position
            self.drag_start = pos
    
    def reset_view(self):
        """Reset camera to default view."""
        self.camera_pos = [0.0, 0.0]
        self.zoom = 0.05
    
    def zoom_in(self, center_pos: Tuple[int, int]):
        """Zoom in towards the mouse position."""
        old_zoom = self.zoom
        self.zoom = clamp(self.zoom * 1.2, self.min_zoom, self.max_zoom)
        
        # Adjust camera to keep zoom centered on mouse
        zoom_factor = self.zoom / old_zoom
        world_center = screen_to_world(center_pos, self.camera_pos, old_zoom, self.screen_size)
        new_world_center = screen_to_world(center_pos, self.camera_pos, self.zoom, self.screen_size)
        
        self.camera_pos[0] += new_world_center[0] - world_center[0]
        self.camera_pos[1] += new_world_center[1] - world_center[1]
    
    def zoom_out(self, center_pos: Tuple[int, int]):
        """Zoom out from the mouse position."""
        old_zoom = self.zoom
        self.zoom = clamp(self.zoom / 1.2, self.min_zoom, self.max_zoom)
        
        # Adjust camera to keep zoom centered on mouse
        zoom_factor = self.zoom / old_zoom
        world_center = screen_to_world(center_pos, self.camera_pos, old_zoom, self.screen_size)
        new_world_center = screen_to_world(center_pos, self.camera_pos, self.zoom, self.screen_size)
        
        self.camera_pos[0] += new_world_center[0] - world_center[0]
        self.camera_pos[1] += new_world_center[1] - world_center[1]
    
    def draw_grid(self):
        """Draw a grid on the screen."""
        if not self.show_grid:
            return
        
        # Calculate grid spacing based on zoom
        grid_spacing = max(50, int(100 / self.zoom))
        
        # Draw vertical lines
        for x in range(0, self.screen_size[0], grid_spacing):
            pygame.draw.line(self.screen, COLORS['grid'], (x, 0), (x, self.screen_size[1]), 1)
        
        # Draw horizontal lines
        for y in range(0, self.screen_size[1], grid_spacing):
            pygame.draw.line(self.screen, COLORS['grid'], (0, y), (self.screen_size[0], y), 1)
    
    def draw_objects(self, universe):
        """Draw all visible objects."""
        # Sort objects by distance from camera (for proper layering)
        visible_objects = []
        total_objects = len(universe.objects.values())
        
        for obj in universe.objects.values():
            screen_pos = world_to_screen(obj.position, self.camera_pos, self.zoom, self.screen_size)
            
            # Check if visible
            if (0 <= screen_pos[0] <= self.screen_size[0] and 0 <= screen_pos[1] <= self.screen_size[1]):
                visible_objects.append(obj)
       
        # Limit number of visible objects for performance
        if len(visible_objects) > self.max_visible_objects:
            visible_objects = visible_objects[:self.max_visible_objects]
        
        # Draw objects
        for obj in visible_objects:
            if self.show_trails:
                obj.draw(self.screen, self.camera_pos, self.zoom, self.screen_size)
            else:
                # Draw without trails
                screen_pos = world_to_screen(obj.position, self.camera_pos, self.zoom, self.screen_size)
                radius = max(2, int(obj.size * self.zoom))  # Minimum radius of 2 pixels
                pygame.draw.circle(self.screen, obj.color, screen_pos, radius)
        
        # Highlight selected object
        if self.selected_object:
            screen_pos = world_to_screen(self.selected_object.position, self.camera_pos, self.zoom, self.screen_size)
            radius = max(3, int(self.selected_object.size * self.zoom) + 2)
            pygame.draw.circle(self.screen, (255, 255, 255), screen_pos, radius, 2)
        
        # Debug info
        debug_text = f"Total objects: {total_objects}, Visible: {len(visible_objects)}"
        draw_text(self.screen, debug_text, self.font_small, (255, 255, 0), (10, self.screen_size[1] - 30))
    
    def draw_ui(self, universe, paused: bool):
        """Draw user interface elements."""
        # Draw title
        title_text = "Universe Simulation"
        draw_text(self.screen, title_text, self.font_title, COLORS['text'], (10, 10))
        
        # Draw statistics
        stats = universe.get_statistics()
        y_offset = 60
        for key, value in stats.items():
            text = f"{key.replace('_', ' ').title()}: {value}"
            draw_text(self.screen, text, self.font_small, COLORS['text'], (10, y_offset))
            y_offset += 25
        
        # Draw camera info
        camera_text = f"Camera: ({self.camera_pos[0]:.1f}, {self.camera_pos[1]:.1f})"
        draw_text(self.screen, camera_text, self.font_small, COLORS['text'], (10, y_offset))
        y_offset += 25
        
        zoom_text = f"Zoom: {self.zoom:.2f}x"
        draw_text(self.screen, zoom_text, self.font_small, COLORS['text'], (10, y_offset))
        y_offset += 25
        
        # Draw pause indicator
        if paused:
            pause_text = "PAUSED"
            draw_text(self.screen, pause_text, self.font_large, (255, 0, 0), (10, y_offset))
            y_offset += 40
        
        # Draw controls
        controls = [
            "Controls:",
            "Left Click: View Object Stats",
            "Right Drag: Move Camera",
            "Wheel: Zoom",
            "Space: Pause/Resume",
            "R: Reset Universe",
            "V: Reset View",
            "G: Toggle Grid",
            "T: Toggle Trails",
            "I: Toggle Object Stats",
            "ESC: Quit"
        ]
        
        for i, control in enumerate(controls):
            color = COLORS['text'] if i == 0 else (200, 200, 200)
            draw_text(self.screen, control, self.font_small, color, 
                     (self.screen_size[0] - 250, 10 + i * 20))
        
        # Draw selected object info
        if self.selected_object and self.show_info:
            self.draw_object_info(universe)
    
    def draw_object_info(self, universe):
        """Draw detailed information about the selected object."""
        info = universe.get_object_info(self.selected_object)
        
        # Create info panel
        panel_width = 300
        panel_height = 400
        panel_x = self.screen_size[0] - panel_width - 10
        panel_y = 200
        
        # Draw panel background
        panel_surface = pygame.Surface((panel_width, panel_height))
        panel_surface.set_alpha(200)
        panel_surface.fill((0, 0, 0))
        self.screen.blit(panel_surface, (panel_x, panel_y))
        
        # Draw panel border
        pygame.draw.rect(self.screen, COLORS['text'], 
                        (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Draw object info
        y_offset = panel_y + 10
        for key, value in info.items():
            text = f"{key.replace('_', ' ').title()}: {value}"
            draw_text(self.screen, text, self.font_small, COLORS['text'], 
                     (panel_x + 10, y_offset))
            y_offset += 20
    
    def render(self, universe):
        """Render the complete frame."""
        # Clear screen
        self.screen.fill(COLORS['background'])
        
        # Draw grid
        self.draw_grid()
        
        # Draw objects
        self.draw_objects(universe)
        
        # Draw UI
        self.draw_ui(universe, self.paused)
        
        # Update display
        pygame.display.flip()
    
    def quit(self):
        """Clean up pygame."""
        pygame.quit() 