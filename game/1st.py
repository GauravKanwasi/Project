import pygame
import random

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill((0, 128, 255))
        self.rect = self.image.get_rect(center=(400, 500))
        self.velocity = 0
        self.jump_power = -15
        self.gravity = 0.8

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT]:
            self.rect.x += 5
        if keys[pygame.K_SPACE] and self.velocity == 0:
            self.velocity = self.jump_power

        self.velocity += self.gravity
        self.rect.y += self.velocity

        if self.rect.bottom > 600:
            self.rect.bottom = 600
            self.velocity = 0

class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((16, 16))
        pygame.draw.circle(self.image, (255, 215, 0), (8, 8), 8)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, 784)
        self.rect.y = random.randint(0, 584)

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((48, 24))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = random.choice([-48, 800])
        self.rect.y = 576
        self.speed = random.randint(3, 6) * (-1 if self.rect.x > 400 else 1)

    def update(self):
        self.rect.x += self.speed
        if self.rect.right < 0 or self.rect.left > 800:
            self.kill()

all_sprites = pygame.sprite.Group()
coins = pygame.sprite.Group()
enemies = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

for _ in range(10):
    coin = Coin()
    all_sprites.add(coin)
    coins.add(coin)

score = 0
font = pygame.font.Font(None, 36)
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    all_sprites.update()
    enemies.update()

    if random.random() < 0.02:
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)

    if pygame.sprite.spritecollide(player, coins, True):
        score += 10

    if pygame.sprite.spritecollide(player, enemies, False):
        running = False

    screen.fill((0, 0, 0))
    all_sprites.draw(screen)
    enemies.draw(screen)

    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (20, 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
