import pygame
import sys
import random
import math
import numpy
import json
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
BALL_SIZE = 20
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
BLUE = (0, 100, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
YELLOW = (255, 255, 50)
PURPLE = (150, 50, 255)
COLORS = [WHITE, RED, GREEN, BLUE, YELLOW, PURPLE]

# Game states
MENU = 0
PLAYING = 1
PAUSED = 2
GAME_OVER = 3
SETTINGS = 4

# Difficulty settings
DIFFICULTIES = {
    "Easy": {"paddle_speed": 5, "ball_speed": 4, "ai_accuracy": 0.6, "ai_reaction": 0.3},
    "Medium": {"paddle_speed": 7, "ball_speed": 6, "ai_accuracy": 0.8, "ai_reaction": 0.2},
    "Hard": {"paddle_speed": 9, "ball_speed": 8, "ai_accuracy": 0.95, "ai_reaction": 0.1}
}

# Set up the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultimate Table Tennis")
icon = pygame.Surface((32, 32))
icon.fill(WHITE)
pygame.draw.circle(icon, BLACK, (16, 16), 8)
pygame.display.set_icon(icon)

# Load sounds with error handling
def load_sound(filename, fallback_freq, duration):
    try:
        return pygame.mixer.Sound(filename)
    except:
        return pygame.mixer.Sound(pygame.sndarray.make_sound(
            pygame.sndarray.array(numpy.sin(2*numpy.pi*fallback_freq*numpy.arange(duration)/duration).astype(numpy.float32))))

paddle_sound = load_sound('paddle_hit.wav', 440, 4000)
wall_sound = load_sound('wall_hit.wav', 220, 2000)
score_sound = load_sound('score.wav', 880, 8000)
menu_sound = load_sound('menu_select.wav', 330, 1000)

# Load background music
try:
    pygame.mixer.music.load('background_music.mp3')
    music_enabled = True
except:
    music_enabled = False

# Game variables
game_state = MENU
difficulty = "Medium"
current_settings = DIFFICULTIES[difficulty]
two_player_mode = False
left_paddle_y = (HEIGHT - PADDLE_HEIGHT) // 2
right_paddle_y = (HEIGHT - PADDLE_HEIGHT) // 2
left_paddle_vel = 0
right_paddle_vel = 0
balls = [{"x": WIDTH // 2, "y": HEIGHT // 2, "vel_x": current_settings["ball_speed"], "vel_y": current_settings["ball_speed"] / 2, "trail": [], "visible": True}]
left_score = 0
right_score = 0
winning_score = 10
power_ups = []
active_power_ups = {"paddle_size": 1.0, "ball_speed": 1.0, "multi_ball": 1, "invisibility": False}
power_up_timer = 0
game_start_time = 0
hit_count = 0
screen_shake = 0
sound_volume = 1.0
screen_shake_enabled = True
high_scores = []
match_time = 0
left_paddle_color = WHITE
right_paddle_color = WHITE
ball_color = WHITE

# Power-up types
power_up_types = ["paddle_grow", "paddle_shrink", "ball_slow", "ball_fast", "multi_ball", "invisibility"]

# Fonts
font_large = pygame.font.Font(None, 74)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 32)

# Menu options
main_menu_options = ["Start Game", "Two Player: Off", f"Difficulty: {difficulty}", "Points to Win: 10", "Settings", "Exit"]
settings_menu_options = ["Sound Volume: 100%", "Music: On", "Screen Shake: On", "Left Paddle Color: White", "Right Paddle Color: White", "Ball Color: White", "Back"]
selected_option = 0
menu_fade = 0

# Particles for hit effects
particles = []

# Load high scores
def load_high_scores():
    global high_scores
    try:
        with open('high_scores.txt', 'r') as f:
            high_scores = json.load(f)
    except:
        high_scores = []

# Save high scores
def save_high_scores():
    try:
        with open('high_scores.txt', 'w') as f:
            json.dump(high_scores, f)
    except:
        pass

load_high_scores()

def reset_game():
    """Reset the game state to start a new game"""
    global left_paddle_y, right_paddle_y, balls, left_score, right_score, game_state, power_ups, active_power_ups
    global game_start_time, power_up_timer, hit_count, left_paddle_vel, right_paddle_vel, match_time
    left_paddle_y = (HEIGHT - PADDLE_HEIGHT) // 2
    right_paddle_y = (HEIGHT - PADDLE_HEIGHT) // 2
    left_paddle_vel = 0
    right_paddle_vel = 0
    balls = [{"x": WIDTH // 2, "y": HEIGHT // 2, "vel_x": current_settings["ball_speed"] * random.choice([-1, 1]),
              "vel_y": current_settings["ball_speed"] / 2 * random.choice([-1, 1]), "trail": [], "visible": True}]
    left_score = 0
    right_score = 0
    power_ups = []
    active_power_ups = {"paddle_size": 1.0, "ball_speed": 1.0, "multi_ball": 1, "invisibility": False}
    game_state = PLAYING
    game_start_time = pygame.time.get_ticks()
    power_up_timer = game_start_time
    hit_count = 0
    match_time = 0
    if music_enabled:
        pygame.mixer.music.play(-1)

def draw_gradient_background():
    """Draw a gradient background"""
    for y in range(HEIGHT):
        color = (0, max(0, 50 - y // 10), max(0, 50 - y // 10))
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))

def draw_paddles():
    """Draw the paddles with glow effect"""
    paddle_height = PADDLE_HEIGHT * active_power_ups["paddle_size"]
    # Glow effect
    for i in range(3):
        glow_alpha = 50 - i * 15
        glow_surface = pygame.Surface((PADDLE_WIDTH + i * 4, paddle_height + i * 4), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (*left_paddle_color, glow_alpha), (0, 0, PADDLE_WIDTH + i * 4, paddle_height + i * 4))
        screen.blit(glow_surface, (-i * 2, left_paddle_y - i * 2))
        glow_surface = pygame.Surface((PADDLE_WIDTH + i * 4, paddle_height + i * 4), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (*right_paddle_color, glow_alpha), (0, 0, PADDLE_WIDTH + i * 4, paddle_height + i * 4))
        screen.blit(glow_surface, (WIDTH - PADDLE_WIDTH - i * 2, right_paddle_y - i * 2))
    # Main paddles
    pygame.draw.rect(screen, left_paddle_color, (0, left_paddle_y, PADDLE_WIDTH, paddle_height))
    pygame.draw.rect(screen, right_paddle_color, (WIDTH - PADDLE_WIDTH, right_paddle_y, PADDLE_WIDTH, paddle_height))

def draw_ball(ball):
    """Draw a ball and its trail"""
    if not ball["visible"] and active_power_ups["invisibility"]:
        return
    # Draw trail
    for i, pos in enumerate(ball["trail"]):
        alpha = int(255 * (i / len(ball["trail"])))
        trail_color = (*ball_color, alpha)
        trail_size = int(BALL_SIZE * (0.3 + 0.7 * i / len(ball["trail"])))
        trail_surface = pygame.Surface((trail_size, trail_size), pygame.SRCALPHA)
        pygame.draw.ellipse(trail_surface, trail_color, (0, 0, trail_size, trail_size))
        screen.blit(trail_surface, (pos[0] - trail_size/2, pos[1] - trail_size/2))
    # Draw main ball
    ball_surface = pygame.Surface((BALL_SIZE, BALL_SIZE), pygame.SRCALPHA)
    pygame.draw.ellipse(ball_surface, ball_color, (0, 0, BALL_SIZE, BALL_SIZE))
    screen.blit(ball_surface, (ball["x"] - BALL_SIZE/2, ball["y"] - BALL_SIZE/2))

def draw_particles():
    """Draw particle effects"""
    global particles
    new_particles = []
    for particle in particles:
        particle["x"] += particle["vel_x"]
        particle["y"] += particle["vel_y"]
        particle["life"] -= 1
        if particle["life"] > 0:
            alpha = int(255 * particle["life"] / particle["max_life"])
            particle_surface = pygame.Surface((particle["size"], particle["size"]), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (*particle["color"], alpha), (particle["size"]/2, particle["size"]/2), particle["size"]/2)
            screen.blit(particle_surface, (particle["x"] - particle["size"]/2, particle["y"] - particle["size"]/2))
            new_particles.append(particle)
    particles = new_particles

def create_particles(x, y, color, count=10):
    """Create particle effects at given position"""
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 5)
        particles.append({
            "x": x,
            "y": y,
            "vel_x": math.cos(angle) * speed,
            "vel_y": math.sin(angle) * speed,
            "life": random.randint(10, 20),
            "max_life": random.randint(10, 20),
            "size": random.randint(5, 10),
            "color": color
        })

def draw_scores():
    """Display scores with slight shadow effect"""
    for offset in [(2, 2), (0, 0)]:
        color = BLACK if offset != (0, 0) else WHITE
        left_text = font_large.render(str(left_score), True, color)
        right_text = font_large.render(str(right_score), True, color)
        screen.blit(left_text, (WIDTH // 4 + offset[0], 20 + offset[1]))
        screen.blit(right_text, (3 * WIDTH // 4 + offset[0], 20 + offset[1]))

def draw_net():
    """Draw a pulsing dashed net"""
    pulse = (math.sin(pygame.time.get_ticks() / 1000) + 1) / 4 + 0.5
    net_color = (int(GRAY[0] * pulse), int(GRAY[1] * pulse), int(GRAY[2] * pulse))
    for y in range(0, HEIGHT, 20):
        pygame.draw.rect(screen, net_color, (WIDTH // 2 - 1, y, 2, 10))

def draw_power_ups():
    """Draw power-ups with animation"""
    for power_up in power_ups:
        scale = 1 + 0.1 * math.sin(pygame.time.get_ticks() / 300)
        size = int(15 * scale)
        pygame.draw.circle(screen, GREEN, (power_up["x"], power_up["y"]), size)
        text = font_small.render(power_up["type"][0].upper(), True, BLACK)
        text_rect = text.get_rect(center=(power_up["x"], power_up["y"]))
        screen.blit(text, text_rect)

def draw_power_up_status():
    """Draw active power-up status indicators"""
    y_pos = HEIGHT - 30
    status_texts = []
    if active_power_ups["paddle_size"] != 1.0:
        status_texts.append(f"Paddle: {'Enlarged' if active_power_ups['paddle_size'] > 1 else 'Reduced'}")
    if active_power_ups["ball_speed"] != 1.0:
        status_texts.append(f"Ball: {'Slowed' if active_power_ups['ball_speed'] < 1 else 'Accelerated'}")
    if active_power_ups["multi_ball"] > 1:
        status_texts.append(f"Multi-Ball: {active_power_ups['multi_ball']}")
    if active_power_ups["invisibility"]:
        status_texts.append("Ball: Invisible")
    for i, text in enumerate(status_texts):
        text_surface = font_small.render(text, True, GREEN)
        screen.blit(text_surface, (10, y_pos - i * 20))

def move_paddles(keys, delta_time):
    """Handle paddle movement with acceleration"""
    global left_paddle_y, right_paddle_y, left_paddle_vel, right_paddle_vel
    paddle_speed = current_settings["paddle_speed"]
    paddle_height = PADDLE_HEIGHT * active_power_ups["paddle_size"]
    accel = paddle_speed * 20
    friction = 0.9

    # Left paddle
    target_vel = 0
    if keys[pygame.K_w] and left_paddle_y > 0:
        target_vel -= paddle_speed
    if keys[pygame.K_s] and left_paddle_y < HEIGHT - paddle_height:
        target_vel += paddle_speed
    left_paddle_vel += (target_vel - left_paddle_vel) * accel * delta_time
    left_paddle_vel *= friction
    left_paddle_y += left_paddle_vel
    left_paddle_y = max(0, min(HEIGHT - paddle_height, left_paddle_y))

    # Right paddle
    if two_player_mode:
        target_vel = 0
        if keys[pygame.K_UP] and right_paddle_y > 0:
            target_vel -= paddle_speed
        if keys[pygame.K_DOWN] and right_paddle_y < HEIGHT - paddle_height:
            target_vel += paddle_speed
        right_paddle_vel += (target_vel - right_paddle_vel) * accel * delta_time
        right_paddle_vel *= friction
        right_paddle_y += right_paddle_vel
        right_paddle_y = max(0, min(HEIGHT - paddle_height, right_paddle_y))
    else:
        # AI control with prediction
        target_y = HEIGHT // 2
        for ball in balls:
            if ball["vel_x"] > 0:  # Ball moving towards AI
                time_to_reach = (WIDTH - PADDLE_WIDTH - ball["x"]) / ball["vel_x"]
                predicted_y = ball["y"] + ball["vel_y"] * time_to_reach
                # Reflect off walls
                while predicted_y < 0 or predicted_y > HEIGHT:
                    if predicted_y < 0:
                        predicted_y = -predicted_y
                    else:
                        predicted_y = 2 * HEIGHT - predicted_y
                target_y = predicted_y
                break
        # Add randomness and reaction delay
        if random.random() > current_settings["ai_accuracy"]:
            target_y += random.uniform(-50, 50)
        paddle_center = right_paddle_y + paddle_height / 2
        if paddle_center < target_y - 5 and right_paddle_y < HEIGHT - paddle_height:
            right_paddle_vel += accel * delta_time
        elif paddle_center > target_y + 5 and right_paddle_y > 0:
            right_paddle_vel -= accel * delta_time
        right_paddle_vel *= friction
        right_paddle_y += right_paddle_vel * (1 - current_settings["ai_reaction"])
        right_paddle_y = max(0, min(HEIGHT - paddle_height, right_paddle_y))

def move_ball(ball, delta_time):
    """Update ball position and handle collisions"""
    global left_score, right_score, hit_count, screen_shake
    actual_vel_x = ball["vel_x"] * active_power_ups["ball_speed"]
    actual_vel_y = ball["vel_y"] * active_power_ups["ball_speed"]
    ball["x"] += actual_vel_x * delta_time * 60
    ball["y"] += actual_vel_y * delta_time * 60
    ball["trail"].append((ball["x"], ball["y"]))
    if len(ball["trail"]) > 8:
        ball["trail"].pop(0)
    paddle_height = PADDLE_HEIGHT * active_power_ups["paddle_size"]

    # Bounce off walls
    if ball["y"] <= 0 or ball["y"] >= HEIGHT:
        ball["vel_y"] = -ball["vel_y"]
        create_particles(ball["x"], ball["y"], YELLOW, 5)
        pygame.mixer.Sound.play(wall_sound).set_volume(sound_volume)
        if screen_shake_enabled:
            screen_shake = 5

    # Bounce off paddles
    if ball["x"] <= PADDLE_WIDTH and left_paddle_y <= ball["y"] <= left_paddle_y + paddle_height:
        hit_pos = (ball["y"] - (left_paddle_y + paddle_height/2)) / paddle_height
        angle = hit_pos * math.pi/3
        speed = math.sqrt(ball["vel_x"]**2 + ball["vel_y"]**2) * 1.05
        ball["vel_x"] = abs(speed * math.cos(angle))
        ball["vel_y"] = speed * math.sin(angle) + left_paddle_vel * 0.3  # Add spin
        hit_count += 1
        create_particles(ball["x"], ball["y"], left_paddle_color, 15)
        pygame.mixer.Sound.play(paddle_sound).set_volume(sound_volume)
        if screen_shake_enabled:
            screen_shake = 8
    elif ball["x"] >= WIDTH - PADDLE_WIDTH - BALL_SIZE and right_paddle_y <= ball["y"] <= right_paddle_y + paddle_height:
        hit_pos = (ball["y"] - (right_paddle_y + paddle_height/2)) / paddle_height
        angle = hit_pos * math.pi/3
        speed = math.sqrt(ball["vel_x"]**2 + ball["vel_y"]**2) * 1.05
        ball["vel_x"] = -abs(speed * math.cos(angle))
        ball["vel_y"] = speed * math.sin(angle) + right_paddle_vel * 0.3  # Add spin
        hit_count += 1
        create_particles(ball["x"], ball["y"], right_paddle_color, 15)
        pygame.mixer.Sound.play(paddle_sound).set_volume(sound_volume)
        if screen_shake_enabled:
            screen_shake = 8

    # Score points
    if ball["x"] < 0:
        right_score += 1
        create_particles(ball["x"], ball["y"], RED, 20)
        pygame.mixer.Sound.play(score_sound).set_volume(sound_volume)
        if screen_shake_enabled:
            screen_shake = 10
        return False
    elif ball["x"] > WIDTH:
        left_score += 1
        create_particles(ball["x"], ball["y"], RED, 20)
        pygame.mixer.Sound.play(score_sound).set_volume(sound_volume)
        if screen_shake_enabled:
            screen_shake = 10
        return False
    return True

def reset_ball():
    """Reset balls with random direction"""
    global balls, hit_count
    balls = []
    for _ in range(active_power_ups["multi_ball"]):
        speed = current_settings["ball_speed"] * (1 + hit_count * 0.02)
        angle = random.uniform(-math.pi/4, math.pi/4)
        direction = random.choice([-1, 1])
        balls.append({
            "x": WIDTH // 2,
            "y": HEIGHT // 2,
            "vel_x": speed * math.cos(angle) * direction,
            "vel_y": speed * math.sin(angle),
            "trail": [],
            "visible": True
        })
    hit_count = 0

def update_power_ups():
    """Manage power-up spawning and collection"""
    global power_ups, active_power_ups, power_up_timer
    current_time = pygame.time.get_ticks()
    if current_time - power_up_timer > 15000 and len(power_ups) < 3:
        power_up_type = random.choice(power_up_types)
        power_ups.append({
            "x": random.randint(WIDTH//4, 3*WIDTH//4),
            "y": random.randint(HEIGHT//4, 3*HEIGHT//4),
            "type": power_up_type
        })
        power_up_timer = current_time
    for power_up in power_ups[:]:
        for ball in balls:
            if math.hypot(ball["x"] - power_up["x"], ball["y"] - power_up["y"]) < 20:
                apply_power_up(power_up["type"])
                power_ups.remove(power_up)
                break
    if current_time - power_up_timer > 10000:
        active_power_ups = {"paddle_size": 1.0, "ball_speed": 1.0, "multi_ball": 1, "invisibility": False}
        reset_ball()

def apply_power_up(power_type):
    """Apply power-up effects"""
    global active_power_ups
    if power_type == "paddle_grow":
        active_power_ups["paddle_size"] = 1.5
    elif power_type == "paddle_shrink":
        active_power_ups["paddle_size"] = 0.7
    elif power_type == "ball_slow":
        active_power_ups["ball_speed"] = 0.7
    elif power_type == "ball_fast":
        active_power_ups["ball_speed"] = 1.3
    elif power_type == "multi_ball":
        active_power_ups["multi_ball"] = min(3, active_power_ups["multi_ball"] + 1)
        reset_ball()
    elif power_type == "invisibility":
        active_power_ups["invisibility"] = True

def draw_menu():
    """Draw the main menu with fade animation"""
    global menu_fade
    draw_gradient_background()
    menu_fade = min(menu_fade + 0.05, 1)
    title = font_large.render("ULTIMATE TABLE TENNIS", True, WHITE)
    title.set_alpha(int(255 * menu_fade))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
    options = main_menu_options if game_state == MENU else settings_menu_options
    for i, option in enumerate(options):
        color = BLUE if i == selected_option else WHITE
        text = font_medium.render(option, True, color)
        text.set_alpha(int(255 * menu_fade))
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 200 + i*60))
    if game_state == MENU:
        instructions = [
            "Player 1: W/S to move",
            "Player 2: UP/DOWN to move",
            "P to pause, ESC to menu",
            "Collect power-ups for advantages!"
        ]
        for i, instruction in enumerate(instructions):
            text = font_small.render(instruction, True, WHITE)
            text.set_alpha(int(255 * menu_fade))
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT - 150 + i*30))
        # Display high scores
        if high_scores:
            text = font_small.render(f"High Score: {max(high_scores)}", True, WHITE)
            text.set_alpha(int(255 * menu_fade))
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT - 50))

def draw_game_over():
    """Draw the game over screen with stats"""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    winner = "Player 1" if left_score > right_score else "Player 2/AI"
    texts = [
        font_large.render("GAME OVER", True, WHITE),
        font_medium.render(f"{winner} Wins!", True, WHITE),
        font_small.render(f"Score: {left_score} - {right_score}", True, WHITE),
        font_small.render(f"Hits: {hit_count}", True, WHITE),
        font_small.render(f"Time: {match_time // 1000}s", True, WHITE),
        font_small.render("ENTER: Menu, R: Replay", True, WHITE)
    ]
    for i, text in enumerate(texts):
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 120 + i*50))
    # Save high score
    score = max(left_score, right_score)
    if score > 0:
        high_scores.append(score)
        high_scores.sort(reverse=True)
        high_scores[:] = high_scores[:5]
        save_high_scores()

def draw_pause_screen():
    """Draw the pause screen with options"""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))
    texts = [
        font_large.render("PAUSED", True, WHITE),
        font_small.render("P: Resume", True, WHITE),
        font_small.render("ESC: Menu", True, WHITE)
    ]
    for i, text in enumerate(texts):
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 50 + i*40))

def handle_menu_input(event):
    """Handle input on the menu and settings screens"""
    global selected_option, two_player_mode, difficulty, current_settings, winning_score, game_state
    global sound_volume, music_enabled, screen_shake_enabled, menu_fade, left_paddle_color, right_paddle_color, ball_color
    if event.type == pygame.KEYDOWN:
        options = main_menu_options if game_state == MENU else settings_menu_options
        if event.key == pygame.K_UP:
            selected_option = (selected_option - 1) % len(options)
            pygame.mixer.Sound.play(menu_sound).set_volume(sound_volume)
        elif event.key == pygame.K_DOWN:
            selected_option = (selected_option + 1) % len(options)
            pygame.mixer.Sound.play(menu_sound).set_volume(sound_volume)
        elif event.key == pygame.K_RETURN:
            pygame.mixer.Sound.play(menu_sound).set_volume(sound_volume)
            if game_state == MENU:
                if selected_option == 0:
                    reset_game()
                elif selected_option == 1:
                    two_player_mode = not two_player_mode
                    main_menu_options[1] = f"Two Player: {'On' if two_player_mode else 'Off'}"
                elif selected_option == 2:
                    difficulties = list(DIFFICULTIES.keys())
                    current_index = difficulties.index(difficulty)
                    difficulty = difficulties[(current_index + 1) % len(difficulties)]
                    current_settings = DIFFICULTIES[difficulty]
                    main_menu_options[2] = f"Difficulty: {difficulty}"
                elif selected_option == 3:
                    winning_score = 5 if winning_score == 10 else (7 if winning_score == 5 else 10)
                    main_menu_options[3] = f"Points to Win: {winning_score}"
                elif selected_option == 4:
                    game_state = SETTINGS
                    selected_option = 0
                    menu_fade = 0
                elif selected_option == 5:
                    pygame.quit()
                    sys.exit()
            else:  # Settings menu
                if selected_option == 0:
                    sound_volume = max(0, min(1, sound_volume + 0.1 if sound_volume < 0.9 else -0.9))
                    settings_menu_options[0] = f"Sound Volume: {int(sound_volume * 100)}%"
                elif selected_option == 1 and music_enabled:
                    music_enabled = not music_enabled
                    settings_menu_options[1] = f"Music: {'On' if music_enabled else 'Off'}"
                    if music_enabled:
                        pygame.mixer.music.play(-1)
                    else:
                        pygame.mixer.music.stop()
                elif selected_option == 2:
                    screen_shake_enabled = not screen_shake_enabled
                    settings_menu_options[2] = f"Screen Shake: {'On' if screen_shake_enabled else 'Off'}"
                elif selected_option == 3:
                    current_color = left_paddle_color
                    color_index = COLORS.index(current_color) if current_color in COLORS else 0
                    left_paddle_color = COLORS[(color_index + 1) % len(COLORS)]
                    settings_menu_options[3] = f"Left Paddle Color: {color_name(left_paddle_color)}"
                elif selected_option == 4:
                    current_color = right_paddle_color
                    color_index = COLORS.index(current_color) if current_color in COLORS else 0
                    right_paddle_color = COLORS[(color_index + 1) % len(COLORS)]
                    settings_menu_options[4] = f"Right Paddle Color: {color_name(right_paddle_color)}"
                elif selected_option == 5:
                    current_color = ball_color
                    color_index = COLORS.index(current_color) if current_color in COLORS else 0
                    ball_color = COLORS[(color_index + 1) % len(COLORS)]
                    settings_menu_options[5] = f"Ball Color: {color_name(ball_color)}"
                elif selected_option == 6:
                    game_state = MENU
                    selected_option = 0
                    menu_fade = 0

def color_name(color):
    """Return the name of a color"""
    color_names = {WHITE: "White", RED: "Red", GREEN: "Green", BLUE: "Blue", YELLOW: "Yellow", PURPLE: "Purple"}
    return color_names.get(color, "Custom")

# Main game loop
clock = pygame.time.Clock()
while True:
    delta_time = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if game_state in [MENU, SETTINGS]:
                handle_menu_input(event)
            elif game_state == PLAYING:
                if event.key == pygame.K_p:
                    game_state = PAUSED
                elif event.key == pygame.K_ESCAPE:
                    game_state = MENU
                    menu_fade = 0
                    pygame.mixer.music.stop()
            elif game_state == PAUSED:
                if event.key == pygame.K_p:
                    game_state = PLAYING
                elif event.key == pygame.K_ESCAPE:
                    game_state = MENU
                    menu_fade = 0
                    pygame.mixer.music.stop()
            elif game_state == GAME_OVER:
                if event.key == pygame.K_RETURN:
                    game_state = MENU
                    menu_fade = 0
                    pygame.mixer.music.stop()
                elif event.key == pygame.K_r:
                    reset_game()

    # Update game state
    if game_state == PLAYING:
        match_time = pygame.time.get_ticks() - game_start_time
        keys = pygame.key.get_pressed()
        move_paddles(keys, delta_time)
        new_balls = []
        for ball in balls:
            if move_ball(ball, delta_time):
                new_balls.append(ball)
            else:
                reset_ball()
                break
        balls = new_balls
        update_power_ups()
        if left_score >= winning_score or right_score >= winning_score:
            game_state = GAME_OVER
            pygame.mixer.music.stop()

    # Render
    draw_gradient_background()
    if screen_shake_enabled and screen_shake > 0:
        offset_x = random.randint(-screen_shake, screen_shake)
        offset_y = random.randint(-screen_shake, screen_shake)
        screen.blit(screen, (offset_x, offset_y))
        screen_shake -= delta_time * 20
    else:
        offset_x = offset_y = 0

    if game_state in [PLAYING, PAUSED, GAME_OVER]:
        draw_net()
        draw_paddles()
        for ball in balls:
            draw_ball(ball)
        draw_scores()
        draw_power_ups()
        draw_power_up_status()
        draw_particles()
        if game_state == PAUSED:
            draw_pause_screen()
        elif game_state == GAME_OVER:
            draw_game_over()
    else:
        draw_menu()

    pygame.display.flip()

pygame.quit()
