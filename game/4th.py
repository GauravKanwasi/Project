import pygame
import sys
import random

# Initialize Pygame and mixer
pygame.init()
pygame.mixer.init()

# Set up the display
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Space Invaders")

# Colors
black = (0, 0, 0)
white = (255, 255, 255)

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Player settings
player_width = 50
player_height = 50
player_speed = 5
player = pygame.Rect(screen_width // 2 - player_width // 2, screen_height - player_height - 10, player_width, player_height)

# Alien settings
alien_width = 40
alien_height = 40
alien_rows = 5
alien_columns = 10
alien_spacing = 20
alien_speed = 1  # Will be updated per level
alien_direction = 1  # 1 for right, -1 for left

# Bullet settings
bullet_width = 5
bullet_height = 10
bullet_speed = 7
player_bullet = None
alien_bullets = []
alien_bullet_speed = 5

# Game variables
score = 0
lives = 3
level = 1
font = pygame.font.Font(None, 36)

# Load sound effects (ensure these files exist in the same directory)
shoot_sound = pygame.mixer.Sound("shoot.wav")
explosion_sound = pygame.mixer.Sound("explosion.wav")
hit_sound = pygame.mixer.Sound("hit.wav")

# Functions
def draw_player(player):
    pygame.draw.rect(screen, white, player)

def move_player(keys, player):
    if keys[pygame.K_LEFT] and player.x > 0:
        player.x -= player_speed
    if keys[pygame.K_RIGHT] and player.x < screen_width - player_width:
        player.x += player_speed

def draw_aliens(aliens):
    for alien in aliens:
        pygame.draw.rect(screen, white, alien)

def move_aliens(aliens, direction):
    for alien in aliens:
        alien.x += alien_speed * direction
    for alien in aliens:
        if alien.x <= 0 or alien.x + alien_width >= screen_width:
            return -direction, True
    return direction, False

def drop_aliens(aliens):
    for alien in aliens:
        alien.y += 10

def setup_aliens(level):
    global aliens, alien_speed
    aliens = []
    alien_speed = 1 + (level - 1) * 0.5  # Increase speed with level
    for row in range(alien_rows):
        for col in range(alien_columns):
            alien_x = col * (alien_width + alien_spacing) + 50
            alien_y = row * (alien_height + alien_spacing) + 50
            aliens.append(pygame.Rect(alien_x, alien_y, alien_width, alien_height))

def fire_bullet(player):
    global player_bullet
    if player_bullet is None:
        bullet_x = player.x + player_width // 2 - bullet_width // 2
        bullet_y = player.y - bullet_height
        player_bullet = pygame.Rect(bullet_x, bullet_y, bullet_width, bullet_height)
        shoot_sound.play()  # Play shooting sound

def move_bullet(bullet):
    if bullet is not None:
        bullet.y -= bullet_speed
        if bullet.y < 0:
            return None
    return bullet

def draw_bullet(bullet):
    if bullet is not None:
        pygame.draw.rect(screen, white, bullet)

def alien_shoot(aliens):
    if random.random() < 0.005 and aliens:
        shooter = random.choice(aliens)
        bullet_x = shooter.x + alien_width // 2 - bullet_width // 2
        bullet_y = shooter.y + alien_height
        alien_bullets.append(pygame.Rect(bullet_x, bullet_y, bullet_width, bullet_height))

def move_alien_bullets(bullets):
    for bullet in bullets:
        bullet.y += alien_bullet_speed
    return [bullet for bullet in bullets if bullet.y < screen_height]

def draw_alien_bullets(bullets):
    for bullet in bullets:
        pygame.draw.rect(screen, white, bullet)

def check_player_bullet_collision(player_bullet, aliens):
    global score
    if player_bullet is not None:
        for alien in aliens[:]:
            if player_bullet.colliderect(alien):
                aliens.remove(alien)
                score += 10
                explosion_sound.play()  # Play explosion sound
                return None
    return player_bullet

def check_alien_bullets_collision(alien_bullets, player):
    global lives
    for bullet in alien_bullets[:]:
        if bullet.colliderect(player):
            alien_bullets.remove(bullet)
            lives -= 1
            hit_sound.play()  # Play hit sound
            if lives <= 0:
                return True  # Game over
            else:
                player.x = screen_width // 2 - player_width // 2  # Respawn player
                return False
    return False

# Initialize aliens for level 1
setup_aliens(level)

# Game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                fire_bullet(player)
    
    # Get keys pressed
    keys = pygame.key.get_pressed()
    
    # Move player
    move_player(keys, player)
    
    # Move aliens
    alien_direction, should_drop = move_aliens(aliens, alien_direction)
    if should_drop:
        drop_aliens(aliens)
    
    # Move player bullet
    player_bullet = move_bullet(player_bullet)
    
    # Move alien bullets
    alien_bullets = move_alien_bullets(alien_bullets)
    
    # Check collisions
    player_bullet = check_player_bullet_collision(player_bullet, aliens)
    if check_alien_bullets_collision(alien_bullets, player):
        print("Game over! You were hit.")
        running = False
    
    # Aliens shoot
    alien_shoot(aliens)
    
    # Check lose condition (aliens reach bottom)
    for alien in aliens:
        if alien.y + alien_height >= screen_height:
            print("Game over! Aliens reached the bottom.")
            running = False
            break
    
    # Check if all aliens are destroyed (level up)
    if not aliens:
        level += 1
        setup_aliens(level)
        player_bullet = None
        alien_bullets = []
    
    # Draw everything
    screen.fill(black)
    draw_player(player)
    draw_aliens(aliens)
    draw_bullet(player_bullet)
    draw_alien_bullets(alien_bullets)
    
    # Draw score, lives, and level
    score_text = font.render(f"Score: {score}", True, white)
    screen.blit(score_text, (10, 10))
    lives_text = font.render(f"Lives: {lives}", True, white)
    screen.blit(lives_text, (10, 40))
    level_text = font.render(f"Level: {level}", True, white)
    screen.blit(level_text, (10, 70))
    
    # Update display
    pygame.display.flip()
    
    # Cap frame rate
    clock.tick(60)

pygame.quit()
sys.exit()
