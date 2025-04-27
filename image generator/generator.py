from PIL import Image
import random

# Set image dimensions and cell size
image_width, image_height = 512, 512
cell_size = 32  # Each cell will be 32x32 pixels

# Calculate the number of cells in each direction
cells_x = image_width // cell_size
cells_y = image_height // cell_size

# Create a new blank image with RGB mode
image = Image.new("RGB", (image_width, image_height))
pixels = image.load()  # Get pixel access object

# Function to generate a random RGB color
def random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# Generate the image with random gradients in each cell
for i in range(cells_x):
    for j in range(cells_y):
        # Calculate the top-left corner of the cell
        cell_x = i * cell_size
        cell_y = j * cell_size
        
        # Randomly choose gradient direction: 0 for horizontal, 1 for vertical
        direction = random.choice([0, 1])
        
        # Generate two random colors for the gradient
        color_A = random_color()
        color_B = random_color()
        
        if direction == 0:  # Horizontal gradient
            for x in range(cell_x, cell_x + cell_size):
                # Calculate interpolation factor t based on x position
                t = (x - cell_x) / (cell_size - 1)
                # Interpolate between color_A and color_B
                r = int(color_A[0] * (1 - t) + color_B[0] * t)
                g = int(color_A[1] * (1 - t) + color_B[1] * t)
                b = int(color_A[2] * (1 - t) + color_B[2] * t)
                # Set the entire column in the cell to this color
                for y in range(cell_y, cell_y + cell_size):
                    pixels[x, y] = (r, g, b)
        
        else:  # Vertical gradient
            for y in range(cell_y, cell_y + cell_size):
                # Calculate interpolation factor t based on y position
                t = (y - cell_y) / (cell_size - 1)
                # Interpolate between color_A and color_B
                r = int(color_A[0] * (1 - t) + color_B[0] * t)
                g = int(color_A[1] * (1 - t) + color_B[1] * t)
                b = int(color_A[2] * (1 - t) + color_B[2] * t)
                # Set the entire row in the cell to this color
                for x in range(cell_x, cell_x + cell_size):
                    pixels[x, y] = (r, g, b)

# Save the image locally
image.save("refined_random_image.png")

print("Refined random image generated and saved as 'refined_random_image.png'")
