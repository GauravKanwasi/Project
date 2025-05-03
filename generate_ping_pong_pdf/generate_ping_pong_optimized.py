PDF_FILE_TEMPLATE = """
%PDF-1.6

% Root
1 0 obj
<<
  /AcroForm <<
    /Fields [ ###FIELD_LIST### ]
  >>
  /Pages 2 0 R
  /OpenAction 17 0 R
  /Type /Catalog
>>
endobj

2 0 obj
<<
  /Count 1
  /Kids [ 16 0 R ]
  /Type /Pages
>>

% Annots Page 1
21 0 obj
[ ###FIELD_LIST### ]
endobj

###FIELDS###

% Page 1
16 0 obj
<<
  /Annots 21 0 R
  /Contents 3 0 R
  /CropBox [ 0.0 0.0 612.0 792.0 ]
  /MediaBox [ 0.0 0.0 612.0 792.0 ]
  /Parent 2 0 R
  /Resources << >>
  /Rotate 0
  /Type /Page
>>
endobj

3 0 obj
<< >>
stream
endstream
endobj

17 0 obj
<<
  /JS 42 0 R
  /S /JavaScript
>>
endobj

42 0 obj
<< >>
stream
// Safer setInterval
function setInterval(cb, ms) {
    try {
        return app.setInterval("try { (" + cb.toString() + ")(); } catch(e) { /* Silent error */ }", ms);
    } catch (e) {
        app.alert("Failed to set interval: " + e);
        return null;
    }
}

// Game variables
var gridSize = 20;
var gridWidth = ###GRID_WIDTH###;
var gridHeight = ###GRID_HEIGHT###;
var playerPaddle = { y: 8, height: 3 };
var aiPaddle = { y: 8, height: 3 };
var ball = { x: 10, y: 10, dx: 1, dy: 1 };
var playerScore = 0;
var aiScore = 0;
var gameInterval = null;
var isPaused = false;
var gridFields = [];

// Cache grid field references
for (var x = 0; x < gridWidth; x++) {
    gridFields[x] = [];
    for (var y = 0; y < gridHeight; y++) {
        gridFields[x][y] = this.getField(`P_${x}_${y}`);
    }
}

// Initialize game
initGame();

function initGame() {
    resetGame();
    renderFullGrid();
    this.getField("B_start").focus();
}

function resetGame() {
    playerPaddle.y = 8;
    aiPaddle.y = 8;
    ball.x = 10;
    ball.y = 10;
    ball.dx = 1;
    ball.dy = 1;
    playerScore = 0;
    aiScore = 0;
    isPaused = false;
    if (gameInterval) {
        app.clearInterval(gameInterval);
        gameInterval = null;
    }
    this.getField("T_player_score").value = "Player: 0";
    this.getField("T_ai_score").value = "AI: 0";
    this.getField("B_restart").display = display.hidden;
    this.getField("B_pause").display = display.hidden;
    this.getField("B_resume").display = display.hidden;
    this.getField("B_start").display = display.visible;
}

function startGame() {
    if (!gameInterval) {
        gameInterval = setInterval(gameLoop, 100); // 100ms for smoothness
    }
    isPaused = false;
    this.getField("B_start").display = display.hidden;
    this.getField("B_pause").display = display.visible;
}

function pauseGame() {
    isPaused = !isPaused;
    this.getField("B_pause").display = isPaused ? display.hidden : display.visible;
    this.getField("B_resume").display = isPaused ? display.visible : display.hidden;
}

function gameLoop() {
    if (isPaused) return;
    try {
        // Move ball
        ball.x += ball.dx;
        ball.y += ball.dy;

        // Wall collisions
        if (ball.y <= 0 || ball.y >= gridHeight - 1) {
            ball.dy = -ball.dy;
            ball.y = Math.max(0, Math.min(gridHeight - 1, ball.y));
        }

        // Paddle collisions
        if (ball.x <= 1 && ball.y >= playerPaddle.y && ball.y < playerPaddle.y + playerPaddle.height) {
            ball.dx = 1;
            ball.x = 1;
        } else if (ball.x >= gridWidth - 2 && ball.y >= aiPaddle.y && ball.y < aiPaddle.y + aiPaddle.height) {
            ball.dx = -1;
            ball.x = gridWidth - 2;
        }

        // Scoring
        if (ball.x < 0) {
            aiScore++;
            resetBall();
            this.getField("T_ai_score").value = "AI: " + aiScore;
        } else if (ball.x >= gridWidth) {
            playerScore++;
            resetBall();
            this.getField("T_player_score").value = "Player: " + playerScore;
        }

        // AI movement
        var targetY = ball.y - 1;
        aiPaddle.y += (targetY - aiPaddle.y) * 0.2; // Smooth tracking
        aiPaddle.y = Math.max(0, Math.min(gridHeight - aiPaddle.height, Math.round(aiPaddle.y)));

        // Render updates
        renderChanges();
    } catch (e) {
        /* Silent error */
    }
}

function resetBall() {
    ball.x = 10;
    ball.y = 10;
    ball.dx = (Math.random() > 0.5 ? 1 : -1);
    ball.dy = (Math.random() > 0.5 ? 1 : -1);
}

function renderFullGrid() {
    for (var x = 0; x < gridWidth; x++) {
        for (var y = 0; y < gridHeight; y++) {
            set_pixel(x, y, 0);
        }
    }
    renderPaddles();
    renderBall();
}

function renderChanges() {
    // Clear previous ball position
    var prevBallX = Math.round(ball.x - ball.dx);
    var prevBallY = Math.round(ball.y - ball.dy);
    set_pixel(prevBallX, prevBallY, 0);

    // Update ball and paddles
    renderBall();
    renderPaddles();
}

function renderPaddles() {
    // Clear paddle columns
    for (var y = 0; y < gridHeight; y++) {
        set_pixel(0, y, 0);
        set_pixel(gridWidth - 1, y, 0);
    }
    // Draw player paddle
    for (var i = 0; i < playerPaddle.height; i++) {
        var y = Math.round(playerPaddle.y) + i;
        if (y >= 0 && y < gridHeight) set_pixel(0, y, 1);
    }
    // Draw AI paddle
    for (var i = 0; i < aiPaddle.height; i++) {
        var y = Math.round(aiPaddle.y) + i;
        if (y >= 0 && y < gridHeight) set_pixel(gridWidth - 1, y, 1);
    }
}

function renderBall() {
    var ballX = Math.round(ball.x);
    var ballY = Math.round(ball.y);
    if (ballX >= 0 && ballX < gridWidth && ballY >= 0 && ballY < gridHeight) {
        set_pixel(ballX, ballY, 2);
    }
}

function onKeyDown(event) {
    if (event.key === "ArrowUp") {
        playerPaddle.y = Math.max(0, playerPaddle.y - 1);
        renderPaddles();
    } else if (event.key === "ArrowDown") {
        playerPaddle.y = Math.min(gridHeight - playerPaddle.height, playerPaddle.y + 1);
        renderPaddles();
    }
}

function set_pixel(x, y, state) {
    if (x < 0 || y < 0 || x >= gridWidth || y >= gridHeight) return;
    var field = gridFields[x][y];
    field.fillColor = state === 0 ? color.white : state === 1 ? color.green : color.red;
}

// Fit page on open
app.execMenuItem("FitPage");
endstream
endobj

trailer
<< /Root 1 0 R >>
%%EOF
"""

PIXEL_OBJ = """
###IDX### obj
<<
  /FT /Btn
  /Ff 1
  /MK << /BG [1.0] /BC [0 0 0] >>
  /Border [0 0 1]
  /P 16 0 R
  /Rect [ ###RECT### ]
  /Subtype /Widget
  /T (P_###X###_###Y###)
  /Type /Annot
>>
endobj
"""

BUTTON_AP_STREAM = """
###IDX### obj
<<
  /BBox [0.0 0.0 ###WIDTH### ###HEIGHT###]
  /FormType 1
  /Matrix [1.0 0.0 0.0 1.0 0.0 0.0]
  /Resources << /Font << /HeBo 10 0 R >> /ProcSet [/PDF /Text] >>
  /Subtype /Form
  /Type /XObject
>>
stream
q
0.75 g
0 0 ###WIDTH### ###HEIGHT### re
f
Q
q
1 1 ###WIDTH### ###HEIGHT### re
W
n
BT
/HeBo 12 Tf
0 g
10 8 Td
(###TEXT###) Tj
ET
Q
endstream
endobj
"""

BUTTON_OBJ = """
###IDX### obj
<<
  /A << /JS ###SCRIPT_IDX### R /S /JavaScript >>
  /AP << /N ###AP_IDX### R >>
  /F 4
  /FT /Btn
  /Ff 65536
  /MK << /BG [0.75] /CA (###LABEL###) >>
  /P 16 0 R
  /Rect [ ###RECT### ]
  /Subtype /Widget
  /T (###NAME###)
  /Type /Annot
>>
endobj
"""

TEXT_OBJ = """
###IDX### obj
<<
    /AA << /K << /JS ###SCRIPT_IDX### R /S /JavaScript >> >>
    /F 4
    /FT /Tx
    /MK << >>
    /MaxLen 0
    /P 16 0 R
    /Rect [ ###RECT### ]
    /Subtype /Widget
    /T (###NAME###)
    /V (###LABEL###)
    /Type /Annot
>>
endobj
"""

STREAM_OBJ = """
###IDX### obj
<< >>
stream
###CONTENT###
endstream
endobj
"""

# Configuration
PX_SIZE = 20
GRID_WIDTH = 20
GRID_HEIGHT = 20
GRID_OFF_X = 100
GRID_OFF_Y = 150

fields_text = ""
field_indexes = []
obj_idx_ctr = 50

def add_field(field):
    global fields_text, field_indexes, obj_idx_ctr
    fields_text += field
    field_indexes.append(obj_idx_ctr)
    obj_idx_ctr += 1

# Grid pixels
for x in range(GRID_WIDTH):
    for y in range(GRID_HEIGHT):
        pixel = PIXEL_OBJ
        pixel = pixel.replace("###IDX###", f"{obj_idx_ctr} 0")
        pixel = pixel.replace("###RECT###", f"{GRID_OFF_X + x*PX_SIZE} {GRID_OFF_Y + y*PX_SIZE} {GRID_OFF_X + x*PX_SIZE + PX_SIZE} {GRID_OFF_Y + y*PX_SIZE + PX_SIZE}")
        pixel = pixel.replace("###X###", f"{x}")
        pixel = pixel.replace("###Y###", f"{y}")
        add_field(pixel)

def add_button(label, name, x, y, width, height, js):
    script = STREAM_OBJ
    script = script.replace("###IDX###", f"{obj_idx_ctr} 0")
    script = script.replace("###CONTENT###", js)
    add_field(script)

    ap_stream = BUTTON_AP_STREAM
    ap_stream = ap_stream.replace("###IDX###", f"{obj_idx_ctr} 0")
    ap_stream = ap_stream.replace("###TEXT###", label)
    ap_stream = ap_stream.replace("###WIDTH###", f"{width}")
    ap_stream = ap_stream.replace("###HEIGHT###", f"{height}")
    add_field(ap_stream)

    button = BUTTON_OBJ
    button = button.replace("###IDX###", f"{obj_idx_ctr} 0")
    button = button.replace("###SCRIPT_IDX###", f"{obj_idx_ctr-2} 0")
    button = button.replace("###AP_IDX###", f"{obj_idx_ctr-1} 0")
    button = button.replace("###NAME###", name)
    button = button.replace("###RECT###", f"{x} {y} {x + width} {y + height}")
    button = button.replace("###LABEL###", label)
    add_field(button)

def add_text(label, name, x, y, width, height, js):
    script = STREAM_OBJ
    script = script.replace("###IDX###", f"{obj_idx_ctr} 0")
    script = script.replace("###CONTENT###", js)
    add_field(script)

    text = TEXT_OBJ
    text = text.replace("###IDX###", f"{obj_idx_ctr} 0")
    text = text.replace("###SCRIPT_IDX###", f"{obj_idx_ctr-1} 0")
    text = text.replace("###LABEL###", label)
    text = text.replace("###NAME###", name)
    text = text.replace("###RECT###", f"{x} {y} {x + width} {y + height}")
    add_field(text)

# Control buttons
add_button("Up", "B_up", GRID_OFF_X, GRID_OFF_Y - 60, 50, 50, "playerPaddle.y = Math.max(0, playerPaddle.y - 1); renderPaddles();")
add_button("Down", "B_down", GRID_OFF_X + 60, GRID_OFF_Y - 60, 50, 50, "playerPaddle.y = Math.min(gridHeight - playerPaddle.height, playerPaddle.y + 1); renderPaddles();")
add_button("Start", "B_start", GRID_OFF_X + (GRID_WIDTH*PX_SIZE - 100)/2, GRID_OFF_Y + (GRID_HEIGHT*PX_SIZE - 100)/2, 100, 50, "startGame();")
add_button("Pause", "B_pause", GRID_OFF_X + GRID_WIDTH*PX_SIZE + 10, GRID_OFF_Y + GRID_HEIGHT*PX_SIZE - 110, 100, 50, "pauseGame();")
add_button("Resume", "B_resume", GRID_OFF_X + GRID_WIDTH*PX_SIZE + 10, GRID_OFF_Y + GRID_HEIGHT*PX_SIZE - 110, 100, 50, "pauseGame();")
add_button("Restart", "B_restart", GRID_OFF_X + (GRID_WIDTH*PX_SIZE - 100)/2, GRID_OFF_Y + (GRID_HEIGHT*PX_SIZE - 100)/2, 100, 50, "initGame(); startGame(); this.getField('B_restart').display = display.hidden; this.getField('B_pause').display = display.visible;")

# Text fields
add_text("Use arrow keys or buttons to move paddle", "T_input", GRID_OFF_X, GRID_OFF_Y - 120, GRID_WIDTH*PX_SIZE, 50, "onKeyDown(event);")
add_text("Player: 0", "T_player_score", GRID_OFF_X + GRID_WIDTH*PX_SIZE + 10, GRID_OFF_Y + GRID_HEIGHT*PX_SIZE - 50, 100, 50, "")
add_text("AI: 0", "T_ai_score", GRID_OFF_X + GRID_WIDTH*PX_SIZE + 10, GRID_OFF_Y + GRID_HEIGHT*PX_SIZE - 110, 100, 50, "")

# Generate PDF
filled_pdf = PDF_FILE_TEMPLATE.replace("###FIELDS###", fields_text)
filled_pdf = filled_pdf.replace("###FIELD_LIST###", " ".join([f"{i} 0 R" for i in field_indexes]))
filled_pdf = filled_pdf.replace("###GRID_WIDTH###", f"{GRID_WIDTH}")
filled_pdf = filled_pdf.replace("###GRID_HEIGHT###", f"{GRID_HEIGHT}")

with open("ping_pong_game_optimized.pdf", "w") as pdffile:
    pdffile.write(filled_pdf)
