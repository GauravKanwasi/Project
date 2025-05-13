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
    - image_width, image_height: Dimensions of the output image in pixels
    - cell_size: Size of each gradient cell in pixels
    - border_size: Width of the border between cells in pixels
    - border_color: RGB tuple for the border color (e.g., (0, 0, 0) for black)
    - use_border: Boolean to enable/disable borders between cells
    - color_mode: Color generation mode ("random", "harmonious", "monochromatic", "analogous", "complementary")
    - gradient_types: List of gradient patterns to randomly choose from
    - saturation_range: Tuple of (min, max) saturation values for HSV colors
    - brightness_range: Tuple of (min, max) brightness values for HSV colors
    - output_filename: Name of the output file (extension determines format)
    """
    # Validate input parameters
    if cell_size <= 0 or image_width <= 0 or image_height <= 0:
        raise ValueError("Image dimensions and cell size must be positive.")
    if use_border and border_size * 2 >= cell_size:
        raise ValueError("Border size too large relative to cell size.")

    # Calculate number of cells
    cells_x = image_width // cell_size
    cells_y = image_height // cell_size

    # Create a new image initialized with border color
    image = Image.new("RGB", (image_width, image_height), border_color)
    pixels = image.load()

    # Base hue for consistent color schemes
    base_hue = random.random()

    # Fill grid with gradients
    for i in range(cells_x):
        for j in range(cells_y):
            cell_x = i * cell_size
            cell_y = j * cell_size

            # Randomly select gradient type
            gradient_type = random.choice(gradient_types)

            # Generate color pair
            color_A, color_B = generate_color_pair(
                color_mode, base_hue, saturation_range, brightness_range
            )

            # Calculate gradient area with borders
            effective_cell_size = cell_size - (border_size * 2 if use_border else 0)
            start_x = cell_x + (border_size if use_border else 0)
            start_y = cell_y + (border_size if use_border else 0)
            end_x = start_x + effective_cell_size
            end_y = start_y + effective_cell_size

            # Skip if effective size is invalid
            if effective_cell_size <= 0:
                continue

            # Apply the chosen gradient
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
    print(f"Gradient image saved as '{output_filename}'")
    return image

def generate_color_pair(color_mode, base_hue, saturation_range, brightness_range):
    """Generate two RGB colors based on the specified color mode."""
    s1 = random.uniform(*saturation_range)
    v1 = random.uniform(*brightness_range)

    if color_mode == "random":
        h1, h2 = random.random(), random.random()
        s2 = random.uniform(*saturation_range)
        v2 = random.uniform(*brightness_range)
    elif color_mode == "harmonious":
        h1 = base_hue
        h2 = (h1 + 0.618033988749895) % 1.0  # Golden ratio conjugate
        s2 = random.uniform(*saturation_range)
        v2 = random.uniform(*brightness_range)
    elif color_mode == "monochromatic":
        h1 = h2 = base_hue
        s2 = random.uniform(*saturation_range)
        v2 = random.uniform(*brightness_range)
        while abs(s1 - s2) + abs(v1 - v2) < 0.4:  # Ensure visible contrast
            s2 = random.uniform(*saturation_range)
            v2 = random.uniform(*brightness_range)
    elif color_mode == "analogous":
        h1 = base_hue
        h2 = (h1 + random.uniform(0.05, 0.15)) % 1.0
        s2 = random.uniform(*saturation_range)
        v2 = random.uniform(*brightness_range)
    elif color_mode == "complementary":
        h1 = base_hue
        h2 = (h1 + 0.5) % 1.0
        s2 = random.uniform(*saturation_range)
        v2 = random.uniform(*brightness_range)
    else:
        h1 = base_hue
        h2 = (h1 + 0.618033988749895) % 1.0  # Fallback to harmonious
        s2 = random.uniform(*saturation_range)
        v2 = random.uniform(*brightness_range)

    return hsv_to_rgb(h1, s1, v1), hsv_to_rgb(h2, s2, v2)

def hsv_to_rgb(h, s, v):
    """Convert HSV color to RGB tuple."""
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))

def interpolate_color(color_A, color_B, t):
    """
    Interpolate between two RGB colors using sRGB gamma correction for perceptual uniformity.
    - color_A, color_B: RGB tuples (0-255)
    - t: Interpolation factor (0 to 1)
    """
    def gamma_expand(c):
        """Convert sRGB to linear RGB."""
        c_srgb = c / 255.0
        return c_srgb / 12.92 if c_srgb <= 0.04045 else ((c_srgb + 0.055) / 1.055) ** 2.4

    def gamma_compress(c_linear):
        """Convert linear RGB to sRGB."""
        c_srgb = c_linear * 12.92 if c_linear <= 0.0031308 else 1.055 * (c_linear ** (1.0 / 2.4)) - 0.055
        return int(max(0, min(255, round(c_srgb * 255))))

    # Convert to linear space
    r1, g1, b1 = [gamma_expand(c) for c in color_A]
    r2, g2, b2 = [gamma_expand(c) for c in color_B]

    # Linear interpolation
    r = r1 * (1 - t) + r2 * t
    g = g1 * (1 - t) + g2 * t
    b = b1 * (1 - t) + b2 * t

    # Convert back to sRGB
    return (gamma_compress(r), gamma_compress(g), gamma_compress(b))

def horizontal_gradient(pixels, start_x, start_y, end_x, end_y, color_A, color_B):
    """Fill area with a horizontal gradient from color_A to color_B."""
    width = end_x - start_x
    for x in range(start_x, end_x):
        t = (x - start_x) / max(1, width - 1)
        color = interpolate_color(color_A, color_B, t)
        for y in range(start_y, end_y):
            pixels[x, y] = color

def vertical_gradient(pixels, start_x, start_y, end_x, end_y, color_A, color_B):
    """Fill area with a vertical gradient from color_A to color_B."""
    height = end_y - start_y
    for y in range(start_y, end_y):
        t = (y - start_y) / max(1, height - 1)
        color = interpolate_color(color_A, color_B, t)
        for x in range(start_x, end_x):
            pixels[x, y] = color

def diagonal_gradient(pixels, start_x, start_y, end_x, end_y, color_A, color_B):
    """Fill area with a diagonal gradient (top-left to bottom-right)."""
    width = end_x - start_x
    height = end_y - start_y
    max_dist = width + height
    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            t = ((x - start_x) + (y - start_y)) / max(1, max_dist - 2)
            pixels[x, y] = interpolate_color(color_A, color_B, t)

def radial_gradient(pixels, start_x, start_y, end_x, end_y, color_A, color_B):
    """Fill area with a radial gradient from center (color_A) to edges (color_B)."""
    width = end_x - start_x
    height = end_y - start_y
    center_x = start_x + width // 2
    center_y = start_y + height // 2
    max_radius = math.sqrt((width / 2) ** 2 + (height / 2) ** 2)
    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
            t = min(1.0, distance / max_radius)
            pixels[x, y] = interpolate_color(color_A, color_B, t)

def main():
    """Parse command-line arguments and generate the gradient image."""
    parser = argparse.ArgumentParser(description="Generate an image with gradient patterns.")
    parser.add_argument("--width", type=int, default=800, help="Image width in pixels")
    parser.add_argument("--height", type=int, default=800, help="Image height in pixels")
    parser.add_argument("--cell-size", type=int, default=64, help="Size of each cell in pixels")
    parser.add_argument("--border-size", type=int, default=1, help="Width of border between cells")
    parser.add_argument("--no-border", action="store_true", help="Disable borders between cells")
    parser.add_argument("--color-mode", 
                        choices=["random", "harmonious", "monochromatic", "analogous", "complementary"],
                        default="harmonious", help="Color generation mode")
    parser.add_argument("--gradients", nargs="+",
                        choices=["horizontal", "vertical", "diagonal", "radial"],
                        default=["horizontal", "vertical", "diagonal", "radial"],
                        help="Gradient types to use")
    parser.add_argument("--output", default="gradient_pattern.png", help="Output filename")

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
