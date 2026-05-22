"""
pong_pdf_generator.py
Generates a self-contained, playable Pong game inside a PDF file.
The game runs via Acrobat/Adobe Reader's built-in JavaScript engine.

How to play after opening the PDF in Adobe Reader / Acrobat:
  - Click "Start"
  - Click "▲ Up" / "▼ Down" buttons to move your paddle (left side)
  - The AI controls the right paddle automatically
  - First to 7 points wins
  - Click "Restart" to play again

Controls are buttons because PDF JavaScript cannot reliably capture
keyboard events without focus tricks across all Reader versions.
"""

import struct
import math
import io

# ─── CONFIGURATION ────────────────────────────────────────────────────────────
GRID_W   = 22          # grid columns (pixels wide)
GRID_H   = 20          # grid rows   (pixels tall)
PX       = 22          # pixel size in PDF points
GRID_X   = 90          # grid left edge (PDF points from bottom-left)
GRID_Y   = 130         # grid bottom edge
WIN_W    = 700         # page width
WIN_H    = 600         # page height
WIN_SCORE = 7          # first to this score wins


# ─── LOW-LEVEL PDF BUILDER ────────────────────────────────────────────────────
class PDFBuilder:
    """
    Minimal but structurally correct PDF builder.
    Tracks every object's byte offset so the xref table is accurate,
    which is the main reason the original script produced unreadable files.
    """
    def __init__(self):
        self.buf      = io.BytesIO()
        self.offsets  = {}   # obj_id → byte offset in file
        self.next_id  = 1

    def _w(self, data: bytes):
        self.buf.write(data)

    def tell(self):
        return self.buf.tell()

    def alloc(self) -> int:
        """Reserve an object ID without writing anything yet."""
        oid = self.next_id
        self.next_id += 1
        return oid

    def begin_obj(self, oid: int):
        self.offsets[oid] = self.tell()
        self._w(f"{oid} 0 obj\n".encode())

    def end_obj(self):
        self._w(b"endobj\n\n")

    def write_stream(self, oid: int, content: str, extra: dict = None):
        """Write a stream object; length is computed automatically."""
        data   = content.encode("latin-1", errors="replace")
        fields = "/Length " + str(len(data))
        if extra:
            for k, v in extra.items():
                fields += f"\n  {k} {v}"
        self.begin_obj(oid)
        self._w(f"<<\n  {fields}\n>>\nstream\n".encode())
        self._w(data)
        self._w(b"\nendstream\n")
        self.end_obj()

    def write_dict_obj(self, oid: int, content: str):
        self.begin_obj(oid)
        self._w(f"<< {content} >>\n".encode())
        self.end_obj()

    def header(self):
        self._w(b"%PDF-1.6\n%\xe2\xe3\xcf\xd3\n")  # binary comment flags binary content

    def xref_and_trailer(self, root_id: int):
        """Write the cross-reference table and trailer — the part the original was missing."""
        xref_pos = self.tell()
        count    = self.next_id
        self._w(b"xref\n")
        self._w(f"0 {count}\n".encode())
        # Free object 0 (always present in PDF)
        self._w(b"0000000000 65535 f \n")
        for i in range(1, count):
            off = self.offsets.get(i, 0)
            self._w(f"{off:010d} 00000 n \n".encode())
        self._w(
            f"trailer\n<< /Size {count} /Root {root_id} 0 R >>\n"
            f"startxref\n{xref_pos}\n%%EOF\n".encode()
        )

    def getvalue(self) -> bytes:
        return self.buf.getvalue()


# ─── JAVASCRIPT GAME LOGIC ────────────────────────────────────────────────────
def make_game_js(grid_w, grid_h, win_score) -> str:
    """
    Full Pong game in Acrobat JavaScript.
    Uses app.setInterval for the game loop.
    Paddle colour: dark green.  Ball colour: orange-red.  Background: dark navy.
    """
    return f"""
// ── Helpers ────────────────────────────────────────────────────────────────
function safeInterval(cb, ms) {{
    try {{
        return app.setInterval(
            "try{{(" + cb.toString() + ")();}}catch(e){{}}",
            ms
        );
    }} catch(e) {{ return null; }}
}}

// ── Constants ─────────────────────────────────────────────────────────────
var GW = {grid_w};
var GH = {grid_h};
var WIN = {win_score};

// Colours (PDF colour arrays [R,G,B] in 0-1 range)
var C_BG   = ["color.RGB", 0.04, 0.04, 0.18];   // dark navy background
var C_PADD = ["color.RGB", 0.20, 0.90, 0.40];   // bright green paddles
var C_BALL = ["color.RGB", 1.00, 0.45, 0.10];   // orange ball
var C_NET  = ["color.RGB", 0.20, 0.20, 0.45];   // dim net stripe
var C_OFF  = ["color.RGB", 0.06, 0.06, 0.22];   // slightly lighter bg for off pixels

// ── State ──────────────────────────────────────────────────────────────────
var pp = {{ y: 8, h: 4 }};    // player paddle (left)
var ap = {{ y: 8, h: 4 }};    // ai    paddle (right)
var ball = {{ x: GW/2, y: GH/2, dx: 1, dy: 1 }};
var ps = 0, as_ = 0;
var gInterval = null;
var paused = false;
var gameOver = false;

// Cache field references for performance (avoid getField on every frame)
var cache = [];
for (var cx = 0; cx < GW; cx++) {{
    cache[cx] = [];
    for (var cy = 0; cy < GH; cy++) {{
        cache[cx][cy] = this.getField("P_" + cx + "_" + cy);
    }}
}}

function pix(x, y, col) {{
    if (x < 0 || y < 0 || x >= GW || y >= GH) return;
    var f = cache[x][y];
    if (!f) return;
    f.fillColor = col;
}}

// ── Initialise ─────────────────────────────────────────────────────────────
function initGame() {{
    if (gInterval) {{ app.clearInterval(gInterval); gInterval = null; }}
    pp.y = Math.floor(GH/2) - 2;
    ap.y = Math.floor(GH/2) - 2;
    resetBall(1);
    ps = 0; as_ = 0; paused = false; gameOver = false;
    updateScore();
    renderAll();
    showBtn("B_start",   true);
    showBtn("B_pause",   false);
    showBtn("B_resume",  false);
    showBtn("B_restart", false);
    app.execMenuItem("FitPage");
}}

function resetBall(dir) {{
    ball.x  = GW / 2;
    ball.y  = GH / 2;
    ball.dx = dir;
    ball.dy = (Math.random() > 0.5) ? 1 : -1;
}}

function showBtn(name, visible) {{
    var f = this.getField(name);
    if (f) f.display = visible ? display.visible : display.hidden;
}}

// ── Controls ───────────────────────────────────────────────────────────────
function startGame() {{
    if (gInterval) return;
    gInterval = safeInterval(gameLoop, 120);
    showBtn("B_start",  false);
    showBtn("B_pause",  true);
}}

function pauseGame() {{
    paused = !paused;
    showBtn("B_pause",  !paused);
    showBtn("B_resume",  paused);
}}

function moveUp()   {{ pp.y = Math.max(0, pp.y - 1); renderPaddles(); }}
function moveDown() {{ pp.y = Math.min(GH - pp.h, pp.y + 1); renderPaddles(); }}

// ── Game loop ──────────────────────────────────────────────────────────────
function gameLoop() {{
    if (paused || gameOver) return;
    moveBall();
    moveAI();
    renderAll();
}}

function moveBall() {{
    ball.x += ball.dx;
    ball.y += ball.dy;

    // Top/bottom wall bounce
    if (ball.y <= 0)       {{ ball.dy =  1; ball.y = 0;      }}
    if (ball.y >= GH - 1)  {{ ball.dy = -1; ball.y = GH - 1; }}

    // Player paddle (x = 1)
    if (ball.dx < 0 && ball.x <= 1 &&
        ball.y >= pp.y && ball.y < pp.y + pp.h) {{
        ball.dx = 1;
        ball.x  = 1;
        // Add slight angle based on where ball hits paddle
        var rel = (ball.y - (pp.y + pp.h / 2)) / (pp.h / 2);
        ball.dy = rel * 1.2;
        if (Math.abs(ball.dy) < 0.3) ball.dy = ball.dy >= 0 ? 0.3 : -0.3;
    }}

    // AI paddle (x = GW-2)
    if (ball.dx > 0 && ball.x >= GW - 2 &&
        ball.y >= ap.y && ball.y < ap.y + ap.h) {{
        ball.dx = -1;
        ball.x  = GW - 2;
        var rel2 = (ball.y - (ap.y + ap.h / 2)) / (ap.h / 2);
        ball.dy = rel2 * 1.2;
        if (Math.abs(ball.dy) < 0.3) ball.dy = ball.dy >= 0 ? 0.3 : -0.3;
    }}

    // Scoring: ball exits left or right
    if (ball.x < 0) {{
        as_++;
        updateScore();
        checkWin();
        resetBall(1);
    }}
    if (ball.x >= GW) {{
        ps++;
        updateScore();
        checkWin();
        resetBall(-1);
    }}
}}

function moveAI() {{
    // AI tracks ball centre with a slight delay proportional to difficulty
    var target = ball.y - ap.h / 2;
    var diff   = target - ap.y;
    // AI speed: 0.55 units/frame (beatable but challenging)
    ap.y += Math.max(-0.55, Math.min(0.55, diff));
    ap.y  = Math.max(0, Math.min(GH - ap.h, Math.round(ap.y)));
}}

function updateScore() {{
    var fs = this.getField("T_score");
    if (fs) fs.value = "YOU  " + ps + "   :   " + as_ + "  AI";
}}

function checkWin() {{
    if (ps >= WIN || as_ >= WIN) {{
        gameOver = true;
        app.clearInterval(gInterval); gInterval = null;
        var fw = this.getField("T_winner");
        if (fw) fw.value = ps >= WIN ? "YOU WIN!" : "AI WINS";
        showBtn("B_restart", true);
        showBtn("B_pause",   false);
    }}
}}

// ── Rendering ──────────────────────────────────────────────────────────────
function renderAll() {{
    // Background
    for (var rx = 0; rx < GW; rx++) {{
        for (var ry = 0; ry < GH; ry++) {{
            // Centre net column
            var bg = (rx === Math.floor(GW / 2)) ? C_NET : C_BG;
            pix(rx, ry, bg);
        }}
    }}
    renderPaddles();
    renderBall();
}}

function renderPaddles() {{
    // Clear paddle columns first
    for (var ry = 0; ry < GH; ry++) {{
        pix(0,      ry, C_BG);
        pix(GW - 1, ry, C_BG);
    }}
    // Player paddle
    for (var i = 0; i < pp.h; i++) {{
        var py = Math.round(pp.y) + i;
        if (py >= 0 && py < GH) pix(0, py, C_PADD);
    }}
    // AI paddle
    for (var i = 0; i < ap.h; i++) {{
        var ay = Math.round(ap.y) + i;
        if (ay >= 0 && ay < GH) pix(GW - 1, ay, C_PADD);
    }}
}}

function renderBall() {{
    var bx = Math.round(ball.x);
    var by = Math.round(ball.y);
    if (bx >= 0 && bx < GW && by >= 0 && by < GH) pix(bx, by, C_BALL);
}}

// ── Boot ───────────────────────────────────────────────────────────────────
initGame();
"""


# ─── PDF CONSTRUCTION ─────────────────────────────────────────────────────────
def build_pdf() -> bytes:
    pdf = PDFBuilder()
    pdf.header()

    # ── Pre-allocate all object IDs ───────────────────────────────────────────
    id_catalog    = pdf.alloc()   # 1
    id_pages      = pdf.alloc()   # 2
    id_page       = pdf.alloc()   # 3
    id_content    = pdf.alloc()   # 4  (empty page content stream)
    id_font       = pdf.alloc()   # 5  (Helvetica-Bold)
    id_js_main    = pdf.alloc()   # 6  (main game JS, runs on open)
    id_open_action= pdf.alloc()   # 7  (OpenAction dictionary)
    id_annots_arr = pdf.alloc()   # 8  (array listing all widget annotations)

    # ── Pixel fields: one per grid cell ──────────────────────────────────────
    pixel_ids = {}
    for x in range(GRID_W):
        for y in range(GRID_H):
            pixel_ids[(x, y)] = pdf.alloc()

    # ── Button / text control objects ────────────────────────────────────────
    # Each button needs: JS stream, AP stream, annotation dict → 3 objects
    def alloc_btn():
        return (pdf.alloc(), pdf.alloc(), pdf.alloc())

    def alloc_text():
        return (pdf.alloc(), pdf.alloc())   # JS stream + annotation

    btn_start   = alloc_btn()
    btn_up      = alloc_btn()
    btn_down    = alloc_btn()
    btn_pause   = alloc_btn()
    btn_resume  = alloc_btn()
    btn_restart = alloc_btn()
    txt_score   = alloc_text()
    txt_winner  = alloc_text()

    # Collect all annotation (widget) IDs for the page /Annots array
    all_annot_ids = list(pixel_ids.values())
    for js_id, ap_id, ann_id in [btn_start, btn_up, btn_down, btn_pause, btn_resume, btn_restart]:
        all_annot_ids.append(ann_id)
    for js_id, ann_id in [txt_score, txt_winner]:
        all_annot_ids.append(ann_id)
    all_annot_ids.append(id_annots_arr)   # placeholder; overwrite below

    annots_ref_str = " ".join(f"{i} 0 R" for i in all_annot_ids[:-1])

    # ── Object 1: Catalog ────────────────────────────────────────────────────
    acro_fields = " ".join(f"{i} 0 R" for i in all_annot_ids[:-1])
    pdf.begin_obj(id_catalog)
    pdf.buf.write(
        f"<<\n"
        f"  /Type /Catalog\n"
        f"  /Pages {id_pages} 0 R\n"
        f"  /OpenAction {id_open_action} 0 R\n"
        f"  /AcroForm <<\n"
        f"    /Fields [ {acro_fields} ]\n"
        f"    /DR << /Font << /HeBo {id_font} 0 R >> >>\n"
        f"  >>\n"
        f">>\n".encode()
    )
    pdf.end_obj()

    # ── Object 2: Pages ──────────────────────────────────────────────────────
    pdf.begin_obj(id_pages)
    pdf.buf.write(
        f"<< /Type /Pages /Count 1 /Kids [ {id_page} 0 R ] >>\n".encode()
    )
    pdf.end_obj()

    # ── Object 3: Page ───────────────────────────────────────────────────────
    pdf.begin_obj(id_page)
    pdf.buf.write((
        f"<<\n"
        f"  /Type /Page\n"
        f"  /Parent {id_pages} 0 R\n"
        f"  /MediaBox [ 0 0 {WIN_W} {WIN_H} ]\n"
        f"  /Contents {id_content} 0 R\n"
        f"  /Annots [ {annots_ref_str} ]\n"
        f"  /Resources << /Font << /HeBo {id_font} 0 R >> >>\n"
        f">>\n"
    ).encode())
    pdf.end_obj()

    # ── Object 4: Page content (draws title text via PDF operators) ───────────
    title_y = GRID_Y + GRID_H * PX + 28
    page_content = (
        f"BT\n"
        f"/HeBo 18 Tf\n"
        f"0.6 0.9 1.0 rg\n"
        f"{GRID_X} {title_y} Td\n"
        f"(PONG  \xe2\x80\x94  Play inside your PDF) Tj\n"
        f"ET\n"
        # instructions below grid
        f"BT\n"
        f"/HeBo 11 Tf\n"
        f"0.5 0.5 0.7 rg\n"
        f"{GRID_X} {GRID_Y - 28} Td\n"
        f"(Use [Up] [Down] buttons to move your paddle  |  First to {WIN_SCORE} wins) Tj\n"
        f"ET\n"
    )
    pdf.write_stream(id_content, page_content)

    # ── Object 5: Font (Helvetica-Bold — always available in PDF viewers) ─────
    pdf.begin_obj(id_font)
    pdf.buf.write(
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold "
        b"/Encoding /WinAnsiEncoding >>\n"
    )
    pdf.end_obj()

    # ── Object 6: Main game JavaScript ───────────────────────────────────────
    js = make_game_js(GRID_W, GRID_H, WIN_SCORE)
    pdf.write_stream(id_js_main, js)

    # ── Object 7: OpenAction (run JS on document open) ────────────────────────
    pdf.begin_obj(id_open_action)
    pdf.buf.write(
        f"<< /Type /Action /S /JavaScript /JS {id_js_main} 0 R >>\n".encode()
    )
    pdf.end_obj()

    # ── Object 8: Annots array placeholder (not actually used — embedded in page)
    pdf.begin_obj(id_annots_arr)
    pdf.buf.write(b"<< >>\n")
    pdf.end_obj()

    # ── Pixel widgets ─────────────────────────────────────────────────────────
    # PDF Y-axis is bottom-up, grid Y=0 is the top row visually,
    # so we flip: pdf_y = GRID_Y + (GRID_H - 1 - grid_y) * PX
    for (gx, gy), oid in pixel_ids.items():
        pdf_x1 = GRID_X + gx * PX
        pdf_y1 = GRID_Y + (GRID_H - 1 - gy) * PX
        pdf_x2 = pdf_x1 + PX
        pdf_y2 = pdf_y1 + PX
        pdf.begin_obj(oid)
        pdf.buf.write((
            f"<<\n"
            f"  /Type /Annot /Subtype /Widget\n"
            f"  /FT /Btn /Ff 1\n"
            f"  /P {id_page} 0 R\n"
            f"  /Rect [ {pdf_x1} {pdf_y1} {pdf_x2} {pdf_y2} ]\n"
            f"  /T (P_{gx}_{gy})\n"
            f"  /MK << /BG [ 0.04 0.04 0.18 ] /BC [ 0.08 0.08 0.25 ] >>\n"
            f"  /Border [ 0 0 0.5 ]\n"
            f">>\n"
        ).encode())
        pdf.end_obj()

    # ── Button helper ─────────────────────────────────────────────────────────
    def write_button(ids, label, name, x, y, w, h, js_code, hidden=False):
        js_id, ap_id, ann_id = ids

        # JS stream
        pdf.write_stream(js_id, js_code)

        # AP (appearance) stream — draws the button face
        ap_js = (
            f"q\n"
            f"0.15 0.15 0.40 rg\n"
            f"0 0 {w} {h} re f\n"      # dark blue fill
            f"0.4 0.7 1.0 RG\n"
            f"0.8 w\n"
            f"0 0 {w} {h} re S\n"      # cyan border
            f"Q\n"
            f"BT\n"
            f"/HeBo 11 Tf\n"
            f"0.9 0.95 1.0 rg\n"
            f"5 {h//2 - 5} Td\n"
            f"({label}) Tj\n"
            f"ET\n"
        )
        pdf.begin_obj(ap_id)
        ap_bytes = ap_js.encode("latin-1")
        pdf.buf.write((
            f"<< /Type /XObject /Subtype /Form\n"
            f"   /BBox [0 0 {w} {h}]\n"
            f"   /Resources << /Font << /HeBo {id_font} 0 R >> >>\n"
            f"   /Length {len(ap_bytes)} >>\n"
            f"stream\n"
        ).encode())
        pdf.buf.write(ap_bytes)
        pdf.buf.write(b"\nendstream\n")
        pdf.end_obj()

        # Annotation
        disp = "display.hidden" if hidden else "display.visible"
        pdf.begin_obj(ann_id)
        pdf.buf.write((
            f"<<\n"
            f"  /Type /Annot /Subtype /Widget\n"
            f"  /FT /Btn /Ff 65536\n"
            f"  /F 4\n"
            f"  /P {id_page} 0 R\n"
            f"  /Rect [ {x} {y} {x+w} {y+h} ]\n"
            f"  /T ({name})\n"
            f"  /MK << /CA ({label}) /BG [0.15 0.15 0.40] >>\n"
            f"  /AP << /N {ap_id} 0 R >>\n"
            f"  /A << /S /JavaScript /JS {js_id} 0 R >>\n"
            f">>\n"
        ).encode())
        pdf.end_obj()

    # ── Text field helper ──────────────────────────────────────────────────────
    def write_text(ids, default_val, name, x, y, w, h):
        js_id, ann_id = ids
        pdf.begin_obj(js_id)
        pdf.buf.write(b"<< /Length 0 >>\nstream\nendstream\n")
        pdf.end_obj()
        pdf.begin_obj(ann_id)
        pdf.buf.write((
            f"<<\n"
            f"  /Type /Annot /Subtype /Widget\n"
            f"  /FT /Tx /F 4\n"
            f"  /P {id_page} 0 R\n"
            f"  /Rect [ {x} {y} {x+w} {y+h} ]\n"
            f"  /T ({name})\n"
            f"  /V ({default_val})\n"
            f"  /DV ({default_val})\n"
            f"  /DA (/HeBo 14 Tf 0.9 0.9 1 rg)\n"
            f"  /MK << /BG [0.06 0.06 0.22] >>\n"
            f"  /Border [0 0 0]\n"
            f">>\n"
        ).encode())
        pdf.end_obj()

    # ── Layout constants ──────────────────────────────────────────────────────
    grid_right   = GRID_X + GRID_W * PX    # right edge of grid
    grid_top     = GRID_Y + GRID_H * PX    # top  edge of grid
    btn_w, btn_h = 80, 30

    # Score bar spans full grid width above the grid
    score_y = GRID_Y + GRID_H * PX + 4
    write_text(txt_score,  f"YOU  0   :   0  AI", "T_score",
               GRID_X, score_y, GRID_W * PX, 24)

    # Winner banner centred in the grid (hidden until game over)
    write_text(txt_winner, "", "T_winner",
               GRID_X + GRID_W * PX // 2 - 80, GRID_Y + GRID_H * PX // 2 - 15, 160, 30)

    # Control buttons to the right of the grid
    ctrl_x = grid_right + 14

    write_button(btn_up,      "▲ Up",    "B_up",
                 ctrl_x, GRID_Y + GRID_H * PX - 70, btn_w, btn_h,
                 "moveUp();")
    write_button(btn_down,    "▼ Down",  "B_down",
                 ctrl_x, GRID_Y + GRID_H * PX - 110, btn_w, btn_h,
                 "moveDown();")

    # Start button (centred over grid, shown initially)
    sx = GRID_X + (GRID_W * PX) // 2 - 50
    sy = GRID_Y + (GRID_H * PX) // 2 - 18
    write_button(btn_start,   "▶ Start",  "B_start",
                 sx, sy, 100, 36,
                 "startGame();")

    write_button(btn_pause,   "⏸ Pause",  "B_pause",
                 ctrl_x, GRID_Y + GRID_H * PX - 150, btn_w, btn_h,
                 "pauseGame();", hidden=True)

    write_button(btn_resume,  "▶ Resume", "B_resume",
                 ctrl_x, GRID_Y + GRID_H * PX - 150, btn_w, btn_h,
                 "pauseGame();", hidden=True)

    write_button(btn_restart, "↺ Restart","B_restart",
                 sx, sy, 100, 36,
                 "initGame(); startGame();", hidden=True)

    # ── xref + trailer ────────────────────────────────────────────────────────
    pdf.xref_and_trailer(id_catalog)
    return pdf.getvalue()


# ─── ENTRY POINT ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    out_path = "/mnt/user-data/outputs/pong_game.pdf"
    data = build_pdf()
    with open(out_path, "wb") as f:
        f.write(data)
    print(f"Written {len(data):,} bytes → {out_path}")
    print("Open in Adobe Acrobat / Adobe Reader and click ▶ Start to play.")
    print("(Other PDF viewers do not support JavaScript and will show a static form.)")
