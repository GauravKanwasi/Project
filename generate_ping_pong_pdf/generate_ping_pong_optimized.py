from dataclasses import dataclass

PDF_TEMPLATE = r"""
%PDF-1.7

1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
/OpenAction 5 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Count 1
/Kids [3 0 R]
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 900 700]
/Resources <<
>>
/Annots [###FIELDS###]
/Contents 4 0 R
>>
endobj

4 0 obj
<< /Length 0 >>
stream
endstream
endobj

5 0 obj
<<
/S /JavaScript
/JS 6 0 R
>>
endobj

6 0 obj
<< /Length ###JS_LEN### >>
stream
###JAVASCRIPT###
endstream
endobj

###OBJECTS###

trailer
<<
/Root 1 0 R
>>
%%EOF
"""

PX = 18
GRID_W = 24
GRID_H = 16

OFFSET_X = 120
OFFSET_Y = 180

objects = []
field_refs = []
obj_id = 10


@dataclass
class ObjRef:
    id: int


def next_id():
    global obj_id
    current = obj_id
    obj_id += 1
    return current


def add_object(content):
    oid = next_id()
    objects.append(f"{oid} 0 obj\n{content}\nendobj\n")
    return oid


def rect(x1, y1, x2, y2):
    return f"[{x1} {y1} {x2} {y2}]"


def pixel_field(x, y):
    rx1 = OFFSET_X + x * PX
    ry1 = OFFSET_Y + y * PX
    rx2 = rx1 + PX
    ry2 = ry1 + PX

    oid = add_object(f"""
<<
/FT /Btn
/Ff 1
/Type /Annot
/Subtype /Widget
/T (P_{x}_{y})
/Rect {rect(rx1, ry1, rx2, ry2)}
/MK << /BG [1 1 1] >>
>>
""")

    field_refs.append(f"{oid} 0 R")


def button(name, label, x, y, w, h, js):
    js_stream = add_object(f"""
<< /Length {len(js)} >>
stream
{js}
endstream
""")

    oid = add_object(f"""
<<
/FT /Btn
/Ff 65536
/Type /Annot
/Subtype /Widget
/T ({name})
/Rect {rect(x, y, x+w, y+h)}
/MK <<
    /CA ({label})
    /BG [0.8 0.8 0.8]
>>
/A <<
    /S /JavaScript
    /JS {js_stream} 0 R
>>
>>
""")

    field_refs.append(f"{oid} 0 R")


def text_field(name, value, x, y, w, h):
    oid = add_object(f"""
<<
/FT /Tx
/Type /Annot
/Subtype /Widget
/T ({name})
/Rect {rect(x, y, x+w, y+h)}
/V ({value})
>>
""")

    field_refs.append(f"{oid} 0 R")


for x in range(GRID_W):
    for y in range(GRID_H):
        pixel_field(x, y)


button(
    "BTN_UP",
    "UP",
    120,
    110,
    70,
    40,
    "movePlayer(-1);"
)

button(
    "BTN_DOWN",
    "DOWN",
    210,
    110,
    70,
    40,
    "movePlayer(1);"
)

button(
    "BTN_START",
    "START",
    350,
    110,
    100,
    40,
    "startGame();"
)

button(
    "BTN_PAUSE",
    "PAUSE",
    470,
    110,
    100,
    40,
    "togglePause();"
)

text_field(
    "TXT_SCORE",
    "Player 0 : 0 AI",
    620,
    110,
    150,
    40
)

javascript = f"""
var W = {GRID_W};
var H = {GRID_H};

var player = {{
    y: 6,
    size: 4
}};

var ai = {{
    y: 6,
    size: 4
}};

var ball = {{
    x: Math.floor(W / 2),
    y: Math.floor(H / 2),
    dx: 1,
    dy: 1
}};

var playerScore = 0;
var aiScore = 0;

var timer = null;
var paused = false;

var grid = [];

function initGrid() {{
    for (var x = 0; x < W; x++) {{
        grid[x] = [];

        for (var y = 0; y < H; y++) {{
            grid[x][y] = this.getField("P_" + x + "_" + y);
        }}
    }}
}}

function setPixel(x, y, type) {{
    if (x < 0 || y < 0 || x >= W || y >= H) return;

    var f = grid[x][y];

    if (type == 0)
        f.fillColor = color.white;
    else if (type == 1)
        f.fillColor = color.blue;
    else
        f.fillColor = color.red;
}}

function clearBoard() {{
    for (var x = 0; x < W; x++) {{
        for (var y = 0; y < H; y++) {{
            setPixel(x, y, 0);
        }}
    }}
}}

function drawPaddle(px, py, size) {{
    for (var i = 0; i < size; i++) {{
        setPixel(px, py + i, 1);
    }}
}}

function drawBall() {{
    setPixel(ball.x, ball.y, 2);
}}

function render() {{
    clearBoard();

    drawPaddle(0, player.y, player.size);
    drawPaddle(W - 1, ai.y, ai.size);

    drawBall();
}}

function movePlayer(dir) {{
    player.y += dir;

    if (player.y < 0)
        player.y = 0;

    if (player.y > H - player.size)
        player.y = H - player.size;

    render();
}}

function updateAI() {{
    var center = ai.y + Math.floor(ai.size / 2);

    if (ball.y > center)
        ai.y++;

    if (ball.y < center)
        ai.y--;

    if (ai.y < 0)
        ai.y = 0;

    if (ai.y > H - ai.size)
        ai.y = H - ai.size;
}}

function resetBall() {{
    ball.x = Math.floor(W / 2);
    ball.y = Math.floor(H / 2);

    ball.dx = Math.random() > 0.5 ? 1 : -1;
    ball.dy = Math.random() > 0.5 ? 1 : -1;
}}

function updateScore() {{
    this.getField("TXT_SCORE").value =
        "Player " + playerScore + " : " + aiScore + " AI";
}}

function physics() {{

    ball.x += ball.dx;
    ball.y += ball.dy;

    if (ball.y <= 0 || ball.y >= H - 1)
        ball.dy *= -1;

    if (
        ball.x == 1 &&
        ball.y >= player.y &&
        ball.y < player.y + player.size
    ) {{
        ball.dx = 1;
    }}

    if (
        ball.x == W - 2 &&
        ball.y >= ai.y &&
        ball.y < ai.y + ai.size
    ) {{
        ball.dx = -1;
    }}

    if (ball.x < 0) {{
        aiScore++;
        updateScore();
        resetBall();
    }}

    if (ball.x >= W) {{
        playerScore++;
        updateScore();
        resetBall();
    }}
}}

function loop() {{

    if (paused)
        return;

    physics();
    updateAI();
    render();
}}

function startGame() {{

    if (timer != null)
        return;

    timer = app.setInterval("loop()", 80);
}}

function togglePause() {{
    paused = !paused;
}}

function init() {{
    initGrid();
    render();
    updateScore();
}}

init();
"""

pdf_data = PDF_TEMPLATE
pdf_data = pdf_data.replace("###FIELDS###", " ".join(field_refs))
pdf_data = pdf_data.replace("###OBJECTS###", "\n".join(objects))
pdf_data = pdf_data.replace("###JAVASCRIPT###", javascript)
pdf_data = pdf_data.replace("###JS_LEN###", str(len(javascript)))

with open("enhanced_ping_pong.pdf", "wb") as f:
    f.write(pdf_data.encode("latin-1"))

print("Enhanced PDF game generated successfully!")
