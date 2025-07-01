import pygame
import random
import os
import math
from pygame import mixer

# Initialize Pygame and mixer
pygame.init()
mixer.init()

# Screen setup
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cosmic Jumper")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (30, 144, 255)
PURPLE = (138, 43, 226)
YELLOW = (255, 215, 0)
RED = (255, 50, 50)

# Load assets function with error handling
def load_asset(path, fallback=None):
    try:
        asset_path = os.path.join("assets", path)
        if not os.path.exists(asset_path):
            raise FileNotFoundError
        return pygame.image.load(asset_path).convert_alpha()
    except (FileNotFoundError, pygame.error):
        if fallback:
            return fallback
        # Create a colored placeholder
        surface = pygame.Surface((32, 32))
        if "player" in path:
            surface.fill(BLUE)
        elif "coin" in path:
            surface.fill(YELLOW)
            pygame.draw.circle(surface, (200, 170, 0), (16, 16), 8)
        elif "enemy" in path:
            surface.fill(RED)
        elif "background" in path:
            return pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        elif "platform" in path:
            surface.fill((0, 200, 0))
        return surface

# Load images with fallbacks
player_img = load_asset("player.png")
coin_img = load_asset("coin.png")
enemy_img = load_asset("enemy.png")
background_img = load_asset("background.png", pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)))
platform_img = load_asset("platform.png")

# Create gradient background if no image
if background_img.get_size() != (SCREEN_WIDTH, SCREEN_HEIGHT):
    background_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    for y in range(SCREEN_HEIGHT):
        # Create a gradient from dark blue to black
        color_value = max(0, 50 - int(y * 0.1))
        pygame.draw.line(background_img, (0, 0, color_value), (0, y), (SCREEN_WIDTH, y))

# Load sounds with fallbacks
try:
    jump_sound = mixer.Sound(os.path.join("assets", "jump.wav"))
    coin_sound = mixer.Sound(os.path.join("assets", "coin.wav"))
    hit_sound = mixer.Sound(os.path.join("assets", "hit.wav"))
    background_music = mixer.Sound(os.path.join("assets", "background_music.mp3"))
except:
    # Create placeholder sounds
    jump_sound = mixer.Sound(buffer=bytearray([0] * 44))
    coin_sound = mixer.Sound(buffer=bytearray([0] * 44))
    hit_sound = mixer.Sound(buffer=bytearray([0] * 44))
    background_music = mixer.Sound(buffer=bytearray([0] * 44))

# Play background music
try:
    background_music.play(-1)
except:
    pass

# Particle system for visual effects
class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def add_particles(self, x, y, color, count=5, size_range=(2, 5), velocity_range=(-2, 2)):
        for _ in range(count):
            size = random.randint(*size_range)
            velocity_x = random.uniform(*velocity_range)
            velocity_y = random.uniform(*velocity_range)
            lifetime = random.randint(20, 40)
            self.particles.append({
                'x': x, 
                'y': y, 
                'size': size, 
                'color': color,
                'velocity_x': velocity_x,
                'velocity_y': velocity_y,
                'lifetime': lifetime
            })
    
    def update(self):
        for particle in self.particles[:]:
            particle['x'] += particle['velocity_x']
            particle['y'] += particle['velocity_y']
            particle['lifetime'] -= 1
            
            # Apply gravity
            particle['velocity_y'] += 0.1
            
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
    
    def draw(self, surface):
        for particle in self.particles:
            alpha = min(255, particle['lifetime'] * 6)
            color = particle['color']
            if len(color) == 3:  # Add alpha if not present
                color = (*color, alpha)
            pygame.draw.circle(
                surface, 
                color, 
                (int(particle['x']), int(particle['y'])), 
                particle['size']
            )

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = pygame.transform.scale(player_img, (40, 40))
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT-100))
        self.velocity_y = 0
        self.velocity_x = 0
        self.jump_power = -15
        self.gravity = 0.8
        self.speed = 5
        self.on_ground = False
        self.lives = 3
        self.invincible = False
        self.invincibility_timer = 0
        self.current_platform = None
        self.double_jump_available = True
        self.direction = 1  # 1 for right, -1 for left
        self.jump_count = 0
        
    def update(self):
        # Move with platform if standing on one
        if self.current_platform is not None:
            self.rect.x += self.current_platform.velocity
        
        # Horizontal movement
        keys = pygame.key.get_pressed()
        self.velocity_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity_x = -self.speed
            self.direction = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity_x = self.speed
            self.direction = 1
            
        # Flip image based on direction
        if self.direction == -1:
            self.image = pygame.transform.flip(self.original_image, True, False)
        else:
            self.image = self.original_image.copy()
            
        # Jump
        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and (self.on_ground or self.double_jump_available):
            if not self.on_ground:
                self.double_jump_available = False
            self.velocity_y = self.jump_power
            self.on_ground = False
            self.jump_count += 1
            jump_sound.play()
            
        # Apply gravity
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y
        self.rect.x += self.velocity_x
        
        # Screen boundaries - wrap around horizontally
        if self.rect.right < 0:
            self.rect.left = SCREEN_WIDTH
        elif self.rect.left > SCREEN_WIDTH:
            self.rect.right = 0
            
        # Ground collision
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.velocity_y = 0
            self.on_ground = True
            self.double_jump_available = True
            self.jump_count = 0
            
        # Invincibility timer and visual effect
        if self.invincible:
            self.invincibility_timer -= 1
            if self.invincibility_timer <= 0:
                self.invincible = False
            # Blink effect
            alpha = 128 if (self.invincibility_timer // 4) % 2 == 0 else 255
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.original_image = pygame.transform.scale(coin_img, (20, 20))
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))
        self.rotation = 0
        self.float_offset = random.uniform(0, 2 * math.pi)
        
    def update(self):
        # Rotate coin
        self.rotation = (self.rotation + 2) % 360
        self.image = pygame.transform.rotate(self.original_image, self.rotation)
        self.rect = self.image.get_rect(center=self.rect.center)
        
        # Float up and down
        self.rect.y += math.sin(pygame.time.get_ticks() / 200 + self.float_offset) * 0.5

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.original_image = pygame.transform.scale(enemy_img, (50, 30))
        self.image = self.original_image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = random.randint(3, 6) * random.choice([-1, 1])
        self.float_offset = random.uniform(0, 2 * math.pi)
        
    def update(self):
        self.rect.x += self.speed
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
            
        # Float up and down
        self.rect.y += math.sin(pygame.time.get_ticks() / 300 + self.float_offset) * 0.3

class JumpingEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.velocity_y = 0
        self.jump_power = -10
        self.gravity = 0.5
        self.jump_timer = random.randint(60, 120)
        
    def update(self):
        super().update()  # Move horizontally and float
        self.jump_timer -= 1
        if self.jump_timer <= 0:
            self.velocity_y = self.jump_power
            self.jump_timer = random.randint(60, 120)
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.velocity_y = 0

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, velocity=0):
        super().__init__()
        self.image = pygame.transform.scale(platform_img, (width, 20))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.velocity = velocity
        self.float_offset = random.uniform(0, 2 * math.pi)
        
    def update(self):
        if self.velocity != 0:
            self.rect.x += self.velocity
            if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
                self.velocity *= -1
                
        # Slight floating motion
        self.rect.y += math.sin(pygame.time.get_ticks() / 500 + self.float_offset) * 0.2

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, type="invincibility"):
        super().__init__()
        self.type = type
        self.original_image = pygame.Surface((20, 20), pygame.SRCALPHA)
        
        # Create different appearances for power-ups
        if type == "invincibility":
            pygame.draw.circle(self.original_image, (255, 255, 0), (10, 10), 10)
            pygame.draw.circle(self.original_image, (200, 200, 0), (10, 10), 8)
        elif type == "speed":
            pygame.draw.circle(self.original_image, (0, 255, 0), (10, 10), 10)
            pygame.draw.circle(self.original_image, (0, 200, 0), (10, 10), 8)
        elif type == "health":
            pygame.draw.circle(self.original_image, (255, 0, 0), (10, 10), 10)
            pygame.draw.circle(self.original_image, (200, 0, 0), (10, 10), 8)
            # Draw heart shape
            points = [
                (10, 7),
                (12, 5),
                (14, 7),
                (14, 10),
                (10, 14),
                (6, 10),
                (6, 7)
            ]
            pygame.draw.polygon(self.original_image, (255, 255, 255), points, 0)
        
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))
        self.rotation = 0
        self.float_offset = random.uniform(0, 2 * math.pi)
        
    def update(self):
        # Rotate and float
        self.rotation = (self.rotation + 1) % 360
        self.image = pygame.transform.rotate(self.original_image, self.rotation)
        self.rect = self.image.get_rect(center=self.rect.center)
        
        # Float up and down
        self.rect.y += math.sin(pygame.time.get_ticks() / 250 + self.float_offset) * 0.5

# Game setup
all_sprites = pygame.sprite.Group()
coins = pygame.sprite.Group()
enemies = pygame.sprite.Group()
platforms = pygame.sprite.Group()
power_ups = pygame.sprite.Group()

# Create player
player = Player()
all_sprites.add(player)

# Create platforms with some moving
platform_layout = [
    (50, 500, 150, 0),   # Static
    (250, 400, 100, 2),  # Moving right
    (450, 300, 120, 0),  # Static
    (650, 200, 100, -3), # Moving left
    (100, 100, 150, 0),  # Static
]
for x, y, width, velocity in platform_layout:
    platform = Platform(x, y, width, velocity)
    all_sprites.add(platform)
    platforms.add(platform)

# Create initial coins
for _ in range(15):
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(50, SCREEN_HEIGHT-50)
    coin = Coin(x, y)
    all_sprites.add(coin)
    coins.add(coin)

# Game variables
score = 0
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)
high_score = 0
game_state = "playing"
pause = False
particle_system = ParticleSystem()

# Main game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                pause = not pause
            if event.key == pygame.K_r and game_state == "game_over":
                # Reset game
                score = 0
                player.lives = 3
                player.rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT-100)
                player.velocity_y = 0
                enemies.empty()
                all_sprites.empty()
                coins.empty()
                power_ups.empty()
                platforms.empty()
                
                # Recreate player
                player = Player()
                all_sprites.add(player)
                
                # Recreate platforms
                for x, y, width, velocity in platform_layout:
                    platform = Platform(x, y, width, velocity)
                    all_sprites.add(platform)
                    platforms.add(platform)
                
                # Recreate coins
                for _ in range(15):
                    x = random.randint(0, SCREEN_WIDTH)
                    y = random.randint(50, SCREEN_HEIGHT-50)
                    coin = Coin(x, y)
                    all_sprites.add(coin)
                    coins.add(coin)
                
                game_state = "playing"
    
    if pause or game_state != "playing":
        # Draw pause/game over overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        if pause:
            pause_text = font.render("PAUSED", True, WHITE)
            screen.blit(pause_text, (SCREEN_WIDTH//2 - pause_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
            resume_text = small_font.render("Press P to Resume", True, WHITE)
            screen.blit(resume_text, (SCREEN_WIDTH//2 - resume_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
        elif game_state == "game_over":
            game_over_text = font.render("GAME OVER", True, RED)
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
            restart_text = small_font.render("Press R to Restart", True, WHITE)
            screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
            final_score = font.render(f"Final Score: {score}", True, YELLOW)
            screen.blit(final_score, (SCREEN_WIDTH//2 - final_score.get_width()//2, SCREEN_HEIGHT//2 - 100))
        
        pygame.display.flip()
        clock.tick(60)
        continue
        
    # Update particles
    particle_system.update()
    
    # Update game objects
    all_sprites.update()
    
    # Platform collision
    platform_hits = pygame.sprite.spritecollide(player, platforms, False)
    player.on_ground = False  # Reset each frame
    for platform in platform_hits:
        # Check if player is falling and collides with top of platform
        if (player.velocity_y >= 0 and 
            player.rect.bottom > platform.rect.top and 
            player.rect.top < platform.rect.top and
            player.rect.bottom - player.velocity_y <= platform.rect.top):
            
            player.rect.bottom = platform.rect.top
            player.velocity_y = 0
            player.on_ground = True
            player.double_jump_available = True
            player.jump_count = 0
            player.current_platform = platform
            
            # Add landing particles
            particle_system.add_particles(
                player.rect.midbottom[0], player.rect.midbottom[1],
                (200, 200, 255), count=10, size_range=(2, 4), velocity_range=(-1, 1)
            )
            break
    else:
        player.current_platform = None
    
    # Spawn enemies
    if random.random() < 0.02 and len(enemies) < 10:
        if random.random() < 0.5:
            enemy = Enemy(random.choice([-50, SCREEN_WIDTH+50]), SCREEN_HEIGHT-30)
        else:
            enemy = JumpingEnemy(random.choice([-50, SCREEN_WIDTH+50]), SCREEN_HEIGHT-30)
        all_sprites.add(enemy)
        enemies.add(enemy)
        
    # Spawn power-ups
    if random.random() < 0.005 and len(power_ups) < 3:
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(50, SCREEN_HEIGHT-50)
        power_up_type = random.choice(["invincibility", "speed", "health"])
        power_up = PowerUp(x, y, power_up_type)
        all_sprites.add(power_up)
        power_ups.add(power_up)
        
    # Coin collection
    collected_coins = pygame.sprite.spritecollide(player, coins, True)
    for coin in collected_coins:
        score += 10
        coin_sound.play()
        
        # Add coin collection particles
        particle_system.add_particles(
            coin.rect.centerx, coin.rect.centery,
            (255, 215, 0), count=15, size_range=(2, 4), velocity_range=(-2, 2)
        )
        
        # Spawn new coin
        coin = Coin(random.randint(0, SCREEN_WIDTH), random.randint(50, SCREEN_HEIGHT-50))
        all_sprites.add(coin)
        coins.add(coin)
        
    # Power-up collection
    power_up_hits = pygame.sprite.spritecollide(player, power_ups, True)
    for power_up in power_up_hits:
        # Add collection particles
        particle_system.add_particles(
            power_up.rect.centerx, power_up.rect.centery,
            (255, 255, 255), count=15, size_range=(2, 4), velocity_range=(-2, 2)
        )
        
        if power_up.type == "invincibility":
            player.invincible = True
            player.invincibility_timer = 600  # 10 seconds at 60 FPS
            coin_sound.play()
        elif power_up.type == "speed":
            player.speed += 2
            # Reset after 5 seconds
            pygame.time.set_timer(pygame.USEREVENT, 5000)
        elif power_up.type == "health":
            player.lives = min(3, player.lives + 1)
            coin_sound.play()
        
    # Enemy collision
    if not player.invincible:
        enemy_hits = pygame.sprite.spritecollide(player, enemies, True)
        if enemy_hits:
            player.lives -= 1
            hit_sound.play()
            player.invincible = True
            player.invincibility_timer = 120
            
            # Add hit particles
            for enemy in enemy_hits:
                particle_system.add_particles(
                    enemy.rect.centerx, enemy.rect.centery,
                    (255, 50, 50), count=20, size_range=(3, 6), velocity_range=(-3, 3)
                )
            
            if player.lives <= 0:
                game_state = "game_over"
                high_score = max(high_score, score)
    
    # Draw everything
    screen.blit(background_img, (0, 0))
    
    # Draw all sprites
    all_sprites.draw(screen)
    
    # Draw particles
    particle_system.draw(screen)
    
    # Draw HUD with background
    hud_bg = pygame.Surface((200, 110))
    hud_bg.set_alpha(180)
    hud_bg.fill((0, 0, 50))
    screen.blit(hud_bg, (10, 10))
    
    # Score and lives
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {player.lives}", True, WHITE)
    high_score_text = font.render(f"High Score: {high_score}", True, YELLOW)
    
    screen.blit(score_text, (20, 20))
    screen.blit(lives_text, (20, 55))
    screen.blit(high_score_text, (20, 90))
    
    # Draw lives as hearts
    heart_x = 120
    for i in range(3):
        color = RED if i < player.lives else (50, 50, 50)
        pygame.draw.circle(screen, color, (heart_x, 40), 8)
        pygame.draw.circle(screen, color, (heart_x + 8, 40), 8)
        pygame.draw.polygon(screen, color, [
            (heart_x - 8, 40),
            (heart_x + 16, 40),
            (heart_x + 4, 54)
        ])
        heart_x += 24
    
    # Draw double jump indicator
    if player.double_jump_available and not player.on_ground:
        jump_text = small_font.render("Double Jump Available", True, (0, 200, 255))
        screen.blit(jump_text, (20, SCREEN_HEIGHT - 30))
    
    # Draw invincibility indicator
    if player.invincible:
        inv_text = small_font.render("Invincible", True, YELLOW)
        screen.blit(inv_text, (SCREEN_WIDTH - 120, 20))
    
    # Draw speed indicator
    if player.speed > 5:
        speed_text = small_font.render("Speed Boost", True, (0, 255, 0))
        screen.blit(speed_text, (SCREEN_WIDTH - 120, 50))
    
    # Update display
    pygame.display.flip()
    clock.tick(60)

# Clean up
pygame.quit()
