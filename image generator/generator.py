from PIL import Image
import random
import colorsys
import math
import argparse

def generate_gradient_image(
    image_width=800,
    image_height=800,
    cell_size=64,
    border_size=1,
    border_color=(0, 0, 0),
    use_border=True,
    color_mode="harmonious",
    gradient_types=["horizontal", "vertical", "diagonal", "radial"],
    saturation_range=(0.5, 1.0),
    brightness_range=(0.5, 0.9),
    output_filename="enhanced_gradient_pattern.png"
):
    """
    Generate an image with a grid of cells containing various gradient patterns.
    
    Parameters:
    - image_width, image_height: Dimensions of the output image
    - cell_size: Size of each gradient cell
    - border_size: Width of the border between cells
    - border_color: Color of the border between cells
    - use_border: Whether to draw borders between cells
    - color_mode: How to generate colors ("random", "harmonious", "monochromatic", "analogous", "complementary")
    - gradient_types: List of gradient patterns to use
    - saturation_range: Range of saturation values for HSV color generation
    - brightness_range: Range of brightness values for HSV color generation
    - output_filename: Name of the output file
    """
    
    # Calculate the number of cells in each direction
    cells_x = image_width // cell_size
    cells_y = image_height // cell_size
    
    # Create a new blank image with RGB mode
    image = Image.new("RGB", (image_width, image_height), border_color)
    pixels = image.load()
    
    # Create a base hue for harmonious colors
    base_hue = random.random()
    
    # Generate the image with random gradients in each cell
    for i in range(cells_x):
        for j in range(cells_y):
            # Calculate the top-left corner of the cell
            cell_x = i * cell_size
            cell_y = j * cell_size
            
            # Choose gradient type
            gradient_type = random.choice(gradient_types)
            
            # Generate colors based on the selected color mode
            color_A, color_B = generate_color_pair(
                color_mode, 
                base_hue, 
                saturation_range, 
                brightness_range
            )
            
            # Calculate effective cell area considering borders
            effective_cell_size = cell_size - (border_size * 2 if use_border else 0)
            start_x = cell_x + (border_size if use_border else 0)
            start_y = cell_y + (border_size if use_border else 0)
            end_x = start_x + effective_cell_size
            end_y = start_y + effective_cell_size
            
            # Fill the cell with the selected gradient pattern
            if gradient_type == "horizontal":
                horizontal_gradient(pixels, start_x, start_y, end_x, end_y, color_A, color_B)
            elif gradient_type == "vertical":
                vertical_gradient(pixels, start_x, start_y, end_x, end_y, color_A, color_B)
            elif gradient_type == "diagonal":
                diagonal_gradient(pixels, start_x, start_y, end_x, end_y, color_A, color_B)
            elif gradient_type == "radial":
                radial_gradient(pixels, start_x, start_y, end_x, end_y, color_A, color_B)
    
    # Save the image
    image.save(output_filename)
    print(f"Enhanced gradient image generated and saved as '{output_filename}'")
    return image

def generate_color_pair(color_mode, base_hue, saturation_range, brightness_range):
    """Generate a pair of colors based on the specified color mode."""
    
    s1 = random.uniform(*saturation_range)
    v1 = random.uniform(*brightness_range)
    
    if color_mode == "random":
        # Completely random colors
        h1 = random.random()
        h2 = random.random()
        s2 = random.uniform(*saturation_range)
        v2 = random.uniform(*brightness_range)
    
    elif color_mode == "harmonious":
        # Colors with related hues
        h1 = base_hue
        # Golden ratio conjugate creates visually pleasing hue spacing
        h2 = (h1 + 0.618033988749895) % 1.0
        s2 = random.uniform(*saturation_range)
        v2 = random.uniform(*brightness_range)
    
    elif color_mode == "monochromatic":
        # Same hue, different saturation/value
        h1 = h2 = base_hue
        s2 = random.uniform(*saturation_range)
        v2 = random.uniform(*brightness_range)
        # Ensure the colors are different enough
        while abs(s1-s2) + abs(v1-v2) < 0.4:
            s2 = random.uniform(*saturation_range)
            v2 = random.uniform(*brightness_range)
    
    elif color_mode == "analogous":
        # Adjacent hues on the color wheel
        h1 = base_hue
        h2 = (h1 + random.uniform(0.05, 0.15)) % 1.0
        s2 = random.uniform(*saturation_range)
        v2 = random.uniform(*brightness_range)
    
    elif color_mode == "complementary":
        # Opposite hues on the color wheel
        h1 = base_hue
        h2 = (h1 + 0.5) % 1.0
        s2 = random.uniform(*saturation_range)
        v2 = random.uniform(*brightness_range)
    
    else:
        # Default to harmonious if mode is unrecognized
        h1 = base_hue
        h2 = (h1 + 0.618033988749895) % 1.0
        s2 = random.uniform(*saturation_range)
        v2 = random.uniform(*brightness_range)
    
    # Convert HSV to RGB
    color_A = hsv_to_rgb(h1, s1, v1)
    color_B = hsv_to_rgb(h2, s2, v2)
    
    return color_A, color_B

def hsv_to_rgb(h, s, v):
    """Convert HSV color to RGB."""
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))

def interpolate_color(color_A, color_B, t):
    """Smoothly interpolate between two colors."""
    # Improved interpolation with gamma correction for better visual perception
    # Convert to linear space, interpolate, then convert back
    def gamma_expand(c):
        return c / 255.0 if c <= 0.04045 else ((c / 255.0 + 0.055) / 1.055) ** 2.4
    
    def gamma_compress(c):
        return int(max(0, min(255, c * 255.0 if c <= 0.0031308 else 1.055 * (c ** (1.0 / 2.4)) - 0.055)))
    
    r1, g1, b1 = [gamma_expand(c) for c in color_A]
    r2, g2, b2 = [gamma_expand(c) for c in color_B]
    
    r = r1 * (1 - t) + r2 * t
    g = g1 * (1 - t) + g2 * t
    b = b1 * (1 - t) + b2 * t
    
    return (gamma_compress(r), gamma_compress(g), gamma_compress(b))

def horizontal_gradient(pixels, start_x, start_y, end_x, end_y, color_A, color_B):
    """Fill an area with a horizontal gradient."""
    width = end_x - start_x
    for x in range(start_x, end_x):
        t = (x - start_x) / max(1, width - 1)
        color = interpolate_color(color_A, color_B, t)
        for y in range(start_y, end_y):
            pixels[x, y] = color

def vertical_gradient(pixels, start_x, start_y, end_x, end_y, color_A, color_B):
    """Fill an area with a vertical gradient."""
    height = end_y - start_y
    for y in range(start_y, end_y):
        t = (y - start_y) / max(1, height - 1)
        color = interpolate_color(color_A, color_B, t)
        for x in range(start_x, end_x):
            pixels[x, y] = color

def diagonal_gradient(pixels, start_x, start_y, end_x, end_y, color_A, color_B):
    """Fill an area with a diagonal gradient."""
    width = end_x - start_x
    height = end_y - start_y
    max_dist = width + height
    
    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            # Calculate normalized position along the diagonal
            t = ((x - start_x) + (y - start_y)) / max(1, max_dist - 2)
            color = interpolate_color(color_A, color_B, t)
            pixels[x, y] = color

def radial_gradient(pixels, start_x, start_y, end_x, end_y, color_A, color_B):
    """Fill an area with a radial gradient."""
    width = end_x - start_x
    height = end_y - start_y
    center_x = start_x + width // 2
    center_y = start_y + height // 2
    max_radius = math.sqrt((width/2)**2 + (height/2)**2)
    
    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            # Calculate distance from center
            dx = x - center_x
            dy = y - center_y
            distance = math.sqrt(dx**2 + dy**2)
            # Normalize distance
            t = min(1.0, distance / max_radius)
            color = interpolate_color(color_A, color_B, t)
            pixels[x, y] = color

def main():
    """Main function to parse command-line arguments and generate the image."""
    parser = argparse.ArgumentParser(description="Generate an image with gradient patterns")
    parser.add_argument("--width", type=int, default=800, help="Image width in pixels")
    parser.add_argument("--height", type=int, default=800, help="Image height in pixels")
    parser.add_argument("--cell-size", type=int, default=64, help="Size of each cell in pixels")
    parser.add_argument("--border-size", type=int, default=1, help="Width of the border between cells")
    parser.add_argument("--no-border", action="store_true", help="Remove borders between cells")
    parser.add_argument("--color-mode", choices=["random", "harmonious", "monochromatic", "analogous", "complementary"], 
                        default="harmonious", help="Color selection mode")
    parser.add_argument("--gradients", nargs="+", 
                        choices=["horizontal", "vertical", "diagonal", "radial"], 
                        default=["horizontal", "vertical", "diagonal", "radial"], 
                        help="Gradient patterns to use")
    parser.add_argument("--output", default="enhanced_gradient_pattern.png", help="Output filename")
    
    args = parser.parse_args()
    
    generate_gradient_image(
        image_width=args.width,
        image_height=args.height,
        cell_size=args.cell_size,
        border_size=args.border_size,
        use_border=not args.no_border,
        color_mode=args.color_mode,
        gradient_types=args.gradients,
        output_filename=args.output
    )

if __name__ == "__main__":
    main()
