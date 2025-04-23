import pygame
import sys

def main():
    # Initialize the Pygame library
    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Interactive Drawing App")
    
    clock = pygame.time.Clock()
    # Fill background with white color
    screen.fill((255, 255, 255))
    
    # Initial brush settings
    brush_color = (0, 0, 0)  # Default black
    brush_size = 5

    drawing = False
    last_pos = None

    instructions = [
        "Instructions:",
        "- Hold down the left mouse button and drag to draw.",
        "- Press 'R' for Red, 'G' for Green, 'B' for Blue, 'K' for Black.",
        "- Use UP/DOWN arrows to increase/decrease brush size.",
        "- Press 'C' to clear the canvas.",
        "- Press 'S' to save your drawing as drawing.png."
    ]
    print("\n".join(instructions))

    # Main application loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Mouse events to toggle drawing state and capture positions
            if event.type == pygame.MOUSEBUTTONDOWN:
                drawing = True
                last_pos = event.pos

            if event.type == pygame.MOUSEBUTTONUP:
                drawing = False
                last_pos = None

            if event.type == pygame.MOUSEMOTION and drawing:
                mouse_pos = event.pos
                if last_pos:
                    # Draw a smooth line between the last position and current position
                    pygame.draw.line(screen, brush_color, last_pos, mouse_pos, brush_size)
                last_pos = mouse_pos

            # Keyboard events for color switching, saving, and clearing
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:  # Clear the screen with white background
                    screen.fill((255, 255, 255))
                elif event.key == pygame.K_s:  # Save the current drawing
                    pygame.image.save(screen, "drawing.png")
                    print("Saved drawing as drawing.png")
                elif event.key == pygame.K_r:  # Switch to red
                    brush_color = (255, 0, 0)
                elif event.key == pygame.K_g:  # Switch to green
                    brush_color = (0, 255, 0)
                elif event.key == pygame.K_b:  # Switch to blue
                    brush_color = (0, 0, 255)
                elif event.key == pygame.K_k:  # Switch to black
                    brush_color = (0, 0, 0)
                elif event.key == pygame.K_UP:  # Increase brush size
                    brush_size += 1
                elif event.key == pygame.K_DOWN:  # Decrease brush size (min 1)
                    brush_size = max(1, brush_size - 1)

        pygame.display.flip()
        clock.tick(120)  # Aim for a smooth 120 FPS

if __name__ == "__main__":
    main()
