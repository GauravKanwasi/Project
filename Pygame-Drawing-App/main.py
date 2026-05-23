import pygame
import sys
import math
import os
from collections import deque

# ─── INIT ─────────────────────────────────────────────────────────────────────
pygame.init()

# ─── CONSTANTS ────────────────────────────────────────────────────────────────
SW, SH      = 1100, 720
TOOLBAR_W   = 200          # left toolbar width
CANVAS_X    = TOOLBAR_W
CANVAS_W    = SW - TOOLBAR_W
CANVAS_H    = SH
FPS         = 120
UNDO_LIMIT  = 40           # max undo steps stored

# Palette (name, RGB)
PALETTE = [
    ("Black",   (10,  10,  10)),
    ("White",   (255, 255, 255)),
    ("Red",     (220, 50,  50)),
    ("Orange",  (255, 140, 30)),
    ("Yellow",  (255, 220, 30)),
    ("Lime",    (80,  220, 80)),
    ("Green",   (30,  160, 60)),
    ("Cyan",    (30,  210, 230)),
    ("Blue",    (50,  100, 230)),
    ("Indigo",  (80,  50,  200)),
    ("Purple",  (160, 50,  220)),
    ("Pink",    (240, 100, 160)),
    ("Brown",   (140, 80,  40)),
    ("Grey",    (130, 130, 130)),
    ("Silver",  (200, 200, 200)),
    ("Gold",    (220, 190, 50)),
]

# Tool names
TOOLS = ["Pencil", "Brush", "Spray", "Line", "Rect", "Ellipse", "Fill", "Eraser"]

# UI colours
BG       = (28,  28,  38)
PANEL    = (38,  38,  52)
ACCENT   = (80,  130, 240)
TEXT_COL = (220, 220, 230)
BORDER   = (60,  60,  80)

# ─── DISPLAY ──────────────────────────────────────────────────────────────────
screen = pygame.display.set_mode((SW, SH))
pygame.display.set_caption("Drawing App  ·  Enhanced")
clock  = pygame.time.Clock()

font_md = pygame.font.SysFont("segoeui",  16)
font_sm = pygame.font.SysFont("segoeui",  13)
font_xs = pygame.font.SysFont("consolas", 12)

# ─── CANVAS ───────────────────────────────────────────────────────────────────
canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill((255, 255, 255))

# Undo / redo stacks store snapshots of the canvas surface
undo_stack: deque = deque(maxlen=UNDO_LIMIT)
redo_stack: deque = deque(maxlen=UNDO_LIMIT)

def push_undo():
    """Snapshot canvas before a stroke begins; clears redo history."""
    undo_stack.append(canvas.copy())
    redo_stack.clear()

def undo():
    if undo_stack:
        redo_stack.append(canvas.copy())
        canvas.blit(undo_stack.pop(), (0, 0))

def redo():
    if redo_stack:
        undo_stack.append(canvas.copy())
        canvas.blit(redo_stack.pop(), (0, 0))

# ─── STATE ────────────────────────────────────────────────────────────────────
state = {
    "tool":        "Brush",
    "color":       (10, 10, 10),
    "size":        8,
    "opacity":     255,         # 0-255 brush opacity
    "drawing":     False,
    "last_pos":    None,
    "shape_start": None,        # for line / rect / ellipse drag
    "shape_snap":  None,        # live preview surface
    "save_tick":   0,
    "hovered_swatch": -1,
}

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def canvas_pos(screen_pos):
    """Convert screen coordinates to canvas coordinates."""
    x, y = screen_pos
    return x - CANVAS_X, y

def on_canvas(pos):
    x, y = pos
    return CANVAS_X <= x < SW and 0 <= y < SH

def lerp_points(a, b):
    """Return interpolated integer positions between a and b (for smooth lines)."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    steps  = max(abs(dx), abs(dy), 1)
    return [(int(a[0] + dx * i / steps), int(a[1] + dy * i / steps))
            for i in range(steps + 1)]

def draw_brush_stamp(surf, pos, color, size, opacity=255):
    """Draw one soft-edged circular stamp at pos."""
    r  = max(1, size // 2)
    s  = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    # Soft falloff: inner full-opacity circle + outer feathered ring
    pygame.draw.circle(s, (*color, opacity),        (r, r), r)
    pygame.draw.circle(s, (*color, opacity // 3),   (r, r), r, max(1, r // 3))
    surf.blit(s, (pos[0] - r, pos[1] - r), special_flags=pygame.BLEND_RGBA_MULT
              if False else 0)
    # Simpler: just alpha blit
    surf.blit(s, (pos[0] - r, pos[1] - r))

def spray_paint(surf, pos, color, size, opacity):
    """Scatter random dots in a circle — simulates spray can."""
    radius  = size * 2
    density = size * 3
    for _ in range(density):
        angle = math.radians(pygame.math.Vector2(1, 0).rotate(
            math.degrees(math.atan2(*([0, 0])))))  # just use random
        import random
        a = random.uniform(0, 2 * math.pi)
        r = random.uniform(0, radius)
        dx, dy = int(math.cos(a) * r), int(math.sin(a) * r)
        px, py = pos[0] + dx, pos[1] + dy
        if 0 <= px < surf.get_width() and 0 <= py < surf.get_height():
            s = pygame.Surface((3, 3), pygame.SRCALPHA)
            s.fill((*color, opacity))
            surf.blit(s, (px - 1, py - 1))

def flood_fill(surf, pos, new_color):
    """
    BFS flood fill on the canvas surface.
    Replaces the colour at pos with new_color.
    """
    if not (0 <= pos[0] < surf.get_width() and 0 <= pos[1] < surf.get_height()):
        return
    target = surf.get_at(pos)[:3]
    if target == new_color[:3]:
        return

    visited = set()
    queue   = [pos]
    w, h    = surf.get_width(), surf.get_height()

    while queue:
        cx, cy = queue.pop()
        if (cx, cy) in visited or not (0 <= cx < w and 0 <= cy < h):
            continue
        if surf.get_at((cx, cy))[:3] != target:
            continue
        visited.add((cx, cy))
        surf.set_at((cx, cy), new_color)
        for nx, ny in ((cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)):
            if (nx, ny) not in visited:
                queue.append((nx, ny))

# ─── TOOLBAR DRAWING ──────────────────────────────────────────────────────────
def draw_toolbar():
    # Background
    pygame.draw.rect(screen, PANEL, (0, 0, TOOLBAR_W, SH))
    pygame.draw.line(screen, BORDER, (TOOLBAR_W - 1, 0), (TOOLBAR_W - 1, SH), 1)

    y = 10

    # ── Title ────────────────────────────────────────────────────────────────
    t = font_md.render("🖌  Drawing App", True, TEXT_COL)
    screen.blit(t, (10, y)); y += 30

    # ── Tools ────────────────────────────────────────────────────────────────
    pygame.draw.line(screen, BORDER, (8, y), (TOOLBAR_W - 8, y), 1); y += 6
    screen.blit(font_sm.render("TOOLS", True, (120, 120, 160)), (10, y)); y += 18

    cols, col_w = 2, (TOOLBAR_W - 20) // 2
    for i, name in enumerate(TOOLS):
        col  = i % cols
        row  = i // cols
        bx   = 10 + col * (col_w + 4)
        by   = y + row * 28
        sel  = state["tool"] == name
        c    = ACCENT if sel else (55, 55, 75)
        pygame.draw.rect(screen, c,      (bx, by, col_w, 24), border_radius=4)
        pygame.draw.rect(screen, BORDER, (bx, by, col_w, 24), 1, border_radius=4)
        screen.blit(font_sm.render(name, True, TEXT_COL), (bx + 4, by + 5))

    y += (len(TOOLS) // cols + 1) * 28 + 6

    # ── Brush size ────────────────────────────────────────────────────────────
    pygame.draw.line(screen, BORDER, (8, y), (TOOLBAR_W - 8, y), 1); y += 6
    screen.blit(font_sm.render(f"SIZE:  {state['size']}px", True, TEXT_COL), (10, y)); y += 18
    # Slider track
    slider_x, slider_w = 14, TOOLBAR_W - 28
    pygame.draw.rect(screen, (60, 60, 80), (slider_x, y + 4, slider_w, 8), border_radius=4)
    fill_w = int(slider_w * (state["size"] - 1) / 49)
    pygame.draw.rect(screen, ACCENT, (slider_x, y + 4, fill_w, 8), border_radius=4)
    # Handle
    hx = slider_x + fill_w
    pygame.draw.circle(screen, TEXT_COL, (hx, y + 8), 8)
    state["_size_slider"] = (slider_x, y, slider_w)   # store for mouse hit-test
    y += 26

    # ── Opacity ───────────────────────────────────────────────────────────────
    screen.blit(font_sm.render(f"OPACITY:  {int(state['opacity']/2.55)}%", True, TEXT_COL), (10, y)); y += 18
    pygame.draw.rect(screen, (60, 60, 80), (slider_x, y + 4, slider_w, 8), border_radius=4)
    op_w = int(slider_w * state["opacity"] / 255)
    pygame.draw.rect(screen, (180, 180, 200), (slider_x, y + 4, op_w, 8), border_radius=4)
    pygame.draw.circle(screen, TEXT_COL, (slider_x + op_w, y + 8), 8)
    state["_opacity_slider"] = (slider_x, y, slider_w)
    y += 26

    # ── Active colour preview ─────────────────────────────────────────────────
    pygame.draw.line(screen, BORDER, (8, y), (TOOLBAR_W - 8, y), 1); y += 6
    screen.blit(font_sm.render("COLOUR", True, TEXT_COL), (10, y)); y += 18
    pygame.draw.rect(screen, state["color"],  (10, y, 40, 28), border_radius=4)
    pygame.draw.rect(screen, TEXT_COL,        (10, y, 40, 28), 1, border_radius=4)
    cr, cg, cb = state["color"]
    screen.blit(font_xs.render(f"#{cr:02X}{cg:02X}{cb:02X}", True, TEXT_COL), (56, y + 7))
    y += 36

    # ── Palette ───────────────────────────────────────────────────────────────
    pygame.draw.line(screen, BORDER, (8, y), (TOOLBAR_W - 8, y), 1); y += 6
    screen.blit(font_sm.render("PALETTE", True, TEXT_COL), (10, y)); y += 18
    sw_size = 20
    sw_gap  = 3
    per_row = (TOOLBAR_W - 16) // (sw_size + sw_gap)
    for i, (name, col) in enumerate(PALETTE):
        sx = 10 + (i % per_row) * (sw_size + sw_gap)
        sy = y + (i // per_row) * (sw_size + sw_gap)
        sel = state["color"] == col
        pygame.draw.rect(screen, col,  (sx, sy, sw_size, sw_size), border_radius=3)
        if sel:
            pygame.draw.rect(screen, WHITE, (sx - 1, sy - 1, sw_size + 2, sw_size + 2), 2, border_radius=3)
        elif state["hovered_swatch"] == i:
            pygame.draw.rect(screen, TEXT_COL, (sx, sy, sw_size, sw_size), 1, border_radius=3)
        state.setdefault("_swatches", []).append((sx, sy, sw_size, col))  # store for hit-test
    y += (len(PALETTE) // per_row + 1) * (sw_size + sw_gap) + 6

    # ── Actions ───────────────────────────────────────────────────────────────
    pygame.draw.line(screen, BORDER, (8, y), (TOOLBAR_W - 8, y), 1); y += 6
    actions = [("Undo  Ctrl+Z", "undo"), ("Redo  Ctrl+Y", "redo"),
               ("Clear  C",     "clear"), ("Save  S",      "save")]
    for label, key in actions:
        pygame.draw.rect(screen, (50, 50, 70), (10, y, TOOLBAR_W - 20, 24), border_radius=4)
        pygame.draw.rect(screen, BORDER,       (10, y, TOOLBAR_W - 20, 24), 1, border_radius=4)
        screen.blit(font_sm.render(label, True, TEXT_COL), (14, y + 5))
        y += 28

    # ── Save toast ────────────────────────────────────────────────────────────
    if pygame.time.get_ticks() - state["save_tick"] < 2500:
        t2 = font_sm.render("✔  Saved as drawing.png", True, (100, 230, 120))
        screen.blit(t2, (10, SH - 30))

    # ── Cursor preview ────────────────────────────────────────────────────────
    mx, my = pygame.mouse.get_pos()
    if on_canvas((mx, my)) and state["tool"] in ("Pencil", "Brush", "Spray", "Eraser"):
        r = max(1, state["size"] // 2)
        s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*state["color"], 120), (r + 1, r + 1), r)
        pygame.draw.circle(s, (0, 0, 0, 180),         (r + 1, r + 1), r, 1)
        screen.blit(s, (mx - r - 1, my - r - 1))

def draw_canvas_area():
    screen.blit(canvas, (CANVAS_X, 0))

    # Live shape preview while dragging
    if state["shape_snap"] and state["shape_start"] and state["drawing"]:
        screen.blit(state["shape_snap"], (CANVAS_X, 0))

def draw_status_bar():
    mx, my = pygame.mouse.get_pos()
    cx, cy = canvas_pos((mx, my))
    cx = max(0, min(CANVAS_W - 1, cx))
    cy = max(0, min(CANVAS_H - 1, cy))
    info = f"  {state['tool']}  ·  ({cx}, {cy})  ·  Undo: {len(undo_stack)}  ·  FPS: {int(clock.get_fps())}"
    t = font_xs.render(info, True, (150, 150, 170))
    screen.blit(t, (CANVAS_X + 6, SH - 18))

# ─── INPUT HANDLING ───────────────────────────────────────────────────────────
_size_dragging    = False
_opacity_dragging = False

WHITE = (255, 255, 255)

def handle_event(event):
    global _size_dragging, _opacity_dragging

    if event.type == pygame.QUIT:
        pygame.quit(); sys.exit()

    # ── Keyboard ──────────────────────────────────────────────────────────────
    if event.type == pygame.KEYDOWN:
        ctrl = pygame.key.get_mods() & pygame.KMOD_CTRL
        if ctrl and event.key == pygame.K_z:   undo()
        elif ctrl and event.key == pygame.K_y: redo()
        elif ctrl and event.key == pygame.K_s: do_save()
        elif event.key == pygame.K_c:          canvas.fill(WHITE); push_undo(); undo_stack.clear()
        elif event.key == pygame.K_s and not ctrl: do_save()
        elif event.key == pygame.K_UP:   state["size"] = min(50, state["size"] + 1)
        elif event.key == pygame.K_DOWN: state["size"] = max(1,  state["size"] - 1)
        # Tool hotkeys
        hotkeys = {"p": "Pencil", "b": "Brush", "a": "Spray", "l": "Line",
                   "r": "Rect",   "e": "Ellipse", "f": "Fill", "x": "Eraser"}
        ch = pygame.key.name(event.key)
        if ch in hotkeys:
            state["tool"] = hotkeys[ch]

    # ── Mouse button down ─────────────────────────────────────────────────────
    if event.type == pygame.MOUSEBUTTONDOWN:
        mx, my = event.pos

        # Size slider
        sx, sy, sw = state.get("_size_slider", (0, 0, 0))
        if sx <= mx <= sx + sw and sy <= my <= sy + 16:
            _size_dragging = True

        # Opacity slider
        ox, oy, ow = state.get("_opacity_slider", (0, 0, 0))
        if ox <= mx <= ox + ow and oy <= my <= oy + 16:
            _opacity_dragging = True

        # Palette swatches
        state["_swatches"] = []  # rebuilt each draw_toolbar call
        # Re-compute swatch hit zones directly
        sw_size, sw_gap = 20, 3
        per_row = (TOOLBAR_W - 16) // (sw_size + sw_gap)
        # Palette starts after header — easier to just do pixel check
        for i, (name, col) in enumerate(PALETTE):
            px = 10 + (i % per_row) * (sw_size + sw_gap)
            # Approximate y — re-derive from toolbar layout:
            # Rough top = 10+30+6+6+18+(len(TOOLS)//2+1)*28+6+6+18+26+6+18+36+6+18
            pal_y_approx = 10+30+8+18+(len(TOOLS)//2+1)*28+8+18+26+18+26+6+18+36+8+18
            py_s = pal_y_approx + (i // per_row) * (sw_size + sw_gap)
            if px <= mx <= px + sw_size and py_s <= my <= py_s + sw_size:
                state["color"] = col

        # Tool buttons
        col_w = (TOOLBAR_W - 20) // 2
        tool_y0 = 10 + 30 + 8 + 18   # approx top of tool grid
        for i, name in enumerate(TOOLS):
            col_i = i % 2
            row_i = i // 2
            bx = 10 + col_i * (col_w + 4)
            by = tool_y0 + row_i * 28
            if bx <= mx <= bx + col_w and by <= my <= by + 24:
                state["tool"] = name

        # Canvas drawing start
        if on_canvas(event.pos):
            cp = canvas_pos(event.pos)
            if state["tool"] == "Fill":
                push_undo()
                flood_fill(canvas, cp, state["color"])
            else:
                push_undo()
                state["drawing"]    = True
                state["last_pos"]   = cp
                state["shape_start"]= cp
                if state["tool"] in ("Pencil", "Brush", "Eraser"):
                    # Draw a dot on click (no drag needed)
                    col = WHITE if state["tool"] == "Eraser" else state["color"]
                    draw_brush_stamp(canvas, cp, col, state["size"], state["opacity"])

    # ── Mouse button up ───────────────────────────────────────────────────────
    if event.type == pygame.MOUSEBUTTONUP:
        _size_dragging = _opacity_dragging = False
        if state["drawing"] and state["tool"] in ("Line", "Rect", "Ellipse"):
            # Commit the live preview onto the canvas
            cp = canvas_pos(event.pos)
            draw_shape_final(canvas, state["shape_start"], cp)
        state["drawing"]     = False
        state["last_pos"]    = None
        state["shape_start"] = None
        state["shape_snap"]  = None

    # ── Mouse motion ──────────────────────────────────────────────────────────
    if event.type == pygame.MOUSEMOTION:
        mx, my = event.pos

        # Dragging size slider
        if _size_dragging:
            sx, sy, sw = state.get("_size_slider", (0, 0, 1))
            pct = max(0.0, min(1.0, (mx - sx) / sw))
            state["size"] = max(1, min(50, int(pct * 49) + 1))

        # Dragging opacity slider
        if _opacity_dragging:
            ox, oy, ow = state.get("_opacity_slider", (0, 0, 1))
            pct = max(0.0, min(1.0, (mx - ox) / ow))
            state["opacity"] = int(pct * 255)

        # Swatch hover detection
        sw_size, sw_gap = 20, 3
        per_row  = (TOOLBAR_W - 16) // (sw_size + sw_gap)
        pal_y0   = 10+30+8+18+(len(TOOLS)//2+1)*28+8+18+26+18+26+6+18+36+8+18
        state["hovered_swatch"] = -1
        for i in range(len(PALETTE)):
            px = 10 + (i % per_row) * (sw_size + sw_gap)
            py_s = pal_y0 + (i // per_row) * (sw_size + sw_gap)
            if px <= mx <= px + sw_size and py_s <= my <= py_s + sw_size:
                state["hovered_swatch"] = i

        # Freehand drawing
        if state["drawing"] and on_canvas((mx, my)):
            cp  = canvas_pos((mx, my))
            lp  = state["last_pos"]
            col = WHITE if state["tool"] == "Eraser" else state["color"]
            sz  = state["size"] * 3 if state["tool"] == "Eraser" else state["size"]

            if state["tool"] in ("Pencil", "Brush", "Eraser") and lp:
                for pt in lerp_points(lp, cp):
                    draw_brush_stamp(canvas, pt, col, sz, state["opacity"])

            elif state["tool"] == "Spray" and lp:
                spray_paint(canvas, cp, col, state["size"], state["opacity"])

            elif state["tool"] in ("Line", "Rect", "Ellipse"):
                # Build live preview on a transparent overlay
                snap = canvas.copy()
                draw_shape_final(snap, state["shape_start"], cp)
                state["shape_snap"] = snap

            state["last_pos"] = cp

def draw_shape_final(surf, start, end):
    """Draw the committed shape (line / rect / ellipse) onto surf."""
    col = state["color"]
    sz  = max(1, state["size"] // 3)
    if state["tool"] == "Line":
        pygame.draw.line(surf, col, start, end, sz)
    elif state["tool"] == "Rect":
        x0, y0 = min(start[0], end[0]), min(start[1], end[1])
        w  = abs(end[0] - start[0])
        h  = abs(end[1] - start[1])
        pygame.draw.rect(surf, col, (x0, y0, w, h), sz)
    elif state["tool"] == "Ellipse":
        x0, y0 = min(start[0], end[0]), min(start[1], end[1])
        w  = abs(end[0] - start[0])
        h  = abs(end[1] - start[1])
        if w > 0 and h > 0:
            pygame.draw.ellipse(surf, col, (x0, y0, w, h), sz)

def do_save():
    pygame.image.save(canvas, "drawing.png")
    state["save_tick"] = pygame.time.get_ticks()

# ─── MAIN LOOP ────────────────────────────────────────────────────────────────
pygame.mouse.set_visible(True)   # we draw our own cursor preview on canvas

while True:
    state["_swatches"] = []   # reset each frame before rebuild

    for event in pygame.event.get():
        handle_event(event)

    # ── Render ────────────────────────────────────────────────────────────────
    screen.fill(BG)
    draw_canvas_area()
    draw_toolbar()           # draws on top (toolbar is in screen-space)
    draw_status_bar()
    pygame.display.flip()
    clock.tick(FPS)
