import pygame
import random
import math
import json

# ─── INIT ────────────────────────────────────────────────────────────────────
pygame.init()
pygame.mixer.init()

# ─── CONSTANTS ───────────────────────────────────────────────────────────────
SW, SH = 900, 650
FPS    = 60

GRAVITY      = 0.7
JUMP_POWER   = -15
PLAYER_SPEED = 5

# Colour palette
BLACK   = (0,   0,   0)
WHITE   = (255, 255, 255)
BLUE    = (30,  144, 255)
PURPLE  = (138, 43,  226)
YELLOW  = (255, 215, 0)
RED     = (220, 50,  50)
GREEN   = (50,  220, 100)
CYAN    = (0,   220, 255)
ORANGE  = (255, 140, 30)
GREY    = (80,  80,  80)
DARK    = (8,   8,   22)

HS_FILE = "cj_highscores.json"

# Power-up types and their display colours
PU_DEFS = {
    "invincibility": (YELLOW, "★"),
    "speed":         (GREEN,  "»"),
    "health":        (RED,    "♥"),
    "magnet":        (CYAN,   "◈"),
}

# ─── DISPLAY ─────────────────────────────────────────────────────────────────
screen = pygame.display.set_mode((SW, SH))
pygame.display.set_caption("Cosmic Jumper  ·  Enhanced")
clock  = pygame.time.Clock()

font_xl = pygame.font.SysFont("consolas", 64, bold=True)
font_lg = pygame.font.SysFont("consolas", 42, bold=True)
font_md = pygame.font.SysFont("consolas", 28, bold=True)
font_sm = pygame.font.SysFont("consolas", 20)
font_xs = pygame.font.SysFont("consolas", 15)

# ─── SYNTHESISED SOUNDS  (no .wav files needed) ───────────────────────────────
def _beep(freq=440, dur=0.08, vol=0.25, shape="square"):
    rate = 44100
    n    = int(rate * dur)
    buf  = bytearray(n * 2)
    for i in range(n):
        t = i / rate
        v = (1 if math.sin(2 * math.pi * freq * t) >= 0 else -1) if shape == "square" \
            else math.sin(2 * math.pi * freq * t)
        s = max(-32768, min(32767, int(v * 32767 * vol)))
        buf[2*i], buf[2*i+1] = s & 0xFF, (s >> 8) & 0xFF
    return pygame.mixer.Sound(buffer=bytes(buf))

snd_jump  = _beep(520,  0.06, 0.20)
snd_djump = _beep(780,  0.06, 0.20, "sine")    # higher pitch for double-jump
snd_coin  = _beep(880,  0.07, 0.18, "sine")
snd_hit   = _beep(160,  0.20, 0.35)
snd_pu    = _beep(1040, 0.12, 0.22, "sine")
snd_death = _beep(140,  0.40, 0.40)
snd_land  = _beep(220,  0.04, 0.12)

# ─── HIGH SCORES ─────────────────────────────────────────────────────────────
def load_hs():
    try:
        with open(HS_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_hs(hs):
    try:
        with open(HS_FILE, "w") as f:
            json.dump(sorted(hs, reverse=True)[:5], f)
    except Exception:
        pass

# ─── PARALLAX BACKGROUND ─────────────────────────────────────────────────────
class Star:
    """One star in the parallax starfield. Faster stars appear closer (larger)."""
    def __init__(self, y=None):
        self._spawn(y if y is not None else random.randint(0, SH))

    def _spawn(self, y=0):
        self.x     = random.randint(0, SW)
        self.y     = float(y)
        self.speed = random.uniform(0.2, 1.0)
        self.size  = 1 + int(self.speed > 0.6)
        self.lum   = int(self.speed * 160 + 60)

    def update(self):
        self.y += self.speed
        if self.y > SH:
            self._spawn()

    def draw(self, surf):
        pygame.draw.circle(surf, (self.lum,)*3, (int(self.x), int(self.y)), self.size)

stars = [Star(random.randint(0, SH)) for _ in range(160)]

def draw_bg(surf):
    surf.fill(DARK)
    for s in stars:
        s.update()
        s.draw(surf)

# ─── PARTICLES ───────────────────────────────────────────────────────────────
particles = []

def spawn_particles(x, y, color, n=12, spd=(1, 5)):
    for _ in range(n):
        a = random.uniform(0, 2 * math.pi)
        v = random.uniform(*spd)
        particles.append({
            "x": float(x), "y": float(y),
            "vx": math.cos(a) * v, "vy": math.sin(a) * v,
            "life": random.randint(20, 45),
            "max":  45,
            "r":    random.randint(2, 5),
            "col":  color,
        })

def update_draw_particles(surf):
    survivors = []
    for p in particles:
        p["x"]  += p["vx"]
        p["y"]  += p["vy"]
        p["vy"] += 0.15          # weak gravity pulls sparks downward
        p["life"] -= 1
        if p["life"] > 0:
            a = p["life"] / p["max"]
            c = tuple(max(0, int(v * a)) for v in p["col"])
            pygame.draw.circle(surf, c, (int(p["x"]), int(p["y"])), p["r"])
            survivors.append(p)
    particles[:] = survivors

# ─── FLOATING SCORE POPUP ────────────────────────────────────────────────────
popups = []

def spawn_popup(x, y, text, color=YELLOW):
    popups.append({"x": x, "y": float(y), "text": text, "col": color, "life": 55})

def update_draw_popups(surf):
    survivors = []
    for p in popups:
        p["y"]   -= 1.1
        p["life"] -= 1
        if p["life"] > 0:
            a = p["life"] / 55
            c = tuple(max(0, int(v * a)) for v in p["col"])
            img = font_xs.render(p["text"], True, c)
            surf.blit(img, (p["x"] - img.get_width() // 2, int(p["y"])))
            survivors.append(p)
    popups[:] = survivors

# ─── PLAYER ──────────────────────────────────────────────────────────────────
class Player(pygame.sprite.Sprite):
    TRAIL_LEN  = 12
    INV_FRAMES = 110     # invincibility frames after getting hit

    def __init__(self):
        super().__init__()
        # Build drawn ship sprite at runtime — no image files needed
        self.base_img = self._make_img()
        self.image    = self.base_img.copy()
        self.rect     = self.image.get_rect(center=(SW // 2, SH - 100))

        self.vx = self.vy = 0.0
        self.on_ground     = False
        self.double_avail  = True   # can we still double-jump?
        self.lives         = 3
        self.inv_t         = 0      # invincibility countdown
        self.speed         = PLAYER_SPEED
        self.speed_timer   = 0
        self.cur_platform  = None   # platform we're standing on (for moving-platform drag)
        self.magnet        = False  # magnet power-up active?
        self.magnet_timer  = 0
        self.trail         = []     # list of (x, y) for afterimage trail
        self.dir           = 1      # 1 = facing right, -1 = facing left

    @staticmethod
    def _make_img():
        """Draw a small spaceship polygon — distinct from simple rectangles."""
        s = pygame.Surface((38, 44), pygame.SRCALPHA)
        # Fuselage
        pygame.draw.polygon(s, CYAN,   [(19, 0), (4, 38), (34, 38)])
        pygame.draw.polygon(s, BLUE,   [(19, 6), (8, 36), (30, 36)])
        # Cockpit window
        pygame.draw.ellipse(s, WHITE,  (12, 10, 14, 10))
        pygame.draw.ellipse(s, CYAN,   (13, 11, 12,  8))
        # Engine glow (bottom)
        pygame.draw.ellipse(s, ORANGE, (12, 36, 14,  6))
        return s

    def update(self, platforms_group, coin_group):
        # ── Speed boost countdown ────────────────────────────────────────────
        if self.speed_timer > 0:
            self.speed_timer -= 1
            if self.speed_timer == 0:
                self.speed = PLAYER_SPEED

        # ── Magnet countdown ─────────────────────────────────────────────────
        if self.magnet_timer > 0:
            self.magnet_timer -= 1
            self.magnet = self.magnet_timer > 0
            # Pull nearby coins toward player
            if self.magnet:
                for coin in coin_group:
                    dx = self.rect.centerx - coin.rect.centerx
                    dy = self.rect.centery  - coin.rect.centery
                    dist = math.hypot(dx, dy)
                    if dist < 180 and dist > 1:
                        coin.rect.x += int(dx / dist * 4)
                        coin.rect.y += int(dy / dist * 4)

        # ── Moving-platform drag ─────────────────────────────────────────────
        if self.cur_platform:
            self.rect.x += self.cur_platform.velocity

        # ── Horizontal movement ──────────────────────────────────────────────
        keys = pygame.key.get_pressed()
        self.vx = 0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]:
            self.vx  = -self.speed
            self.dir = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx  =  self.speed
            self.dir =  1

        self.rect.x += int(self.vx)

        # Horizontal screen wrapping
        if self.rect.right < 0:        self.rect.left  = SW
        elif self.rect.left > SW:      self.rect.right = 0

        # ── Gravity & vertical movement ──────────────────────────────────────
        self.vy      += GRAVITY
        self.rect.y  += int(self.vy)

        # Ground floor
        if self.rect.bottom >= SH - 10:
            self.rect.bottom = SH - 10
            self._land()

        # ── Platform collisions ──────────────────────────────────────────────
        self.on_ground    = False
        self.cur_platform = None
        for plat in platforms_group:
            # Only land on top surface when falling downward
            if (self.vy >= 0
                    and self.rect.bottom > plat.rect.top
                    and self.rect.bottom - self.vy <= plat.rect.top + 4
                    and self.rect.right  > plat.rect.left + 4
                    and self.rect.left   < plat.rect.right - 4):
                self.rect.bottom  = plat.rect.top
                self.cur_platform = plat
                self._land()
                break

        # ── Trail (for speed-boost afterimage) ──────────────────────────────
        self.trail.append((self.rect.centerx, self.rect.centery))
        if len(self.trail) > self.TRAIL_LEN:
            self.trail.pop(0)

        # ── Invincibility flicker ────────────────────────────────────────────
        if self.inv_t > 0:
            self.inv_t -= 1
            # Alternate opacity so the player visibly blinks
            alpha = 80 if (self.inv_t // 5) % 2 == 0 else 255
        else:
            alpha = 255

        # Flip sprite horizontally when moving left
        flipped = pygame.transform.flip(self.base_img, self.dir == -1, False)
        flipped.set_alpha(alpha)
        self.image = flipped

    def _land(self):
        self.vy           = 0
        self.on_ground    = True
        self.double_avail = True

    def jump(self):
        if self.on_ground:
            self.vy        = JUMP_POWER
            self.on_ground = False
            snd_jump.play()
            spawn_particles(self.rect.centerx, self.rect.bottom, CYAN, 8, (1, 3))
        elif self.double_avail:
            # Double-jump: slightly weaker, different sound
            self.vy           = JUMP_POWER * 0.85
            self.double_avail = False
            snd_djump.play()
            spawn_particles(self.rect.centerx, self.rect.bottom, YELLOW, 12, (1, 4))

    def hurt(self):
        """Called when the player takes a hit; starts invincibility frames."""
        if self.inv_t > 0:
            return False      # still invincible — ignore hit
        self.lives -= 1
        self.inv_t  = self.INV_FRAMES
        snd_hit.play()
        spawn_particles(self.rect.centerx, self.rect.centery, RED, 25, (2, 6))
        return True

    def draw_trail(self, surf):
        """Draw faint afterimage trail (visible during speed boost)."""
        if self.speed <= PLAYER_SPEED:
            return
        for i, (tx, ty) in enumerate(self.trail):
            a = int(120 * i / len(self.trail))
            s = pygame.Surface((38, 44), pygame.SRCALPHA)
            s.fill((0, 220, 255, a))
            surf.blit(s, (tx - 19, ty - 22))

# ─── COIN ────────────────────────────────────────────────────────────────────
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y, value=10):
        super().__init__()
        self.value  = value
        self.offset = random.uniform(0, 2 * math.pi)
        self.image  = self._make_img()
        self.rect   = self.image.get_rect(center=(x, y))
        self._base_y = y   # stored so floating bob is relative to spawn

    @staticmethod
    def _make_img():
        s = pygame.Surface((22, 22), pygame.SRCALPHA)
        pygame.draw.circle(s, YELLOW,            (11, 11), 11)
        pygame.draw.circle(s, (200, 170, 0),     (11, 11),  9)
        pygame.draw.circle(s, (240, 210, 80),    ( 8,  8),  4)
        return s

    def update(self):
        # Gentle sine-wave float
        self.rect.centery = int(self._base_y + math.sin(
            pygame.time.get_ticks() / 400 + self.offset) * 5)

# ─── PLATFORM ────────────────────────────────────────────────────────────────
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, velocity=0, crumble=False):
        super().__init__()
        self.velocity  = velocity
        self.crumble   = crumble       # crumbling platforms disappear after being stood on
        self.crumble_t = 0             # countdown once player lands
        self.image     = self._make_img(w, crumble)
        self.rect      = self.image.get_rect(topleft=(x, y))

    @staticmethod
    def _make_img(w, crumble):
        s = pygame.Surface((w, 18), pygame.SRCALPHA)
        col = (180, 80, 80) if crumble else (60, 200, 120)
        dim = (100, 40, 40) if crumble else (30, 120, 60)
        pygame.draw.rect(s, col, (0, 0, w, 18), border_radius=6)
        pygame.draw.rect(s, dim, (0, 0, w, 18), width=2, border_radius=6)
        # Dashed top highlight
        for i in range(0, w - 10, 18):
            pygame.draw.line(s, WHITE, (i + 4, 4), (i + 12, 4), 1)
        return s

    def update(self):
        # Bounce moving platforms off screen edges
        if self.velocity:
            self.rect.x += self.velocity
            if self.rect.left < 0 or self.rect.right > SW:
                self.velocity *= -1

        # Crumble: start dissolving after player stands on it
        if self.crumble_t > 0:
            self.crumble_t -= 1
            # Flash red then vanish
            alpha = int(255 * self.crumble_t / 60)
            self.image.set_alpha(alpha)
            if self.crumble_t == 0:
                self.kill()

    def trigger_crumble(self):
        if self.crumble and self.crumble_t == 0:
            self.crumble_t = 60

# ─── ENEMIES ─────────────────────────────────────────────────────────────────
class Enemy(pygame.sprite.Sprite):
    """Horizontal patrol enemy that floats sinusoidally."""
    def __init__(self, x, y, spd=None):
        super().__init__()
        self.speed  = (spd or random.uniform(2, 5)) * random.choice([-1, 1])
        self.offset = random.uniform(0, 2 * math.pi)
        self.base_y = float(y)
        self.image  = self._make_img()
        self.rect   = self.image.get_rect(center=(x, y))

    @staticmethod
    def _make_img():
        s = pygame.Surface((46, 28), pygame.SRCALPHA)
        pygame.draw.ellipse(s, RED,    (0,  4, 46, 20))
        pygame.draw.ellipse(s, ORANGE, (6,  8, 34, 12))
        # Eyes
        pygame.draw.circle(s, WHITE,   (14, 10),  5)
        pygame.draw.circle(s, WHITE,   (32, 10),  5)
        pygame.draw.circle(s, BLACK,   (15, 10),  3)
        pygame.draw.circle(s, BLACK,   (33, 10),  3)
        # Tentacles
        for i, tx in enumerate([8, 18, 28, 38]):
            pygame.draw.line(s, RED, (tx, 24), (tx + (i % 2)*4 - 2, 28), 2)
        return s

    def update(self):
        self.rect.x += int(self.speed)
        # Wrap around screen edges instead of despawning
        if self.rect.right < 0:   self.rect.left  = SW
        elif self.rect.left > SW: self.rect.right = 0
        # Bob up and down
        self.rect.centery = int(self.base_y + math.sin(
            pygame.time.get_ticks() / 350 + self.offset) * 8)


class DiveEnemy(pygame.sprite.Sprite):
    """Swoops down at the player periodically."""
    DIVE_SPEED = 8

    def __init__(self, x):
        super().__init__()
        self.image  = self._make_img()
        self.rect   = self.image.get_rect(center=(x, 30))
        self.base_x = float(x)
        self.base_y = 30.0
        self.diving = False
        self.timer  = random.randint(90, 200)   # frames until next dive
        self.target_y = SH // 2

    @staticmethod
    def _make_img():
        s = pygame.Surface((34, 34), pygame.SRCALPHA)
        pygame.draw.polygon(s, PURPLE, [(17, 0), (34, 34), (17, 24), (0, 34)])
        pygame.draw.circle(s, WHITE,   (17, 12), 5)
        pygame.draw.circle(s, RED,     (17, 12), 3)
        return s

    def update(self):
        if not self.diving:
            # Hover slowly across the top
            self.base_x += 1.2
            if self.base_x > SW: self.base_x = 0
            self.rect.centerx = int(self.base_x)
            self.timer -= 1
            if self.timer <= 0:
                self.diving  = True
                self.timer   = 0
        else:
            # Dive straight down
            self.rect.y += self.DIVE_SPEED
            if self.rect.top > SH:
                # Reset back to top after completing dive
                self.rect.center = (int(self.base_x), 30)
                self.diving = False
                self.timer  = random.randint(90, 200)

# ─── POWER-UP ────────────────────────────────────────────────────────────────
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, kind):
        super().__init__()
        self.kind   = kind
        self.offset = random.uniform(0, 2 * math.pi)
        self.base_y = float(y)
        self.rot    = 0
        col, icon   = PU_DEFS[kind]
        self._orig  = self._make_img(col, icon)
        self.image  = self._orig
        self.rect   = self.image.get_rect(center=(x, y))

    @staticmethod
    def _make_img(col, icon):
        s = pygame.Surface((28, 28), pygame.SRCALPHA)
        pygame.draw.circle(s, col,   (14, 14), 14)
        pygame.draw.circle(s, WHITE, (14, 14), 14, 2)
        txt = font_xs.render(icon, True, BLACK)
        s.blit(txt, txt.get_rect(center=(14, 14)))
        return s

    def update(self):
        self.rot = (self.rot + 1.5) % 360
        self.image = pygame.transform.rotate(self._orig, self.rot)
        self.rect  = self.image.get_rect(center=(
            self.rect.centerx,
            int(self.base_y + math.sin(pygame.time.get_ticks() / 300 + self.offset) * 6)
        ))

# ─── LEVEL GENERATOR ─────────────────────────────────────────────────────────
def generate_level(level_num):
    """
    Procedurally place platforms, coins, and enemies scaled to level number.
    Higher levels: more gaps, faster enemies, crumbling platforms.
    """
    plats = []
    # Guaranteed safe ground-level platform at start
    plats.append({"x": SW // 2 - 80, "y": SH - 70, "w": 160, "v": 0, "c": False})

    rows = 5
    for row in range(rows):
        y   = SH - 130 - row * 100
        n   = random.randint(2, 4)
        xs  = sorted(random.sample(range(0, SW - 120, 60), min(n, (SW - 120) // 60)))
        for x in xs:
            w       = random.randint(80, 160)
            moving  = random.random() < 0.2 + level_num * 0.06
            crumble = random.random() < level_num * 0.07
            vel     = random.uniform(1.5, 2.5 + level_num * 0.3) * random.choice([-1, 1]) if moving else 0
            plats.append({"x": x, "y": y, "w": w, "v": vel, "c": crumble})

    # Coins: more per level
    coin_count = 12 + level_num * 3
    coins = [{"x": random.randint(40, SW - 40), "y": random.randint(60, SH - 80)}
             for _ in range(coin_count)]

    # Enemies: more and faster
    enemy_count = 2 + level_num
    enemies = [{"x": random.randint(0, SW), "y": SH - 50, "spd": 2 + level_num * 0.4}
               for _ in range(enemy_count)]

    return plats, coins, enemies

# ─── GAME STATE ──────────────────────────────────────────────────────────────
MENU      = "menu"
PLAYING   = "playing"
PAUSED    = "paused"
GAME_OVER = "gameover"
WIN       = "win"

COINS_PER_LEVEL = 30   # coins needed to advance to next level

def new_game():
    """Initialise/reset all mutable game state."""
    state = {
        "mode":     PLAYING,
        "score":    0,
        "level":    1,
        "coin_goal": COINS_PER_LEVEL,
        "coins_got": 0,
        "hs":       load_hs(),
        "all":      pygame.sprite.Group(),
        "plat_g":   pygame.sprite.Group(),
        "coin_g":   pygame.sprite.Group(),
        "enemy_g":  pygame.sprite.Group(),
        "pu_g":     pygame.sprite.Group(),
        "pu_timer": pygame.time.get_ticks(),
        "enemy_timer": pygame.time.get_ticks(),
    }
    state["player"] = Player()
    state["all"].add(state["player"])
    _load_level(state)
    return state

def _load_level(st):
    """Build sprites for the current level number."""
    for g in ("plat_g", "coin_g", "enemy_g", "pu_g"):
        st[g].empty()
    # Rebuild 'all' keeping only player
    st["all"].empty()
    st["all"].add(st["player"])

    plats, coins, enms = generate_level(st["level"])

    for p in plats:
        pl = Platform(p["x"], p["y"], p["w"], p["v"], p["c"])
        st["all"].add(pl); st["plat_g"].add(pl)

    for c in coins:
        co = Coin(c["x"], c["y"])
        st["all"].add(co); st["coin_g"].add(co)

    for e in enms:
        en = Enemy(e["x"], e["y"], e["spd"])
        st["all"].add(en); st["enemy_g"].add(en)

    # One dive enemy from level 2 onward
    if st["level"] >= 2:
        de = DiveEnemy(random.randint(100, SW - 100))
        st["all"].add(de); st["enemy_g"].add(de)

    # Reset per-level counters
    st["coins_got"]  = 0
    st["coin_goal"]  = COINS_PER_LEVEL + (st["level"] - 1) * 5
    st["pu_timer"]   = pygame.time.get_ticks()
    st["enemy_timer"]= pygame.time.get_ticks()

# ─── HUD ─────────────────────────────────────────────────────────────────────
def draw_hud(surf, st):
    pl = st["player"]
    # Semi-transparent top bar
    bar = pygame.Surface((SW, 50), pygame.SRCALPHA)
    bar.fill((10, 10, 40, 180))
    surf.blit(bar, (0, 0))
    pygame.draw.line(surf, CYAN, (0, 50), (SW, 50), 1)

    surf.blit(font_md.render(f"SCORE {st['score']:06d}", True, WHITE), (12, 10))

    hi = st["hs"][0] if st["hs"] else 0
    ht = font_sm.render(f"BEST {hi:06d}", True, YELLOW)
    surf.blit(ht, (SW // 2 - ht.get_width() // 2, 14))

    lv = font_md.render(f"LVL {st['level']}", True, CYAN)
    surf.blit(lv, (SW - lv.get_width() - 120, 10))

    # Hearts for lives
    for i in range(3):
        hx = SW - 35 - i * 28
        hy = 15
        col = RED if i < pl.lives else GREY
        pygame.draw.circle(surf, col, (hx - 5, hy + 5), 7)
        pygame.draw.circle(surf, col, (hx + 5, hy + 5), 7)
        pygame.draw.polygon(surf, col, [(hx - 12, hy + 6), (hx + 12, hy + 6), (hx, hy + 20)])

    # Coin progress bar for level goal
    bar_w = 200
    bx = SW // 2 - bar_w // 2
    by = SH - 24
    pygame.draw.rect(surf, GREY, (bx, by, bar_w, 12), border_radius=6)
    fill = int(bar_w * min(1.0, st["coins_got"] / st["coin_goal"]))
    if fill > 0:
        pygame.draw.rect(surf, YELLOW, (bx, by, fill, 12), border_radius=6)
    pygame.draw.rect(surf, WHITE, (bx, by, bar_w, 12), 1, border_radius=6)
    ct = font_xs.render(f"{st['coins_got']}/{st['coin_goal']}", True, WHITE)
    surf.blit(ct, (bx + bar_w + 6, by))

    # Active power-up indicators bottom-left
    tags = []
    if pl.speed > PLAYER_SPEED:        tags.append(("SPEED",    GREEN))
    if pl.inv_t > 0:                   tags.append(("INVINCIBLE", YELLOW))
    if pl.magnet:                      tags.append(("MAGNET",   CYAN))
    if pl.double_avail and not pl.on_ground: tags.append(("2×JUMP", WHITE))
    for i, (tag, col) in enumerate(tags):
        t = font_xs.render(f"◆ {tag}", True, col)
        surf.blit(t, (12, SH - 22 - i * 18))

# ─── OVERLAY SCREENS ─────────────────────────────────────────────────────────
def draw_overlay(surf, lines):
    """Generic semi-transparent overlay with centred lines: (text, font, colour, y_offset)."""
    ov = pygame.Surface((SW, SH), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 160))
    surf.blit(ov, (0, 0))
    for text, fnt, col, yo in lines:
        img = fnt.render(text, True, col)
        surf.blit(img, (SW // 2 - img.get_width() // 2, SH // 2 + yo))

def draw_menu(surf):
    draw_bg(surf)
    hs = load_hs()
    hi = hs[0] if hs else 0
    draw_overlay(surf, [
        ("COSMIC  JUMPER",           font_xl, CYAN,   -200),
        ("Collect coins  ·  Dodge enemies",  font_sm, GREY,  -120),
        ("ENTER  ·  Start Game",     font_md, GREEN,  -60),
        ("ESC    ·  Quit",           font_sm, GREY,   -20),
        (f"BEST  {hi:06d}",          font_md, YELLOW,  40),
        ("← → / A D  Move",          font_xs, GREY,   100),
        ("SPACE / W  Jump (×2)",     font_xs, GREY,   122),
        ("P  Pause",                 font_xs, GREY,   144),
    ])

def draw_gameover(surf, st):
    draw_overlay(surf, [
        ("GAME  OVER",               font_xl, RED,    -180),
        (f"Score  {st['score']:06d}", font_lg, WHITE,  -90),
        (f"Level  {st['level']}",    font_md, CYAN,   -30),
        ("R  ·  Restart",            font_md, GREEN,   40),
        ("ESC  ·  Menu",             font_sm, GREY,    90),
    ])

def draw_win(surf, st):
    draw_overlay(surf, [
        ("LEVEL  CLEAR!",             font_xl, GREEN,  -180),
        (f"Score  {st['score']:06d}", font_lg, WHITE,   -90),
        ("ENTER  ·  Next Level",      font_md, CYAN,    -20),
        ("ESC    ·  Menu",            font_sm, GREY,     30),
    ])

def draw_pause(surf):
    draw_overlay(surf, [
        ("PAUSED",          font_xl, WHITE,  -80),
        ("P  ·  Resume",    font_md, GREY,   10),
        ("ESC  ·  Menu",    font_sm, GREY,   60),
    ])

# ─── MAIN LOOP ───────────────────────────────────────────────────────────────
hs      = load_hs()
mode    = MENU
st      = None
fade    = 0.0

running = True
while running:
    dt = clock.tick(FPS) / 1000.0

    # ── EVENTS ───────────────────────────────────────────────────────────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if mode == MENU:
                if event.key == pygame.K_RETURN:
                    st   = new_game()
                    mode = PLAYING
                elif event.key == pygame.K_ESCAPE:
                    running = False

            elif mode == PLAYING:
                if event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                    st["player"].jump()
                elif event.key == pygame.K_p:
                    mode = PAUSED
                elif event.key == pygame.K_ESCAPE:
                    mode = MENU

            elif mode == PAUSED:
                if event.key == pygame.K_p:
                    mode = PLAYING
                elif event.key == pygame.K_ESCAPE:
                    mode = MENU

            elif mode == GAME_OVER:
                if event.key == pygame.K_r:
                    st   = new_game()
                    mode = PLAYING
                elif event.key == pygame.K_ESCAPE:
                    mode = MENU

            elif mode == WIN:
                if event.key == pygame.K_RETURN:
                    st["level"] += 1
                    st["player"].rect.center = (SW // 2, SH - 100)
                    st["player"].vy = 0
                    _load_level(st)
                    mode = PLAYING
                elif event.key == pygame.K_ESCAPE:
                    mode = MENU

    # ── MENU / OVERLAY ───────────────────────────────────────────────────────
    if mode == MENU:
        draw_menu(screen)
        pygame.display.flip()
        continue

    if mode in (PAUSED, GAME_OVER, WIN):
        # Render frozen game world beneath overlay
        draw_bg(screen)
        st["all"].draw(screen)
        if   mode == PAUSED:    draw_pause(screen)
        elif mode == GAME_OVER: draw_gameover(screen, st)
        elif mode == WIN:       draw_win(screen, st)
        pygame.display.flip()
        continue

    # ══════════════════════════════════════════════════════════════════════════
    #  PLAYING
    # ══════════════════════════════════════════════════════════════════════════
    pl = st["player"]

    # ── Update all sprites ───────────────────────────────────────────────────
    # Player update needs both platform group (for landing) and coin group (for magnet)
    pl.update(st["plat_g"], st["coin_g"])

    # Trigger crumble on platforms the player is standing on
    if pl.cur_platform and hasattr(pl.cur_platform, "trigger_crumble"):
        pl.cur_platform.trigger_crumble()

    st["plat_g"].update()
    st["coin_g"].update()
    st["enemy_g"].update()
    st["pu_g"].update()

    # ── Spawn enemies over time ──────────────────────────────────────────────
    now = pygame.time.get_ticks()
    spawn_interval = max(2000, 5000 - st["level"] * 300)   # faster spawns at higher levels
    if now - st["enemy_timer"] > spawn_interval and len(st["enemy_g"]) < 6 + st["level"]:
        en = Enemy(random.choice([-60, SW + 60]), SH - 50)
        st["all"].add(en); st["enemy_g"].add(en)
        st["enemy_timer"] = now

    # ── Spawn power-ups ──────────────────────────────────────────────────────
    if now - st["pu_timer"] > 12000 and len(st["pu_g"]) < 2:
        kind = random.choice(list(PU_DEFS.keys()))
        pu   = PowerUp(random.randint(60, SW - 60), random.randint(80, SH - 100), kind)
        st["all"].add(pu); st["pu_g"].add(pu)
        st["pu_timer"] = now

    # ── Coin collection ──────────────────────────────────────────────────────
    for coin in pygame.sprite.spritecollide(pl, st["coin_g"], True):
        st["score"]    += coin.value
        st["coins_got"] += 1
        snd_coin.play()
        spawn_particles(coin.rect.centerx, coin.rect.centery, YELLOW, 10, (1, 4))
        spawn_popup(coin.rect.centerx, coin.rect.centery, f"+{coin.value}")
        # Respawn a new coin at a random position to keep supply constant
        nc = Coin(random.randint(40, SW - 40), random.randint(60, SH - 100))
        st["all"].add(nc); st["coin_g"].add(nc)

    # ── Power-up collection ──────────────────────────────────────────────────
    for pu in pygame.sprite.spritecollide(pl, st["pu_g"], True):
        snd_pu.play()
        spawn_particles(pu.rect.centerx, pu.rect.centery, WHITE, 18, (2, 5))
        spawn_popup(pu.rect.centerx, pu.rect.centery, pu.kind.upper(), PU_DEFS[pu.kind][0])
        if pu.kind == "invincibility":
            pl.inv_t = 360               # 6 seconds at 60 FPS
        elif pu.kind == "speed":
            pl.speed       = PLAYER_SPEED + 4
            pl.speed_timer = 300         # 5 seconds
        elif pu.kind == "health":
            pl.lives = min(5, pl.lives + 1)
        elif pu.kind == "magnet":
            pl.magnet       = True
            pl.magnet_timer = 420        # 7 seconds

    # ── Enemy collision ──────────────────────────────────────────────────────
    if pl.inv_t == 0:    # skip check while invincible
        for en in pygame.sprite.spritecollide(pl, st["enemy_g"], False):
            hit = pl.hurt()
            if hit:
                if pl.lives <= 0:
                    snd_death.play()
                    hs.append(st["score"])
                    save_hs(hs)
                    st["hs"] = load_hs()
                    mode = GAME_OVER
                break

    # ── Level complete check ──────────────────────────────────────────────────
    if st["coins_got"] >= st["coin_goal"]:
        mode = WIN

    # ── DRAW ─────────────────────────────────────────────────────────────────
    draw_bg(screen)
    pl.draw_trail(screen)
    st["all"].draw(screen)
    update_draw_particles(screen)
    update_draw_popups(screen)
    draw_hud(screen, st)
    pygame.display.flip()

# ─── SHUTDOWN ────────────────────────────────────────────────────────────────
if st:
    hs.append(st["score"])
    save_hs(hs)
pygame.quit()
