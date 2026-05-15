import pygame
import sys
import random
import json
import os
import math

# ─────────────────────────────────────────────
#  INIT
# ─────────────────────────────────────────────
pygame.init()
pygame.mixer.init()

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
SW, SH = 900, 650          # screen width / height
FPS    = 60

# Colours
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
GREEN      = (0,   255, 70)
RED        = (255, 50,  50)
YELLOW     = (255, 220, 0)
CYAN       = (0,   220, 255)
ORANGE     = (255, 140, 0)
DARK_GREEN = (0,   120, 40)
GREY       = (80,  80,  80)
BG_COLOR   = (5,   5,   20)   # deep-space navy

# Player
P_W, P_H   = 54, 36
P_SPEED    = 5

# Aliens
A_W, A_H   = 36, 28
A_ROWS     = 4
A_COLS     = 11
A_GAP_X    = 16           # horizontal gap between aliens
A_GAP_Y    = 14           # vertical gap between rows
A_DROP     = 18           # pixels to drop each time direction reverses
BASE_SPEED = 0.8          # starting horizontal speed
SPEED_STEP = 0.4          # extra speed per level

# Bullets
B_W, B_H       = 4, 14
P_BULLET_SPD   = 9        # player bullet speed (upward)
A_BULLET_SPD   = 5        # alien bullet speed (downward)
A_SHOOT_CHANCE = 0.003    # per alien per frame

# Shields
SHIELD_COUNT = 4          # number of shields across the screen
BLOCK_W, BLOCK_H = 10, 8  # size of each shield brick
# Shape template for a shield (1 = solid, 0 = gap)
SHIELD_SHAPE = [
    [0,1,1,1,1,1,1,1,1,0],
    [1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1],
    [1,1,1,0,0,0,0,1,1,1],
    [1,1,0,0,0,0,0,0,1,1],
]

# Scores per alien row (top rows worth more)
ROW_SCORES = [30, 20, 20, 10, 10]

# High-score file
HS_FILE = "si_highscores.json"

# ─────────────────────────────────────────────
#  DISPLAY
# ─────────────────────────────────────────────
screen = pygame.display.set_mode((SW, SH))
pygame.display.set_caption("Space Invaders — Enhanced")
clock = pygame.time.Clock()

font_lg  = pygame.font.SysFont("consolas", 48, bold=True)
font_md  = pygame.font.SysFont("consolas", 28, bold=True)
font_sm  = pygame.font.SysFont("consolas", 20)
font_xs  = pygame.font.SysFont("consolas", 16)

# ─────────────────────────────────────────────
#  SOUND GENERATION  (no external files needed)
# ─────────────────────────────────────────────
def _make_sound(freq=440, duration=0.1, volume=0.3, wave="square"):
    """Synthesise a simple beep so the game works without .wav files."""
    sample_rate = 44100
    n_samples   = int(sample_rate * duration)
    buf = bytearray(n_samples * 2)          # 16-bit mono
    for i in range(n_samples):
        t = i / sample_rate
        if wave == "square":
            val = 1 if math.sin(2 * math.pi * freq * t) >= 0 else -1
        else:  # sine
            val = math.sin(2 * math.pi * freq * t)
        sample = int(val * 32767 * volume)
        sample = max(-32768, min(32767, sample))
        buf[2*i]   = sample & 0xFF
        buf[2*i+1] = (sample >> 8) & 0xFF
    sound = pygame.mixer.Sound(buffer=bytes(buf))
    return sound

snd_shoot     = _make_sound(880,  0.08, 0.25, "square")
snd_explosion = _make_sound(150,  0.25, 0.40, "square")
snd_hit       = _make_sound(300,  0.15, 0.30, "square")
snd_levelup   = _make_sound(660,  0.40, 0.30, "sine")
snd_ufo       = _make_sound(1200, 0.05, 0.20, "sine")

# ─────────────────────────────────────────────
#  STARS  (parallax background)
# ─────────────────────────────────────────────
class Star:
    def __init__(self):
        self.reset(random.randint(0, SH))

    def reset(self, y=0):
        self.x     = random.randint(0, SW)
        self.y     = y
        self.speed = random.uniform(0.2, 1.0)
        self.size  = 1 if self.speed < 0.5 else 2
        self.bright = int(self.speed * 200 + 55)

    def update(self):
        self.y += self.speed
        if self.y > SH:
            self.reset()

    def draw(self, surf):
        c = (self.bright, self.bright, self.bright)
        pygame.draw.circle(surf, c, (int(self.x), int(self.y)), self.size)

stars = [Star() for _ in range(120)]

# ─────────────────────────────────────────────
#  PARTICLE EXPLOSION
# ─────────────────────────────────────────────
class Particle:
    """A single spark from an explosion."""
    def __init__(self, x, y, color):
        angle  = random.uniform(0, 2 * math.pi)
        speed  = random.uniform(1, 5)
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life   = random.randint(15, 35)
        self.color  = color
        self.radius = random.randint(2, 4)

    def update(self):
        self.x    += self.vx
        self.y    += self.vy
        self.vy   += 0.1            # gravity
        self.life -= 1

    def draw(self, surf):
        alpha = max(0, self.life / 35)
        c = tuple(int(v * alpha) for v in self.color)
        pygame.draw.circle(surf, c, (int(self.x), int(self.y)), self.radius)

particles = []

def explode(x, y, color=ORANGE, n=20):
    """Spawn n particles at (x, y)."""
    for _ in range(n):
        particles.append(Particle(x, y, color))

# ─────────────────────────────────────────────
#  FLOATING SCORE POPUP
# ─────────────────────────────────────────────
class ScorePopup:
    """Shows '+10', '+30', etc. floating upward then fading."""
    def __init__(self, x, y, text, color=YELLOW):
        self.x    = x
        self.y    = y
        self.text = text
        self.color= color
        self.life = 45

    def update(self):
        self.y   -= 1
        self.life -= 1

    def draw(self, surf):
        alpha = self.life / 45
        c = tuple(int(v * alpha) for v in self.color)
        img = font_xs.render(self.text, True, c)
        surf.blit(img, (self.x, self.y))

popups = []

# ─────────────────────────────────────────────
#  HIGH SCORES
# ─────────────────────────────────────────────
def load_hs():
    try:
        with open(HS_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_hs(scores):
    with open(HS_FILE, "w") as f:
        json.dump(scores, f)

def add_hs(score):
    hs = load_hs()
    hs.append(score)
    hs.sort(reverse=True)
    hs = hs[:5]
    save_hs(hs)
    return hs

# ─────────────────────────────────────────────
#  SHIELD BUILDER
# ─────────────────────────────────────────────
def build_shields():
    """
    Returns a list of dicts, each representing one brick of a shield.
    Bricks are placed based on SHIELD_SHAPE template.
    """
    shield_blocks = []
    total_shield_w = len(SHIELD_SHAPE[0]) * BLOCK_W
    spacing = (SW - SHIELD_COUNT * total_shield_w) // (SHIELD_COUNT + 1)

    for s in range(SHIELD_COUNT):
        sx = spacing + s * (total_shield_w + spacing)
        sy = SH - 130
        for row_i, row in enumerate(SHIELD_SHAPE):
            for col_i, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(
                        sx + col_i * BLOCK_W,
                        sy + row_i * BLOCK_H,
                        BLOCK_W, BLOCK_H
                    )
                    shield_blocks.append({"rect": rect, "hp": 3})
    return shield_blocks

# ─────────────────────────────────────────────
#  ALIEN SETUP
# ─────────────────────────────────────────────
def build_aliens(level):
    """
    Returns list of alien dicts.
    Each alien stores its rect, row index (for scoring), and animation frame.
    Speed increases with level.
    """
    aliens = []
    # Total grid width
    grid_w = A_COLS * (A_W + A_GAP_X) - A_GAP_X
    start_x = (SW - grid_w) // 2

    for row in range(A_ROWS):
        for col in range(A_COLS):
            x = start_x + col * (A_W + A_GAP_X)
            y = 70 + row * (A_H + A_GAP_Y)
            aliens.append({
                "rect":  pygame.Rect(x, y, A_W, A_H),
                "row":   row,
                "frame": random.randint(0, 1),   # animation toggle
                "tick":  random.randint(0, 30),  # stagger animation
            })
    speed = BASE_SPEED + (level - 1) * SPEED_STEP
    return aliens, speed

# ─────────────────────────────────────────────
#  DRAWING HELPERS
# ─────────────────────────────────────────────
ALIEN_COLORS = [CYAN, CYAN, GREEN, GREEN]   # color per row

def draw_alien(surf, alien, tick):
    """Draw a pixelated alien shape that toggles between two frames."""
    r   = alien["rect"]
    col = ALIEN_COLORS[alien["row"] % len(ALIEN_COLORS)]
    cx, cy = r.centerx, r.centery

    # Frame 0 / Frame 1 differ by leg position
    frame = (tick // 20) % 2

    # Body (shared)
    pygame.draw.ellipse(surf, col, (cx - 14, cy - 8, 28, 18))
    # Eyes
    pygame.draw.circle(surf, BLACK, (cx - 6, cy - 3), 4)
    pygame.draw.circle(surf, BLACK, (cx + 6, cy - 3), 4)
    pygame.draw.circle(surf, WHITE, (cx - 5, cy - 4), 2)
    pygame.draw.circle(surf, WHITE, (cx + 7, cy - 4), 2)
    # Antennae
    pygame.draw.line(surf, col, (cx - 10, cy - 8), (cx - 14, cy - 16), 2)
    pygame.draw.line(surf, col, (cx + 10, cy - 8), (cx + 14, cy - 16), 2)
    # Legs (animated)
    if frame == 0:
        pygame.draw.line(surf, col, (cx - 10, cy + 8), (cx - 14, cy + 16), 2)
        pygame.draw.line(surf, col, (cx,      cy + 8), (cx,      cy + 16), 2)
        pygame.draw.line(surf, col, (cx + 10, cy + 8), (cx + 14, cy + 16), 2)
    else:
        pygame.draw.line(surf, col, (cx - 10, cy + 8), (cx - 8,  cy + 16), 2)
        pygame.draw.line(surf, col, (cx,      cy + 8), (cx + 4,  cy + 16), 2)
        pygame.draw.line(surf, col, (cx + 10, cy + 8), (cx + 12, cy + 16), 2)


def draw_player(surf, rect, invincible_tick=0):
    """Draw the player ship as a triangle with engine glow."""
    x, y, w, h = rect.x, rect.y, rect.width, rect.height
    cx = x + w // 2

    # Flicker if briefly invincible after a hit
    if invincible_tick > 0 and (invincible_tick // 4) % 2 == 0:
        return

    # Engine glow (orange flicker beneath ship)
    glow_h = random.randint(4, 12)
    pygame.draw.rect(surf, ORANGE, (cx - 5, y + h, 10, glow_h))

    # Ship body
    points = [(cx, y), (x, y + h), (x + w, y + h)]
    pygame.draw.polygon(surf, GREEN, points)
    pygame.draw.polygon(surf, DARK_GREEN, points, 2)

    # Cockpit window
    pygame.draw.circle(surf, CYAN, (cx, y + h // 2), 6)
    pygame.draw.circle(surf, WHITE, (cx - 1, y + h // 2 - 1), 2)

    # Wing accents
    pygame.draw.line(surf, DARK_GREEN, (x + 5, y + h), (cx - 8, y + h // 2 + 4), 2)
    pygame.draw.line(surf, DARK_GREEN, (x + w - 5, y + h), (cx + 8, y + h // 2 + 4), 2)


def draw_shield_block(surf, block):
    """Colour shields from green → yellow → red based on remaining HP."""
    hp = block["hp"]
    if hp == 3:   c = GREEN
    elif hp == 2: c = YELLOW
    else:         c = RED
    pygame.draw.rect(surf, c, block["rect"])


def draw_hud(surf, score, lives, level, hi):
    """Draw score, lives, level, and high-score bar at the top."""
    # Background strip
    pygame.draw.rect(surf, (10, 10, 40), (0, 0, SW, 45))
    pygame.draw.line(surf, CYAN, (0, 45), (SW, 45), 1)

    score_txt = font_sm.render(f"SCORE  {score:06d}", True, WHITE)
    hi_txt    = font_sm.render(f"HI  {hi:06d}", True, YELLOW)
    level_txt = font_sm.render(f"LEVEL {level}", True, CYAN)
    surf.blit(score_txt, (10, 10))
    surf.blit(hi_txt,    (SW // 2 - hi_txt.get_width() // 2, 10))
    surf.blit(level_txt, (SW - level_txt.get_width() - 120, 10))

    # Draw ship icons for lives
    for i in range(lives):
        lx = SW - 40 - i * 30
        ly = 12
        pts = [(lx + 10, ly), (lx, ly + 20), (lx + 20, ly + 20)]
        pygame.draw.polygon(surf, GREEN, pts)


def draw_ground_line(surf):
    """Horizontal line just above the player to show the 'ground'."""
    pygame.draw.line(surf, GREY, (0, SH - 55), (SW, SH - 55), 1)

# ─────────────────────────────────────────────
#  UFO (mystery ship across the top)
# ─────────────────────────────────────────────
class UFO:
    WIDTH  = 60
    HEIGHT = 20
    SPEED  = 2
    POINTS = 150

    def __init__(self):
        self.active = False
        self.x      = -self.WIDTH
        self.y      = 55
        self.dir    = 1    # 1 = left→right, -1 = right→left
        self.timer  = 0    # countdown to next appearance

    def maybe_spawn(self):
        """Randomly spawn the UFO if it's not already active."""
        if not self.active:
            self.timer -= 1
            if self.timer <= 0:
                self.timer  = random.randint(600, 1800)
                self.active = True
                self.dir    = random.choice([-1, 1])
                self.x      = -self.WIDTH if self.dir == 1 else SW

    def update(self):
        if self.active:
            self.x += self.SPEED * self.dir
            snd_ufo.play()   # rapid beep while visible
            if self.x > SW + self.WIDTH or self.x < -self.WIDTH:
                self.active = False

    def draw(self, surf):
        if not self.active:
            return
        cx, cy = int(self.x) + self.WIDTH // 2, self.y
        # Saucer shape
        pygame.draw.ellipse(surf, RED, (int(self.x), cy, self.WIDTH, self.HEIGHT))
        pygame.draw.ellipse(surf, ORANGE, (int(self.x) + 10, cy - 8, self.WIDTH - 20, 16))
        # Lights
        for i in range(4):
            lx = int(self.x) + 8 + i * 14
            pygame.draw.circle(surf, YELLOW, (lx, cy + 8), 3)

    def hit_rect(self):
        return pygame.Rect(int(self.x), self.y, self.WIDTH, self.HEIGHT)

# ─────────────────────────────────────────────
#  MENU / GAME-OVER SCREENS
# ─────────────────────────────────────────────
def draw_menu(surf, hi_scores):
    surf.fill(BG_COLOR)
    for s in stars:
        s.update(); s.draw(surf)

    title = font_lg.render("SPACE  INVADERS", True, GREEN)
    surf.blit(title, (SW // 2 - title.get_width() // 2, 120))

    sub = font_md.render("Press  ENTER  to  start", True, WHITE)
    surf.blit(sub, (SW // 2 - sub.get_width() // 2, 210))

    ctrl = font_sm.render("← → Move     SPACE Shoot     H Hint", True, GREY)
    surf.blit(ctrl, (SW // 2 - ctrl.get_width() // 2, 260))

    # High scores
    hs_title = font_sm.render("TOP  SCORES", True, YELLOW)
    surf.blit(hs_title, (SW // 2 - hs_title.get_width() // 2, 320))
    for i, s in enumerate(hi_scores[:5]):
        t = font_xs.render(f"{i+1}.  {s:06d}", True, WHITE)
        surf.blit(t, (SW // 2 - t.get_width() // 2, 355 + i * 24))


def draw_gameover(surf, score, hi_scores, won=False):
    overlay = pygame.Surface((SW, SH), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surf.blit(overlay, (0, 0))

    msg   = "YOU  WIN!" if won else "GAME  OVER"
    color = CYAN       if won else RED
    title = font_lg.render(msg, True, color)
    surf.blit(title, (SW // 2 - title.get_width() // 2, SH // 2 - 100))

    sc_txt = font_md.render(f"Score:  {score:06d}", True, WHITE)
    surf.blit(sc_txt, (SW // 2 - sc_txt.get_width() // 2, SH // 2 - 20))

    hi = hi_scores[0] if hi_scores else 0
    if score >= hi:
        new_hi = font_md.render("NEW  HIGH  SCORE!", True, YELLOW)
        surf.blit(new_hi, (SW // 2 - new_hi.get_width() // 2, SH // 2 + 30))

    again = font_sm.render("Press  ENTER  to  play  again   ESC  to  quit", True, GREY)
    surf.blit(again, (SW // 2 - again.get_width() // 2, SH // 2 + 80))

# ─────────────────────────────────────────────
#  MAIN GAME LOGIC
# ─────────────────────────────────────────────
def run_game():
    hi_scores = load_hs()

    # ── game state ──
    score      = 0
    lives      = 3
    level      = 1
    tick       = 0          # global frame counter (drives animations)
    inv_tick   = 0          # invincibility frames after player hit

    player = pygame.Rect(SW // 2 - P_W // 2, SH - P_H - 10, P_W, P_H)

    aliens, alien_speed = build_aliens(level)
    alien_dir  = 1          # +1 → moving right, -1 → moving left
    shields    = build_shields()
    ufo        = UFO()

    p_bullet   = None       # only one player bullet at a time
    a_bullets  = []         # list of alien bullet rects

    game_state = "menu"     # menu → playing → gameover
    won        = False

    running = True
    while running:
        dt = clock.tick(FPS)   # ms since last frame (not used numerically but keeps FPS)
        tick += 1

        # ─── EVENTS ─────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN:

                if game_state == "menu" and event.key == pygame.K_RETURN:
                    game_state = "playing"

                elif game_state == "gameover":
                    if event.key == pygame.K_RETURN:
                        # Full reset
                        score = 0; lives = 3; level = 1; tick = 0
                        aliens, alien_speed = build_aliens(level)
                        alien_dir = 1
                        shields   = build_shields()
                        ufo       = UFO()
                        p_bullet  = None
                        a_bullets = []
                        particles.clear()
                        popups.clear()
                        player.x  = SW // 2 - P_W // 2
                        won       = False
                        game_state = "playing"
                    elif event.key == pygame.K_ESCAPE:
                        return

                elif game_state == "playing":
                    if event.key == pygame.K_SPACE and p_bullet is None:
                        # Fire player bullet from ship nose
                        bx = player.x + P_W // 2 - B_W // 2
                        by = player.y - B_H
                        p_bullet = pygame.Rect(bx, by, B_W, B_H)
                        snd_shoot.play()

                    if event.key == pygame.K_ESCAPE:
                        game_state = "menu"

        # ─── MENU ───────────────────────────────────────────────
        if game_state == "menu":
            draw_menu(screen, hi_scores)
            pygame.display.flip()
            continue

        # ─── GAMEOVER ───────────────────────────────────────────
        if game_state == "gameover":
            screen.fill(BG_COLOR)
            for s in stars: s.update(); s.draw(screen)
            draw_gameover(screen, score, hi_scores, won)
            pygame.display.flip()
            continue

        # ══════════════════════════════════════════════════════════
        #  PLAYING STATE
        # ══════════════════════════════════════════════════════════

        # ── Move player ─────────────────────────────────────────
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]  and player.x > 0:
            player.x -= P_SPEED
        if keys[pygame.K_RIGHT] and player.x < SW - P_W:
            player.x += P_SPEED

        # ── Move player bullet upward ────────────────────────────
        if p_bullet:
            p_bullet.y -= P_BULLET_SPD
            if p_bullet.y + B_H < 0:    # off-screen → remove
                p_bullet = None

        # ── Move alien bullets downward ──────────────────────────
        for b in a_bullets:
            b.y += A_BULLET_SPD
        # remove bullets that have left the screen
        a_bullets = [b for b in a_bullets if b.y < SH]

        # ── Move aliens horizontally; drop when hitting edge ─────
        hit_edge = False
        for a in aliens:
            a["rect"].x += alien_speed * alien_dir
            if a["rect"].right >= SW or a["rect"].left <= 0:
                hit_edge = True

        if hit_edge:
            alien_dir *= -1              # reverse horizontal direction
            for a in aliens:
                a["rect"].y += A_DROP   # drop all aliens one step

        # ── Alien animation tick ─────────────────────────────────
        for a in aliens:
            a["tick"] = tick

        # ── Alien shooting ───────────────────────────────────────
        for a in aliens:
            if random.random() < A_SHOOT_CHANCE:
                bx = a["rect"].centerx - B_W // 2
                by = a["rect"].bottom
                a_bullets.append(pygame.Rect(bx, by, B_W, B_H))

        # ── UFO ─────────────────────────────────────────────────
        ufo.maybe_spawn()
        ufo.update()

        # ── Collision: player bullet vs aliens ───────────────────
        if p_bullet:
            for a in aliens[:]:
                if p_bullet.colliderect(a["rect"]):
                    cx, cy = a["rect"].center
                    explode(cx, cy, CYAN, 18)
                    pts = ROW_SCORES[min(a["row"], len(ROW_SCORES) - 1)]
                    score += pts
                    popups.append(ScorePopup(cx, cy, f"+{pts}"))
                    aliens.remove(a)
                    p_bullet = None
                    snd_explosion.play()
                    break

        # ── Collision: player bullet vs UFO ─────────────────────
        if p_bullet and ufo.active:
            if p_bullet.colliderect(ufo.hit_rect()):
                cx, cy = ufo.hit_rect().center
                explode(cx, cy, RED, 30)
                score += UFO.POINTS
                popups.append(ScorePopup(cx, cy, f"+{UFO.POINTS}", RED))
                ufo.active  = False
                p_bullet    = None
                snd_explosion.play()

        # ── Collision: player bullet vs shields ──────────────────
        if p_bullet:
            for blk in shields[:]:
                if p_bullet.colliderect(blk["rect"]):
                    blk["hp"] -= 1
                    p_bullet   = None
                    if blk["hp"] <= 0:
                        shields.remove(blk)
                    break

        # ── Collision: alien bullets vs player ───────────────────
        if inv_tick <= 0:        # only take damage if not invincible
            for b in a_bullets[:]:
                if b.colliderect(player):
                    a_bullets.remove(b)
                    lives   -= 1
                    inv_tick = 120   # 2 seconds of invincibility
                    explode(player.centerx, player.centery, ORANGE, 25)
                    snd_hit.play()
                    if lives <= 0:
                        hi_scores = add_hs(score)
                        game_state = "gameover"
                        won        = False
                    break
        else:
            inv_tick -= 1

        # ── Collision: alien bullets vs shields ──────────────────
        for b in a_bullets[:]:
            for blk in shields[:]:
                if b.colliderect(blk["rect"]):
                    a_bullets.remove(b)
                    blk["hp"] -= 1
                    if blk["hp"] <= 0:
                        shields.remove(blk)
                    break

        # ── Lose condition: aliens reach the ground line ─────────
        for a in aliens:
            if a["rect"].bottom >= SH - 55:
                hi_scores  = add_hs(score)
                game_state = "gameover"
                won        = False
                break

        # ── Win condition: all aliens destroyed ──────────────────
        if not aliens:
            level += 1
            snd_levelup.play()
            aliens, alien_speed = build_aliens(level)
            alien_dir = 1
            shields   = build_shields()   # fresh shields each level
            p_bullet  = None
            a_bullets = []
            # Brief flash could be added here

        # ── Update particles and popups ──────────────────────────
        for p in particles[:]:
            p.update()
            if p.life <= 0:
                particles.remove(p)

        for pp in popups[:]:
            pp.update()
            if pp.life <= 0:
                popups.remove(pp)

        # ══════════════════════════════════════════════════════════
        #  DRAW
        # ══════════════════════════════════════════════════════════
        screen.fill(BG_COLOR)

        # Scrolling starfield
        for s in stars:
            s.update()
            s.draw(screen)

        # HUD
        hi = hi_scores[0] if hi_scores else 0
        draw_hud(screen, score, lives, level, hi)

        # Ground line
        draw_ground_line(screen)

        # Shields
        for blk in shields:
            draw_shield_block(screen, blk)

        # Aliens
        for a in aliens:
            draw_alien(screen, a, tick)

        # UFO
        ufo.draw(screen)

        # Player bullet (bright yellow streak)
        if p_bullet:
            pygame.draw.rect(screen, YELLOW, p_bullet)
            # subtle glow line above
            pygame.draw.rect(screen, WHITE,  (p_bullet.x + 1, p_bullet.y - 3, 2, 4))

        # Alien bullets (orange)
        for b in a_bullets:
            pygame.draw.rect(screen, ORANGE, b)

        # Player ship
        draw_player(screen, player, inv_tick)

        # Particles (explosions)
        for p in particles:
            p.draw(screen)

        # Floating score popups
        for pp in popups:
            pp.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    run_game()
