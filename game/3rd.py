import pygame
import sys
import random
import math
import json

pygame.init()
pygame.mixer.init()

# ─── CONSTANTS ────────────────────────────────────────────────────────────────
WIDTH, HEIGHT       = 900, 650
PADDLE_W, PADDLE_H  = 12, 100
BALL_SIZE            = 18
FPS                  = 60

# Colour palette
BLACK   = (0,   0,   0)
WHITE   = (255, 255, 255)
GREY    = (60,  60,  60)
BLUE    = (0,   120, 255)
RED     = (255, 60,  60)
GREEN   = (60,  255, 120)
YELLOW  = (255, 230, 50)
PURPLE  = (160, 60,  255)
ORANGE  = (255, 140, 30)
CYAN    = (0,   220, 255)
BG      = (8,   8,   22)

COLORS      = [WHITE, RED, GREEN, BLUE, YELLOW, PURPLE, CYAN, ORANGE]
COLOR_NAMES = {WHITE:"White", RED:"Red", GREEN:"Green", BLUE:"Blue",
               YELLOW:"Yellow", PURPLE:"Purple", CYAN:"Cyan", ORANGE:"Orange"}

# Game-state tokens
MENU      = 0
PLAYING   = 1
PAUSED    = 2
GAME_OVER = 3
SETTINGS  = 4

DIFFICULTIES = {
    "Easy":   {"paddle_speed": 5,  "ball_speed": 4, "ai_accuracy": 0.60, "ai_reaction": 0.30},
    "Medium": {"paddle_speed": 7,  "ball_speed": 6, "ai_accuracy": 0.82, "ai_reaction": 0.18},
    "Hard":   {"paddle_speed": 10, "ball_speed": 9, "ai_accuracy": 0.96, "ai_reaction": 0.08},
}

HS_FILE = "pong_highscores.json"

# ─── DISPLAY ──────────────────────────────────────────────────────────────────
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong  ·  Enhanced")
clock  = pygame.time.Clock()

font_xl  = pygame.font.SysFont("consolas", 72, bold=True)
font_lg  = pygame.font.SysFont("consolas", 48, bold=True)
font_md  = pygame.font.SysFont("consolas", 30, bold=True)
font_sm  = pygame.font.SysFont("consolas", 22)
font_xs  = pygame.font.SysFont("consolas", 16)

# ─── SYNTHESISED SOUNDS  (no .wav files required) ─────────────────────────────
def _beep(freq=440, dur=0.08, vol=0.25, shape="square"):
    rate = 44100
    n    = int(rate * dur)
    buf  = bytearray(n * 2)
    for i in range(n):
        t = i / rate
        if shape == "square":
            v = 1 if math.sin(2 * math.pi * freq * t) >= 0 else -1
        else:
            v = math.sin(2 * math.pi * freq * t)
        s = max(-32768, min(32767, int(v * 32767 * vol)))
        buf[2*i], buf[2*i+1] = s & 0xFF, (s >> 8) & 0xFF
    return pygame.mixer.Sound(buffer=bytes(buf))

snd_paddle = _beep(480,  0.07, 0.25)
snd_wall   = _beep(240,  0.05, 0.18)
snd_score  = _beep(160,  0.22, 0.35, "square")
snd_menu   = _beep(380,  0.05, 0.15, "sine")
snd_pu     = _beep(880,  0.12, 0.20, "sine")
snd_lvlup  = _beep(660,  0.35, 0.25, "sine")

# ─── HIGH SCORES ──────────────────────────────────────────────────────────────
def load_hs():
    try:
        with open(HS_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_hs(hs):
    try:
        with open(HS_FILE, "w") as f:
            json.dump(hs[:5], f)
    except Exception:
        pass

high_scores = load_hs()

# ─── PARTICLES ────────────────────────────────────────────────────────────────
particles = []

def spawn_particles(x, y, color, n=14):
    for _ in range(n):
        a = random.uniform(0, 2 * math.pi)
        s = random.uniform(1.5, 6)
        particles.append({
            "x": x, "y": y,
            "vx": math.cos(a) * s,
            "vy": math.sin(a) * s,
            "life": random.randint(18, 38),
            "max":  random.randint(18, 38),
            "r":    random.randint(3, 6),
            "col":  color,
        })

def update_draw_particles(surf):
    survivors = []
    for p in particles:
        p["x"] += p["vx"];  p["y"] += p["vy"];  p["vy"] += 0.12
        p["life"] -= 1
        if p["life"] > 0:
            alpha = p["life"] / p["max"]
            c = tuple(int(v * alpha) for v in p["col"])
            pygame.draw.circle(surf, c, (int(p["x"]), int(p["y"])), p["r"])
            survivors.append(p)
    particles[:] = survivors

# ─── SCORE POPUPS ─────────────────────────────────────────────────────────────
popups = []

def spawn_popup(x, y, text, color=YELLOW):
    popups.append({"x": x, "y": y, "text": text, "col": color, "life": 50})

def update_draw_popups(surf):
    survivors = []
    for p in popups:
        p["y"] -= 1.2;  p["life"] -= 1
        if p["life"] > 0:
            a = p["life"] / 50
            c = tuple(int(v * a) for v in p["col"])
            img = font_xs.render(p["text"], True, c)
            surf.blit(img, (p["x"], p["y"]))
            survivors.append(p)
    popups[:] = survivors

# ─── STARS (parallax background) ──────────────────────────────────────────────
class Star:
    def __init__(self, y=None):
        self._spawn(y if y is not None else random.randint(0, HEIGHT))

    def _spawn(self, y=0):
        self.x     = random.randint(0, WIDTH)
        self.y     = float(y)
        self.speed = random.uniform(0.15, 0.9)
        self.size  = 1 + int(self.speed > 0.55)
        self.lum   = int(self.speed * 180 + 50)

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self._spawn()

    def draw(self, surf):
        c = (self.lum,) * 3
        pygame.draw.circle(surf, c, (int(self.x), int(self.y)), self.size)

stars = [Star(random.randint(0, HEIGHT)) for _ in range(140)]

# ─── UFO ──────────────────────────────────────────────────────────────────────
class UFO:
    W, H, SPD, PTS = 58, 18, 2, 200

    def __init__(self):
        self.active = False
        self.timer  = random.randint(700, 1800)
        self.x = self.y = 0
        self.dir = 1

    def tick(self):
        if not self.active:
            self.timer -= 1
            if self.timer <= 0:
                self.dir    = random.choice([-1, 1])
                self.x      = -self.W if self.dir == 1 else WIDTH
                self.y      = 60
                self.active = True
                self.timer  = random.randint(700, 1800)
        else:
            self.x += self.SPD * self.dir
            if self.x > WIDTH + self.W or self.x < -self.W:
                self.active = False

    def draw(self, surf):
        if not self.active:
            return
        cx = int(self.x) + self.W // 2
        pygame.draw.ellipse(surf, RED,    (int(self.x),      self.y,      self.W,      self.H))
        pygame.draw.ellipse(surf, ORANGE, (int(self.x) + 10, self.y - 7,  self.W - 20, 14))
        for i in range(4):
            pygame.draw.circle(surf, YELLOW, (int(self.x) + 7 + i * 14, self.y + 9), 3)

    def hitbox(self):
        return pygame.Rect(int(self.x), self.y, self.W, self.H)

# ─── SHIELDS ──────────────────────────────────────────────────────────────────
# Template for each shield — 1 = solid brick, 0 = gap
SHIELD_SHAPE = [
    [0,1,1,1,1,1,1,1,0],
    [1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1],
    [1,1,0,0,0,0,0,1,1],
    [1,0,0,0,0,0,0,0,1],
]
BLK_W, BLK_H = 11, 8

def build_shields():
    blocks = []
    cols   = len(SHIELD_SHAPE[0])
    sw     = cols * BLK_W
    n      = 4
    gap    = (WIDTH - n * sw) // (n + 1)
    sy     = HEIGHT - 140
    for s in range(n):
        ox = gap + s * (sw + gap)
        for ri, row in enumerate(SHIELD_SHAPE):
            for ci, cell in enumerate(row):
                if cell:
                    blocks.append({
                        "rect": pygame.Rect(ox + ci * BLK_W, sy + ri * BLK_H, BLK_W, BLK_H),
                        "hp": 3,
                    })
    return blocks

def draw_shields(surf, blocks):
    HP_COL = {3: GREEN, 2: YELLOW, 1: RED}
    for b in blocks:
        pygame.draw.rect(surf, HP_COL[b["hp"]], b["rect"])

# ─── POWER-UPS ────────────────────────────────────────────────────────────────
PU_TYPES = ["paddle_grow", "paddle_shrink", "ball_slow", "ball_fast", "multi_ball", "invisibility"]
PU_ICONS = {"paddle_grow":"▲", "paddle_shrink":"▼", "ball_slow":"●", "ball_fast":"★", "multi_ball":"✦", "invisibility":"?"}
PU_COLS  = {"paddle_grow": GREEN, "paddle_shrink": RED, "ball_slow": CYAN,
            "ball_fast": ORANGE, "multi_ball": PURPLE, "invisibility": GREY}

# ─── GAME STATE ───────────────────────────────────────────────────────────────
def fresh_state(difficulty="Medium"):
    cfg = DIFFICULTIES[difficulty]
    spd = cfg["ball_speed"]
    ang = random.uniform(-math.pi / 5, math.pi / 5)
    drc = random.choice([-1, 1])
    return {
        "diff": difficulty,
        "cfg":  cfg,
        "lpy":  float((HEIGHT - PADDLE_H) // 2),
        "rpy":  float((HEIGHT - PADDLE_H) // 2),
        "lpv":  0.0,
        "rpv":  0.0,
        "balls": [{
            "x": WIDTH / 2, "y": HEIGHT / 2,
            "vx": spd * math.cos(ang) * drc,
            "vy": spd * math.sin(ang),
            "trail": [], "visible": True,
        }],
        "ls": 0, "rs": 0,
        "hits": 0,
        "pu_items":  [],
        "pu_active": {"size": 1.0, "speed": 1.0, "n_balls": 1, "invis": False},
        "pu_timer":  pygame.time.get_ticks(),
        "pu_reset":  pygame.time.get_ticks(),
        "start":     pygame.time.get_ticks(),
        "match_ms":  0,
        "shake":     0,
        "shields":   build_shields(),
        "ufo":       UFO(),
        "score":     0,   # running point total (distinct from rally score)
    }

# ─── BALL RESET ───────────────────────────────────────────────────────────────
def reset_balls(gs):
    spd = gs["cfg"]["ball_speed"]
    n   = gs["pu_active"]["n_balls"]
    gs["balls"] = []
    for _ in range(n):
        ang = random.uniform(-math.pi / 5, math.pi / 5)
        drc = random.choice([-1, 1])
        gs["balls"].append({
            "x": WIDTH / 2, "y": HEIGHT / 2,
            "vx": spd * math.cos(ang) * drc,
            "vy": spd * math.sin(ang),
            "trail": [], "visible": True,
        })
    gs["hits"] = 0

# ─── DRAWING ──────────────────────────────────────────────────────────────────
def draw_bg(surf):
    surf.fill(BG)
    for s in stars:
        s.update(); s.draw(surf)

def draw_net(surf):
    pulse = 0.6 + 0.4 * (math.sin(pygame.time.get_ticks() / 900) * 0.5 + 0.5)
    c = tuple(int(80 * pulse) for _ in range(3))
    for y in range(0, HEIGHT, 22):
        pygame.draw.rect(surf, c, (WIDTH // 2 - 1, y, 2, 12))

def draw_paddles(surf, gs):
    ph = int(PADDLE_H * gs["pu_active"]["size"])
    for i in range(3):
        # glow layers (alpha decreases with distance from paddle)
        ga = 40 - i * 12
        for xp, yp, col in ((0, gs["lpy"], lp_col), (WIDTH - PADDLE_W, gs["rpy"], rp_col)):
            s = pygame.Surface((PADDLE_W + i * 6, ph + i * 6), pygame.SRCALPHA)
            pygame.draw.rect(s, (*col, ga), s.get_rect())
            surf.blit(s, (xp - i * 3, yp - i * 3))
    # Solid paddles
    pygame.draw.rect(surf, lp_col, (0,             gs["lpy"], PADDLE_W, ph))
    pygame.draw.rect(surf, rp_col, (WIDTH - PADDLE_W, gs["rpy"], PADDLE_W, ph))

def draw_ball_obj(surf, ball, pu):
    if ball["visible"] is False and pu["invis"]:
        return
    # Trail fades from transparent to opaque
    for i, (tx, ty) in enumerate(ball["trail"]):
        frac  = i / max(len(ball["trail"]), 1)
        alpha = int(frac * 180)
        r     = max(2, int(BALL_SIZE * 0.3 + BALL_SIZE * 0.5 * frac))
        s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (*ball_col, alpha), (0, 0, r * 2, r * 2))
        surf.blit(s, (tx - r, ty - r))
    # Main ball with soft glow
    for g in (2, 0):
        r = BALL_SIZE // 2 + g
        s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        a = 80 if g else 255
        pygame.draw.ellipse(s, (*ball_col, a), (0, 0, r * 2, r * 2))
        surf.blit(s, (int(ball["x"]) - r, int(ball["y"]) - r))

def draw_hud(surf, gs):
    pygame.draw.rect(surf, (12, 12, 38), (0, 0, WIDTH, 48))
    pygame.draw.line(surf, CYAN, (0, 48), (WIDTH, 48), 1)
    hi = high_scores[0] if high_scores else 0
    surf.blit(font_md.render(f"{gs['ls']:02d}", True, lp_col), (WIDTH // 4 - 20, 8))
    surf.blit(font_md.render(f"{gs['rs']:02d}", True, rp_col), (3 * WIDTH // 4 - 10, 8))
    hi_t = font_xs.render(f"HI {hi:04d}", True, YELLOW)
    surf.blit(hi_t, (WIDTH // 2 - hi_t.get_width() // 2, 16))
    # Life icons
    for i in range(lives):
        lx = WIDTH - 30 - i * 22
        pts = [(lx + 8, 6), (lx, 42), (lx + 16, 42)]
        pygame.draw.polygon(surf, GREEN, pts)

def draw_pu_status(surf, pu):
    lines = []
    if pu["size"]   != 1.0:  lines.append(f"Paddle {'↑' if pu['size'] > 1 else '↓'}")
    if pu["speed"]  != 1.0:  lines.append(f"Ball {'slow' if pu['speed'] < 1 else 'fast'}")
    if pu["n_balls"] > 1:    lines.append(f"×{pu['n_balls']} balls")
    if pu["invis"]:           lines.append("Invisible")
    for i, ln in enumerate(lines):
        surf.blit(font_xs.render(ln, True, CYAN), (8, HEIGHT - 20 - i * 18))

def draw_ground(surf):
    pygame.draw.line(surf, GREY, (0, HEIGHT - 50), (WIDTH, HEIGHT - 50), 1)

# ─── PHYSICS ──────────────────────────────────────────────────────────────────
def move_paddles(gs, keys, dt, two_player):
    ph   = PADDLE_H * gs["pu_active"]["size"]
    spd  = gs["cfg"]["paddle_speed"]
    acc  = spd * 18
    fric = 0.88

    # Left paddle — always human (W/S)
    tv = 0
    if keys[pygame.K_w] and gs["lpy"] > 0:         tv = -spd
    if keys[pygame.K_s] and gs["lpy"] < HEIGHT - ph: tv =  spd
    gs["lpv"] += (tv - gs["lpv"]) * acc * dt
    gs["lpv"] *= fric
    gs["lpy"]  = max(0, min(HEIGHT - ph, gs["lpy"] + gs["lpv"]))

    if two_player:
        tv = 0
        if keys[pygame.K_UP]   and gs["rpy"] > 0:          tv = -spd
        if keys[pygame.K_DOWN] and gs["rpy"] < HEIGHT - ph: tv =  spd
        gs["rpv"] += (tv - gs["rpv"]) * acc * dt
        gs["rpv"] *= fric
        gs["rpy"]  = max(0, min(HEIGHT - ph, gs["rpy"] + gs["rpv"]))
    else:
        # AI: predict where ball will be when it crosses the right side
        target = HEIGHT / 2
        for ball in gs["balls"]:
            if ball["vx"] > 0:
                t = (WIDTH - PADDLE_W - ball["x"]) / max(ball["vx"], 0.1)
                py = ball["y"] + ball["vy"] * t
                # Simulate wall bounces in prediction
                while py < 0 or py > HEIGHT:
                    py = -py if py < 0 else 2 * HEIGHT - py
                target = py
                break
        if random.random() > gs["cfg"]["ai_accuracy"]:
            target += random.uniform(-60, 60)
        center = gs["rpy"] + ph / 2
        if center < target - 5:   gs["rpv"] += acc * dt
        elif center > target + 5: gs["rpv"] -= acc * dt
        gs["rpv"] *= fric
        # ai_reaction reduces how quickly it converges
        gs["rpy"] = max(0, min(HEIGHT - ph, gs["rpy"] + gs["rpv"] * (1 - gs["cfg"]["ai_reaction"])))

def step_ball(ball, gs):
    """Move one ball, handle wall/paddle/shield collisions. Returns False if it scored."""
    pu  = gs["pu_active"]
    ph  = PADDLE_H * pu["size"]
    spd = pu["speed"]
    vx  = ball["vx"] * spd
    vy  = ball["vy"] * spd

    ball["x"] += vx
    ball["y"] += vy
    ball["trail"].append((ball["x"], ball["y"]))
    if len(ball["trail"]) > 10:
        ball["trail"].pop(0)

    # Top / bottom wall bounce
    if ball["y"] <= BALL_SIZE / 2:
        ball["y"] = BALL_SIZE / 2
        ball["vy"] = abs(ball["vy"])
        spawn_particles(ball["x"], ball["y"], YELLOW, 5)
        snd_wall.play()
        gs["shake"] = 4

    elif ball["y"] >= HEIGHT - BALL_SIZE / 2:
        ball["y"] = HEIGHT - BALL_SIZE / 2
        ball["vy"] = -abs(ball["vy"])
        spawn_particles(ball["x"], ball["y"], YELLOW, 5)
        snd_wall.play()
        gs["shake"] = 4

    # Left paddle collision
    if ball["x"] - BALL_SIZE / 2 <= PADDLE_W and gs["lpy"] <= ball["y"] <= gs["lpy"] + ph:
        rel    = (ball["y"] - (gs["lpy"] + ph / 2)) / ph
        spd_s  = math.hypot(ball["vx"], ball["vy"]) * 1.04
        ang    = rel * math.pi / 3
        ball["vx"] =  abs(spd_s * math.cos(ang))
        ball["vy"] =  spd_s * math.sin(ang) + gs["lpv"] * 0.25
        ball["x"]  = PADDLE_W + BALL_SIZE / 2
        gs["hits"] += 1
        gs["score"] += 1
        spawn_particles(ball["x"], ball["y"], lp_col, 16)
        snd_paddle.play()
        gs["shake"] = 7

    # Right paddle collision
    elif ball["x"] + BALL_SIZE / 2 >= WIDTH - PADDLE_W and gs["rpy"] <= ball["y"] <= gs["rpy"] + ph:
        rel    = (ball["y"] - (gs["rpy"] + ph / 2)) / ph
        spd_s  = math.hypot(ball["vx"], ball["vy"]) * 1.04
        ang    = rel * math.pi / 3
        ball["vx"] = -abs(spd_s * math.cos(ang))
        ball["vy"] =  spd_s * math.sin(ang) + gs["rpv"] * 0.25
        ball["x"]  = WIDTH - PADDLE_W - BALL_SIZE / 2
        gs["hits"] += 1
        gs["score"] += 1
        spawn_particles(ball["x"], ball["y"], rp_col, 16)
        snd_paddle.play()
        gs["shake"] = 7

    # Shield collisions — erode bricks the ball passes through
    for blk in gs["shields"][:]:
        if blk["rect"].collidepoint(ball["x"], ball["y"]):
            blk["hp"] -= 1
            if blk["hp"] <= 0:
                gs["shields"].remove(blk)
            ball["vy"] = -ball["vy"]
            break

    # Scored on left side → right player gets a point
    if ball["x"] < 0:
        gs["rs"] += 1
        spawn_particles(0, ball["y"], RED, 22)
        snd_score.play()
        gs["shake"] = 12
        return False

    # Scored on right side → left player gets a point
    if ball["x"] > WIDTH:
        gs["ls"] += 1
        spawn_particles(WIDTH, ball["y"], RED, 22)
        snd_score.play()
        gs["shake"] = 12
        return False

    return True

# ─── POWER-UP LOGIC ───────────────────────────────────────────────────────────
def update_power_ups(gs):
    now = pygame.time.get_ticks()

    # Spawn a new power-up every ~15 s (max 3 on screen)
    if now - gs["pu_timer"] > 15_000 and len(gs["pu_items"]) < 3:
        gs["pu_items"].append({
            "x": random.randint(WIDTH // 4, 3 * WIDTH // 4),
            "y": random.randint(80, HEIGHT - 80),
            "type": random.choice(PU_TYPES),
        })
        gs["pu_timer"] = now

    # Check ball collection
    for item in gs["pu_items"][:]:
        for ball in gs["balls"]:
            if math.hypot(ball["x"] - item["x"], ball["y"] - item["y"]) < 22:
                _apply_pu(gs, item["type"])
                gs["pu_items"].remove(item)
                snd_pu.play()
                spawn_popup(item["x"], item["y"], PU_ICONS[item["type"]], PU_COLS[item["type"]])
                break

    # Reset active effects after 10 s
    if now - gs["pu_reset"] > 10_000:
        gs["pu_active"] = {"size": 1.0, "speed": 1.0, "n_balls": 1, "invis": False}
        reset_balls(gs)
        gs["pu_reset"] = now

def _apply_pu(gs, kind):
    pu = gs["pu_active"]
    if   kind == "paddle_grow":   pu["size"]    = 1.5
    elif kind == "paddle_shrink": pu["size"]    = 0.65
    elif kind == "ball_slow":     pu["speed"]   = 0.65
    elif kind == "ball_fast":     pu["speed"]   = 1.4
    elif kind == "multi_ball":
        pu["n_balls"] = min(3, pu["n_balls"] + 1)
        reset_balls(gs)
    elif kind == "invisibility":  pu["invis"]   = True

def draw_pu_items(surf, items):
    t = pygame.time.get_ticks()
    for item in items:
        scale = 1 + 0.12 * math.sin(t / 280)
        r     = int(14 * scale)
        col   = PU_COLS[item["type"]]
        pygame.draw.circle(surf, col, (item["x"], item["y"]), r, 2)
        pygame.draw.circle(surf, (*col, 60), (item["x"], item["y"]), r)
        icon = font_xs.render(PU_ICONS[item["type"]], True, WHITE)
        surf.blit(icon, icon.get_rect(center=(item["x"], item["y"])))

# ─── MENU SCREENS ─────────────────────────────────────────────────────────────
main_opts = [
    "Start Game",
    "Two Player: Off",
    f"Difficulty: Medium",
    "Points to Win: 10",
    "Settings",
    "Exit",
]
set_opts = [
    "Sound: On",
    "Screen Shake: On",
    "Left Paddle: White",
    "Right Paddle: White",
    "Ball Color: White",
    "Back",
]
sel       = 0
fade      = 0.0
two_player = False
win_score  = 10
diff       = "Medium"
sound_on   = True
shake_on   = True
lp_col     = WHITE
rp_col     = WHITE
ball_col   = WHITE
lives      = 3

def draw_menu_screen(surf, state):
    global fade
    draw_bg(surf)
    fade = min(fade + 0.04, 1.0)

    title = font_lg.render("PONG  ·  ENHANCED", True, GREEN)
    title.set_alpha(int(255 * fade))
    surf.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

    opts = main_opts if state == MENU else set_opts
    for i, opt in enumerate(opts):
        col = CYAN if i == sel else WHITE
        t   = font_md.render(opt, True, col)
        t.set_alpha(int(255 * fade))
        surf.blit(t, (WIDTH // 2 - t.get_width() // 2, 180 + i * 56))

    if state == MENU:
        hints = ["W / S  — Left paddle", "↑ / ↓  — Right paddle",
                 "SPACE — Shoot  |  P — Pause  |  ESC — Menu"]
        for i, h in enumerate(hints):
            img = font_xs.render(h, True, GREY)
            img.set_alpha(int(200 * fade))
            surf.blit(img, (WIDTH // 2 - img.get_width() // 2, HEIGHT - 110 + i * 22))
        if high_scores:
            ht = font_xs.render(f"Best: {high_scores[0]}", True, YELLOW)
            surf.blit(ht, (WIDTH // 2 - ht.get_width() // 2, HEIGHT - 42))

def draw_gameover_screen(surf, gs, won):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 175))
    surf.blit(overlay, (0, 0))
    if won:
        msg, col = "YOU WIN!", CYAN
    else:
        msg, col = "GAME OVER", RED
    for txt, y, fnt in [
        (font_xl.render(msg, True, col),             HEIGHT // 2 - 130, None),
        (font_md.render(f"Score: {gs['ls']} – {gs['rs']}", True, WHITE), HEIGHT // 2 - 30, None),
        (font_md.render(f"Hits: {gs['hits']}", True, WHITE),             HEIGHT // 2 + 20, None),
        (font_sm.render(f"Time: {gs['match_ms']//1000}s", True, GREY),  HEIGHT // 2 + 70, None),
        (font_sm.render("ENTER  ·  Menu      R  ·  Replay", True, GREY), HEIGHT // 2 + 120, None),
    ]:
        surf.blit(txt, (WIDTH // 2 - txt.get_width() // 2, y))

def draw_pause_screen(surf):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    surf.blit(overlay, (0, 0))
    for txt, y in [
        (font_lg.render("PAUSED", True, WHITE), HEIGHT // 2 - 60),
        (font_sm.render("P  ·  Resume", True, GREY),  HEIGHT // 2 + 10),
        (font_sm.render("ESC  ·  Menu", True, GREY),  HEIGHT // 2 + 50),
    ]:
        surf.blit(txt, (WIDTH // 2 - txt.get_width() // 2, y))

# ─── MENU INPUT ───────────────────────────────────────────────────────────────
def handle_menu_key(event, state):
    global sel, two_player, diff, win_score, sound_on, shake_on
    global lp_col, rp_col, ball_col, fade, game_state, gs

    opts = main_opts if state == MENU else set_opts
    if event.key == pygame.K_UP:
        sel = (sel - 1) % len(opts)
        if sound_on: snd_menu.play()
    elif event.key == pygame.K_DOWN:
        sel = (sel + 1) % len(opts)
        if sound_on: snd_menu.play()
    elif event.key in (pygame.K_RETURN, pygame.K_RIGHT, pygame.K_LEFT):
        if sound_on: snd_menu.play()
        if state == MENU:
            if sel == 0:
                gs = fresh_state(diff)
                game_state = PLAYING
            elif sel == 1:
                two_player = not two_player
                main_opts[1] = f"Two Player: {'On' if two_player else 'Off'}"
            elif sel == 2:
                dl = list(DIFFICULTIES.keys())
                diff = dl[(dl.index(diff) + 1) % len(dl)]
                main_opts[2] = f"Difficulty: {diff}"
            elif sel == 3:
                win_score = {10: 5, 5: 7, 7: 10}[win_score]
                main_opts[3] = f"Points to Win: {win_score}"
            elif sel == 4:
                game_state = SETTINGS
                sel = 0; fade = 0
            elif sel == 5:
                pygame.quit(); sys.exit()
        else:  # SETTINGS
            if sel == 0:
                sound_on = not sound_on
                set_opts[0] = f"Sound: {'On' if sound_on else 'Off'}"
            elif sel == 1:
                shake_on = not shake_on
                set_opts[1] = f"Screen Shake: {'On' if shake_on else 'Off'}"
            elif sel == 2:
                lp_col = COLORS[(COLORS.index(lp_col) + 1) % len(COLORS)]
                set_opts[2] = f"Left Paddle: {COLOR_NAMES[lp_col]}"
            elif sel == 3:
                rp_col = COLORS[(COLORS.index(rp_col) + 1) % len(COLORS)]
                set_opts[3] = f"Right Paddle: {COLOR_NAMES[rp_col]}"
            elif sel == 4:
                ball_col = COLORS[(COLORS.index(ball_col) + 1) % len(COLORS)]
                set_opts[4] = f"Ball Color: {COLOR_NAMES[ball_col]}"
            elif sel == 5:
                game_state = MENU; sel = 0; fade = 0

# ─── BOOTSTRAP ────────────────────────────────────────────────────────────────
game_state = MENU
gs = None    # initialised when game starts

# ─── MAIN LOOP ────────────────────────────────────────────────────────────────
while True:
    dt = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_hs(high_scores)
            pygame.quit(); sys.exit()

        if event.type == pygame.KEYDOWN:
            if game_state in (MENU, SETTINGS):
                handle_menu_key(event, game_state)

            elif game_state == PLAYING:
                if event.key == pygame.K_p:
                    game_state = PAUSED
                elif event.key == pygame.K_ESCAPE:
                    game_state = MENU; fade = 0

            elif game_state == PAUSED:
                if event.key == pygame.K_p:
                    game_state = PLAYING
                elif event.key == pygame.K_ESCAPE:
                    game_state = MENU; fade = 0

            elif game_state == GAME_OVER:
                if event.key == pygame.K_RETURN:
                    game_state = MENU; fade = 0
                elif event.key == pygame.K_r:
                    gs = fresh_state(diff)
                    game_state = PLAYING

    # ── PLAYING UPDATE ────────────────────────────────────────────────────────
    if game_state == PLAYING:
        gs["match_ms"] = pygame.time.get_ticks() - gs["start"]
        keys = pygame.key.get_pressed()
        move_paddles(gs, keys, dt, two_player)

        # Step each ball; if one scores, reset the set
        survivors = []
        scored    = False
        for ball in gs["balls"]:
            if step_ball(ball, gs):
                survivors.append(ball)
            else:
                scored = True
        gs["balls"] = survivors
        if scored or not gs["balls"]:
            reset_balls(gs)

        update_power_ups(gs)

        # UFO pass
        gs["ufo"].tick()
        if gs["ufo"].active:
            for ball in gs["balls"]:
                if gs["ufo"].hitbox().collidepoint(ball["x"], ball["y"]):
                    spawn_particles(gs["ufo"].hitbox().centerx, gs["ufo"].y, RED, 30)
                    spawn_popup(gs["ufo"].hitbox().centerx, gs["ufo"].y, f"+{UFO.PTS}", RED)
                    gs["ls"] += 1
                    gs["score"] += UFO.PTS
                    gs["ufo"].active = False
                    if sound_on: snd_lvlup.play()

        # Decay screen shake
        if gs["shake"] > 0:
            gs["shake"] = max(0, gs["shake"] - dt * 28)

        # Check win condition
        if gs["ls"] >= win_score or gs["rs"] >= win_score:
            won = gs["ls"] >= win_score
            high_scores.append(gs["score"])
            high_scores.sort(reverse=True)
            save_hs(high_scores)
            game_state = GAME_OVER

    # ── RENDER ────────────────────────────────────────────────────────────────
    if game_state in (MENU, SETTINGS):
        draw_menu_screen(screen, game_state)

    elif game_state in (PLAYING, PAUSED, GAME_OVER):
        draw_bg(screen)

        # Apply screen shake offset
        ox = oy = 0
        if shake_on and gs["shake"] > 0:
            ox = random.randint(-int(gs["shake"]), int(gs["shake"]))
            oy = random.randint(-int(gs["shake"]), int(gs["shake"]))
            if ox or oy:
                tmp = screen.copy()
                screen.blit(tmp, (ox, oy))

        draw_net(screen)
        draw_ground(screen)
        draw_shields(screen, gs["shields"])
        draw_pu_items(screen, gs["pu_items"])
        draw_paddles(screen, gs)
        for ball in gs["balls"]:
            draw_ball_obj(screen, ball, gs["pu_active"])
        gs["ufo"].draw(screen)
        update_draw_particles(screen)
        update_draw_popups(screen)
        draw_hud(screen, gs)
        draw_pu_status(screen, gs["pu_active"])

        if game_state == PAUSED:
            draw_pause_screen(screen)
        elif game_state == GAME_OVER:
            draw_gameover_screen(screen, gs, won)

    pygame.display.flip()
