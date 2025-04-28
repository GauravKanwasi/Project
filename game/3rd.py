import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants for the game
WIDTH, HEIGHT = 800, 600           # Window size
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100  # Paddle dimensions
BALL_SIZE = 20                     # Ball size
PADDLE_SPEED = 5                   # Paddle movement speed
BALL_SPEED_X, BALL_SPEED_Y = 5, 5  # Ball speed
WHITE = (255, 255, 255)            # Color for paddles, ball, and text
BLACK = (0, 0, 0)                  # Background color

# Set up the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Table Tennis")

# Initial positions
left_paddle_y = (HEIGHT - PADDLE_HEIGHT) // 2  # Left paddle vertical position
right_paddle_y = (HEIGHT - PADDLE_HEIGHT) // 2 # Right paddle vertical position
ball_x, ball_y = WIDTH // 2, HEIGHT // 2       # Ball starting position
ball_vel_x, ball_vel_y = BALL_SPEED_X, BALL_SPEED_Y  # Ball velocity

# Scores
left_score = 0
right_score = 0

# Font for score display
font = pygame.font.Font(None, 74)

# Function to draw paddles
def draw_paddles():
    pygame.draw.rect(screen, WHITE, (0, left_paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT))  # Left paddle
    pygame.draw.rect(screen, WHITE, (WIDTH - PADDLE_WIDTH, right_paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT))  # Right paddle

# Function to draw the ball
def draw_ball():
    pygame.draw.ellipse(screen, WHITE, (ball_x, ball_y, BALL_SIZE, BALL_SIZE))

# Function to display scores
def draw_scores():
    left_text = font.render(str(left_score), True, WHITE)
    right_text = font.render(str(right_score), True, WHITE)
    screen.blit(left_text, (WIDTH // 4, 10))    # Left score
    screen.blit(right_text, (3 * WIDTH // 4, 10))  # Right score

# Function to move paddles based on key presses
def move_paddles(keys):
    global left_paddle_y, right_paddle_y
    if keys[pygame.K_w] and left_paddle_y > 0:  # Move left paddle up
        left_paddle_y -= PADDLE_SPEED
    if keys[pygame.K_s] and left_paddle_y < HEIGHT - PADDLE_HEIGHT:  # Move left paddle down
        left_paddle_y += PADDLE_SPEED
    if keys[pygame.K_UP] and right_paddle_y > 0:  # Move right paddle up
        right_paddle_y -= PADDLE_SPEED
    if keys[pygame.K_DOWN] and right_paddle_y < HEIGHT - PADDLE_HEIGHT:  # Move right paddle down
        right_paddle_y += PADDLE_SPEED

# Function to update ball position and handle collisions
def move_ball():
    global ball_x, ball_y, ball_vel_x, ball_vel_y, left_score, right_score
    ball_x += ball_vel_x
    ball_y += ball_vel_y

    # Bounce off top and bottom walls
    if ball_y <= 0 or ball_y >= HEIGHT - BALL_SIZE:
        ball_vel_y = -ball_vel_y

    # Bounce off paddles
    if (ball_x <= PADDLE_WIDTH and left_paddle_y < ball_y < left_paddle_y + PADDLE_HEIGHT) or \
       (ball_x >= WIDTH - PADDLE_WIDTH - BALL_SIZE and right_paddle_y < ball_y < right_paddle_y + PADDLE_HEIGHT):
        ball_vel_x = -ball_vel_x

    # Score points and reset ball if it goes out of bounds
    if ball_x < 0:
        right_score += 1
        reset_ball()
    elif ball_x > WIDTH:
        left_score += 1
        reset_ball()

# Function to reset the ball to the center
def reset_ball():
    global ball_x, ball_y, ball_vel_x, ball_vel_y
    ball_x, ball_y = WIDTH // 2, HEIGHT // 2
    ball_vel_x = -ball_vel_x  # Reverse direction after a point

# Main game loop
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Exit game if window is closed
            pygame.quit()
            sys.exit()

    # Get keyboard input and update game state
    keys = pygame.key.get_pressed()
    move_paddles(keys)
    move_ball()

    # Draw everything
    screen.fill(BLACK)  # Clear screen with black background
    draw_paddles()
    draw_ball()
    draw_scores()

    pygame.display.flip()  # Update the display
    clock.tick(60)        # Run at 60 frames per second
