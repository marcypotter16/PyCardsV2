import pygame


def draw_rect_alpha(surface, color, rect, corner_radius=10, width=0):
    rect_obj = pygame.Rect(rect)
    # Skip rendering if rect has invalid dimensions
    if rect_obj.width <= 0 or rect_obj.height <= 0:
        return

    # Clamp corner_radius to valid range (can't be larger than half the smallest dimension)
    max_radius = min(rect_obj.width, rect_obj.height) // 2
    corner_radius = min(corner_radius, max_radius)

    try:
        shape_surf = pygame.Surface(rect_obj.size, pygame.SRCALPHA)
        pygame.draw.rect(shape_surf, color, shape_surf.get_rect(), width=width, border_radius=corner_radius)
        surface.blit(shape_surf, rect)
    except Exception as e:
        # Fallback to simple rect if there's an issue
        print(f"Warning: draw_rect_alpha failed with rect {rect_obj}, radius {corner_radius}: {e}")
        pygame.draw.rect(surface, color, rect_obj, width=width)
