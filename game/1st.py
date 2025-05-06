import pygame
import random
import os
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

# Load assets
def load_asset(path):
    return pygame.image.load(os.path.join("assets", path)).convert_alpha()

try:
    # Load images
    player_img = load_asset("player.png")
    coin_img = load_asset("coin.png")
    enemy_img = load_asset("enemy.png")
    background_img = load_asset("background.png")
    platform_img = load_asset("platform.png")
    
    # Load sounds
    jump_sound = mixer.Sound(os.path.join("assets", "jump.wav"))
    coin_sound = mixer.Sound(os.path.join("assets", "coin.wav"))
    hit_sound = mixer.Sound(os.path.join("assets", "hit.wav"))
    background_music = mixer.Sound(os.path.join("assets", "background_music.mp3"))
except FileNotFoundError:
    print("Asset files not found. Using fallback graphics.")
    player_img = pygame.Surface((32, 32))
    player_img.fill((0, 128, 255))
    coin_img = pygame.Surface((16, 16))
    pygame.draw.circle(coin_img, (255, 215, 0), (8, 8), 8)
    enemy_img = pygame.Surface((48, 24))
    enemy_img.fill((255, 0, 0))
    background_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background_img.fill(BLACK)
    platform_img = pygame.Surface((100, 20))
    platform_img.fill((0, 255, 0))
    
    # Create dummy sounds
    jump_sound = mixer.Sound(pygame.mixer.Sound(100))
    coin_sound = mixer.Sound(pygame.mixer.Sound(200))
    hit_sound = mixer.Sound(pygame.mixer.Sound(300))

# Play background music
background_music.play(-1)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(player_img, (40, 40))
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
        
    def update(self):
        # Move with platform if standing on one
        if self.current_platform is not None:
            self.rect.x += self.current_platform.velocity
        
        # Horizontal movement
        keys = pygame.key.get_pressed()
        self.velocity_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity_x = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity_x = self.speed
            
        # Jump
        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.on_ground:
            self.velocity_y = self.jump_power
            self.on_ground = False
            jump_sound.play()
            
        # Apply gravity
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y
        self.rect.x += self.velocity_x
        
        # Screen boundaries
        self.rect.clamp_ip(screen.get_rect())
        
        # Ground collision
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.velocity_y = 0
            self.on_ground = True
            
        # Invincibility timer
        if self.invincible:
            self.invincibility_timer -= 1
            if self.invincibility_timer <= 0:
                self.invincible = False

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(coin_img, (20, 20))
        self.rect = self.image.get_rect(center=(x, y))
        
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(enemy_img, (50, 30))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = random.randint(3, 6) * random.choice([-1, 1])
        
    def update(self):
        self.rect.x += self.speed
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

class JumpingEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.velocity_y = 0
        self.jump_power = -10
        self.gravity = 0.5
        self.jump_timer = random.randint(60, 120)
        
    def update(self):
        super().update()  # Move horizontally
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
        
    def update(self):
        if self.velocity != 0:
            self.rect.x += self.velocity
            if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
                self.velocity *= -1

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.type = "invincibility"

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
font = pygame.font.Font(None, 36)
high_score = 0
game_state = "playing"
pause = False

# Game loop
running = True
while running:
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
                game_state = "playing"
                
    if pause or game_state != "playing":
        if game_state == "game_over":
            game_over_text = font.render("Game Over! Press R to Restart", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2))
        pygame.display.flip()
        continue
        
    # Update
    all_sprites.update()
    
    # Platform collision
    platform_hits = pygame.sprite.spritecollide(player, platforms, False)
    player.on_ground = False  # Reset each frame
    for platform in platform_hits:
        if player.rect.bottom > platform.rect.top and player.rect.top < platform.rect.bottom and player.velocity_y >= 0:
            player.rect.bottom = platform.rect.top
            player.velocity_y = 0
            player.on_ground = True
            player.current_platform = platform
            break
    else:
        player.current_platform = None
    
    # Spawn enemies
    if random.random() < 0.02:
        if random.random() < 0.5:
            enemy = Enemy(random.choice([0, SCREEN_WIDTH]), SCREEN_HEIGHT-30)
        else:
            enemy = JumpingEnemy(random.choice([0, SCREEN_WIDTH]), SCREEN_HEIGHT-30)
        all_sprites.add(enemy)
        enemies.add(enemy)
        
    # Spawn power-ups
    if random.random() < 0.005:
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(50, SCREEN_HEIGHT-50)
        power_up = PowerUp(x, y)
        all_sprites.add(power_up)
        power_ups.add(power_up)
        
    # Coin collection
    collected_coins = pygame.sprite.spritecollide(player, coins, True)
    for coin in collected_coins:
        score += 10
        coin_sound.play()
        # Spawn new coin
        coin = Coin(random.randint(0, SCREEN_WIDTH), random.randint(50, SCREEN_HEIGHT-50))
        all_sprites.add(coin)
        coins.add(coin)
        
    # Power-up collection
    power_up_hits = pygame.sprite.spritecollide(player, power_ups, True)
    for power_up in power_up_hits:
        if power_up.type == "invincibility":
            player.invincible = True
            player.invincibility_timer = 600  # 10 seconds at 60 FPS
            coin_sound.play()  # Reuse coin sound; replace if desired
        
    # Enemy collision
    if not player.invincible:
        enemy_hits = pygame.sprite.spritecollide(player, enemies, True)
        if enemy_hits:
            player.lives -= 1
            hit_sound.play()
            player.invincible = True
            player.invincibility_timer = 120
            if player.lives <= 0:
                game_state = "game_over"
                high_score = max(high_score, score)
                
    # Draw
    screen.blit(background_img, (0, 0))
    all_sprites.draw(screen)
    
    # HUD
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {player.lives}", True, WHITE)
    high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
    screen.blit(score_text, (20, 20))
    screen.blit(lives_text, (20, 50))
    screen.blit(high_score_text, (20, 80))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
