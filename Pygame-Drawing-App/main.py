import pygame
import sys
import time

def main():
    # Initialize Pygame
    pygame.init()
    
    # Screen dimensions
    width, height = 1000, 700
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Interactive Drawing App")
    
    # Clock for controlling FPS
    clock = pygame.time.Clock()
    
    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    
    # Brush settings
    brush_color = BLACK
    brush_size = 5
    MAX_BRUSH_SIZE = 50
    MIN_BRUSH_SIZE = 1
    
    # Flags and tracking
    drawing = False
    last_pos = None
    save_message_time = 0
    
    # Fonts for UI
    font = pygame.font.SysFont('Arial', 16)
    
    # Instructions
    instructions = [
        "Hold LMB to draw. R:Red G:Green B:Blue K:Black",
        "UP/DOWN: Brush Size | C:Clear | S:Save"
    ]
    instruction_surfaces = [font.render(line, True, BLACK) for line in instructions]
    
    # Main loop
    while True:
        current_time = pygame.time.get_ticks()
        screen.fill(WHITE)  # Clear screen each frame to prevent ghosting
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            # Mouse events
            elif event.type == pygame.MOUSEBUTTONDOWN:
                drawing = True
                last_pos = event.pos
                
            elif event.type == pygame.MOUSEBUTTONUP:
                drawing = False
                last_pos = None
                
            elif event.type == pygame.MOUSEMOTION and drawing:
                mouse_pos = event.pos
                if last_pos:
                    # Draw smooth lines using anti-aliased circles and lines
                    dx = mouse_pos[0] - last_pos[0]
                    dy = mouse_pos[1] - last_pos[1]
                    distance = max(abs(dx), abs(dy))
                    for i in range(distance):
                        x = int(last_pos[0] + dx * i / distance)
                        y = int(last_pos[1] + dy * i / distance)
                        pygame.draw.circle(screen, brush_color, (x, y), brush_size // 2)
                last_pos = mouse_pos
                
            # Keyboard events
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:  # Clear canvas
                    pass  # Screen is cleared each frame
                elif event.key == pygame.K_s:  # Save drawing
                    pygame.image.save(screen, "drawing.png")
                    save_message_time = current_time
                    print("Saved drawing as drawing.png")
                elif event.key == pygame.K_r:
                    brush_color = (255, 0, 0)
                elif event.key == pygame.K_g:
                    brush_color = (0, 255, 0)
                elif event.key == pygame.K_b:
                    brush_color = (0, 0, 255)
                elif event.key == pygame.K_k:
                    brush_color = BLACK
                elif event.key == pygame.K_UP:
                    brush_size = min(MAX_BRUSH_SIZE, brush_size + 1)
                elif event.key == pygame.K_DOWN:
                    brush_size = max(MIN_BRUSH_SIZE, brush_size - 1)
        
        # Re-draw all UI elements
        # 1. Instructions
        for i, surf in enumerate(instruction_surfaces):
            screen.blit(surf, (10, 10 + i * 20))
            
        # 2. Current color and size
        color_text = font.render(f"Color: {brush_color}", True, BLACK)
        size_text = font.render(f"Size: {brush_size}", True, BLACK)
        screen.blit(color_text, (10, 60))
        screen.blit(size_text, (10, 80))
        
        # 3. Save confirmation
        if current_time - save_message_time < 2000:
            save_text = font.render("Drawing saved as drawing.png", True, BLACK)
            screen.blit(save_text, (width // 2 - 120, height - 30))
        
        pygame.display.flip()
        clock.tick(120)  # Limit to 120 FPS

if __name__ == "__main__":
    main()
