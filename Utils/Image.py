import pygame
import svg.path


def images_from_spritesheet(
    path: str, tilesize: tuple[int, int]
) -> list[pygame.Surface]:
    """
    Very useful function that returns a list of images based on a tiled spritesheet.
    You can use for example Aseprite to create an animation, then export the animation as a spritesheet,
    and finally use this function to get all the frames at once, without needing to crop or export single frames.
    :param path: path of the spritesheet
    :param tilesize: a tuple of 2 ints, representing the width and height of each frame in the animation
    :return: a list of the images (pygame images) of the animation.
    """
    x = y = 0
    full_img = pygame.image.load(path).convert_alpha()
    max_x, max_y = full_img.get_rect().size
    images: list[pygame.Surface] = []
    while y < max_y:
        while x < max_x:
            subsurface_rect = pygame.rect.Rect((x, y), tilesize)
            image = full_img.subsurface(subsurface_rect)
            images.append(image)
            x += tilesize[0]
        x = 0
        y += tilesize[1]
    return images


def surf_from_svg(
    svg_path: str,
    dimensions: tuple[int, int],
    color: pygame.Color = pygame.Color("black"),
    resolution=100,
) -> pygame.Surface:
    import xml.etree.ElementTree as ET

    try:
        # Parse the SVG XML
        tree = ET.parse(svg_path)
        root = tree.getroot()

        # Extract viewBox or width/height for scaling
        viewbox = root.get('viewBox')
        if viewbox:
            vb_parts = [float(x) for x in viewbox.split()]
            svg_width, svg_height = vb_parts[2] - vb_parts[0], vb_parts[3] - vb_parts[1]
            offset_x, offset_y = vb_parts[0], vb_parts[1]
        else:
            # Parse width/height, removing units like 'px'
            import re
            width_str = root.get('width', '100')
            height_str = root.get('height', '100')
            svg_width = float(re.sub(r'[^0-9.-]', '', width_str)) if width_str else 100
            svg_height = float(re.sub(r'[^0-9.-]', '', height_str)) if height_str else 100
            offset_x = offset_y = 0

        # Calculate scale
        scale_x = dimensions[0] / svg_width
        scale_y = dimensions[1] / svg_height
        scale = min(scale_x, scale_y)

        # Create surface
        surf = pygame.Surface(dimensions, pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))

        # Build a dictionary of defined paths from <defs>
        defs = {}
        defs_path_ids = set()  # Track which path IDs are in defs
        for defs_elem in root.iter():
            if defs_elem.tag.split('}')[-1] == 'defs':
                for path_def in defs_elem:
                    if path_def.tag.split('}')[-1] == 'path':
                        path_id = path_def.get('id')
                        path_d = path_def.get('d')
                        if path_id and path_d:
                            defs[path_id] = path_d
                            defs_path_ids.add(id(path_def))  # Track the element's identity

        # Collect all paths to render with their transforms
        paths_to_render = []  # List of (path_d, translate_x, translate_y) tuples

        def parse_transform(transform_str):
            """Extract translate values from transform attribute"""
            if not transform_str:
                return 0, 0
            import re
            # Look for translate(x,y) or translate(x y)
            match = re.search(r'translate\(([^,\s]+)[,\s]+([^)]+)\)', transform_str)
            if match:
                return float(match.group(1)), float(match.group(2))
            return 0, 0

        # Find all <use> elements that reference paths
        for elem in root.iter():
            tag = elem.tag.split('}')[-1]

            if tag == 'use':
                href = elem.get('{http://www.w3.org/1999/xlink}href') or elem.get('href')
                if href and href.startswith('#'):
                    ref_id = href[1:]
                    if ref_id in defs:
                        # Get transform from the use element
                        transform = elem.get('transform', '')
                        tx, ty = parse_transform(transform)
                        paths_to_render.append((defs[ref_id], tx, ty))

            elif tag == 'path':
                # Only add paths that are NOT in defs (not definitions)
                if id(elem) not in defs_path_ids:
                    d = elem.get('d')
                    if d:
                        transform = elem.get('transform', '')
                        tx, ty = parse_transform(transform)
                        paths_to_render.append((d, tx, ty))

        # Render each path
        for path_d, tx, ty in paths_to_render:
            try:
                parsed_path = svg.path.parse_path(path_d)

                # Get points along the path
                pts = [
                    (p.real, p.imag)
                    for p in (
                        parsed_path.point(i / resolution) for i in range(0, resolution + 1)
                    )
                ]

                # Scale and transform points (including translate from transform)
                transformed_pts = [
                    (
                        int((x + tx - offset_x) * scale),
                        int((y + ty - offset_y) * scale)
                    )
                    for x, y in pts
                ]

                # Draw the path
                if len(transformed_pts) > 1:
                    pygame.draw.aalines(surf, color, False, transformed_pts, 1)

            except Exception as e:
                print(f"Error parsing path: {e}")
                continue

        return surf

    except Exception as e:
        print(f"Error loading SVG '{svg_path}': {e}")
        import traceback
        traceback.print_exc()
        # Fallback: create a placeholder surface
        surf = pygame.Surface(dimensions, pygame.SRCALPHA)
        surf.fill((255, 0, 255))
        return surf
