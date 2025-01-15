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
  /Kids [
    16 0 R
  ]
  /Type /Pages
>>

%% Annots Page 1 (also used as overall fields list)
21 0 obj
[
  ###FIELD_LIST###
]
endobj

###FIELDS###

%% Page 1
16 0 obj
<<
  /Annots 21 0 R
  /Contents 3 0 R
  /CropBox [
    0.0
    0.0
    612.0
    792.0
  ]
  /MediaBox [
    0.0
    0.0
    612.0
  ]
  /Parent 2 0 R
  /Resources <<
  >>
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

// Hacky wrapper to work with a callback instead of a string
function setInterval(cb, ms) {
    evalStr = "(" + cb.toString() + ")();";
    return app.setInterval(evalStr, ms);
}

// Globals
var gridSize = 20;
var gridWidth = ###GRID_WIDTH###;
var gridHeight = ###GRID_HEIGHT###;

var snake;
var food;
var score;
var gameInterval;

function initGame() {
    resetGame();
    startGame();
}

function resetGame() {
    snake = [{x: 5, y: 5, directionX: 1, directionY: 0}];
    food = generateFood();
    score = 0;
}

function startGame() {
    gameInterval = setInterval(gameLoop, 200);
    document.addEventListener('keydown', onKeyDown);
}

function gameLoop() {
    var head = {...snake[0]};
    head.x += head.directionX;
    head.y += head.directionY;

    if (head.x < 0 || head.x >= gridWidth || head.y < 0 || head.y >= gridHeight || checkCollision(head)) {
        clearInterval(gameInterval);
        app.alert("Game Over! Your score is: " + score);
        return;
    }

    snake.unshift(head);

    if (head.x === food.x && head.y === food.y) {
        score += 10;
        food = generateFood();
    } else {
        snake.pop();
    }

    renderGame();
}

function renderGame() {
    for (var x = 0; x < gridWidth; x++) {
        for (var y = 0; y < gridHeight; y++) {
            set_pixel(x, y, 0);
        }
    }
    for (var i = 0; i < snake.length; i++) {
        set_pixel(snake[i].x, snake[i].y, 1);
    }
    set_pixel(food.x, food.y, 2);
    this.getField("T_score").value = "Score: " + score;
}

function generateFood() {
    var foodX = Math.floor(Math.random() * gridWidth);
    var foodY = Math.floor(Math.random() * gridHeight);
    return {x: foodX, y: foodY};
}

function checkCollision(head) {
    for (var i = 1; i < snake.length; i++) {
        if (head.x === snake[i].x && head.y === snake[i].y) {
            return true;
        }
    }
    return false;
}

function onKeyDown(event) {
    if (event.key === "ArrowLeft" && snake[0].directionX === 0) {
        snake[0].directionX = -1;
        snake[0].directionY = 0;
    }

    if (event.key === "ArrowRight" && snake[0].directionX === 0) {
        snake[0].directionX = 1;
        snake[0].directionY = 0;
    }

    if (event.key === "ArrowUp" && snake[0].directionY === 0) {
        snake[0].directionX = 0;
        snake[0].directionY = -1;
    }

    if (event.key === "ArrowDown" && snake[0].directionY === 0) {
        snake[0].directionX = 0;
        snake[0].directionY = 1;
    }
}

function set_pixel(x, y, state) {
    if (x < 0 || y < 0 || x >= gridWidth || y >= gridHeight) {
        return;
    }
    var field = this.getField(`P_${x}_${y}`);
    field.fillColor = state === 0 ? color.gray : state === 1 ? color.green : color.red;
}

// Zoom to fit (on FF)
app.execMenuItem("FitPage");

endstream
endobj


18 0 obj
<<
  /JS 43 0 R
  /S /JavaScript
>>
endobj


43 0 obj
<< >>
stream



endstream
endobj

trailer
<<
  /Root 1 0 R
>>

%%EOF
"""

PIXEL_OBJ = """
###IDX### obj
<<
  /FT /Btn
  /Ff 1
  /MK <<
    /BG [
      0.8
    ]
    /BC [
      0 0 0
    ]
  >>
  /Border [ 0 0 1 ]
  /P 16 0 R
  /Rect [
    ###RECT###
  ]
  /Subtype /Widget
  /T (P_###X###_###Y###)
  /Type /Annot
>>
endobj
"""

BUTTON_AP_STREAM = """
###IDX### obj
<<
  /BBox [ 0.0 0.0 ###WIDTH### ###HEIGHT### ]
  /FormType 1
  /Matrix [ 1.0 0.0 0.0 1.0 0.0 0.0]
  /Resources <<
    /Font <<
      /HeBo 10 0 R
    >>
    /ProcSet [ /PDF /Text ]
  >>
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
  /A <<
      /JS ###SCRIPT_IDX### R
      /S /JavaScript
    >>
  /AP <<
    /N ###AP_IDX### R
  >>
  /F 4
  /FT /Btn
  /Ff 65536
  /MK <<
    /BG [
      0.75
    ]
    /CA (###LABEL###)
  >>
  /P 16 0 R
  /Rect [
    ###RECT###
  ]
  /Subtype /Widget
  /T (###NAME###)
  /Type /Annot
>>
endobj
"""

TEXT_OBJ = """
###IDX### obj
<<
    /AA <<
        /K <<
            /JS ###SCRIPT_IDX### R
            /S /JavaScript
        >>
    >>
    /F 4
    /FT /Tx
    /MK <<
    >>
    /MaxLen 0
    /P 16 0 R
    /Rect [
        ###RECT###
    ]
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

# Playing field outline
for x in range(GRID_WIDTH):
    for y in range(GRID_HEIGHT):
        # Build object
        pixel = PIXEL_OBJ
        pixel = pixel.replace("###IDX###", f"{obj_idx_ctr} 0")
        c = [0, 0, 0]
        pixel = pixel.replace("###COLOR###", f"{c[0]} {c[1]} {c[2]}")
        pixel = pixel.replace("###RECT###", f"{GRID_OFF_X+x*PX_SIZE} {GRID_OFF_Y+y*PX_SIZE} {GRID_OFF_X+x*PX_SIZE+PX_SIZE} {GRID_OFF_Y+y*PX_SIZE+PX_SIZE}")
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
    button = button.replace("###NAME###", name if name else f"B_{obj_idx_ctr}")
    button = button.replace("###RECT###", f"{x} {y} {x + width} {y + height}")
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
    text = text.replace("###RECT###", f"{x} {y} {x + width} + {y + height}")
    add_field(text)

add_button("<", "B_left", GRID_OFF_X + 0, GRID_OFF_Y - 70, 50, 50, "move_left();")
add_button(">", "B_right", GRID_OFF_X + 60, GRID_OFF_Y - 70, 50, 50, "move_right();")
add_button("\\\\/", "B_down", GRID_OFF_X + 30, GRID_OFF_Y - 130, 50, 50, "lower_piece();")
add_button("SPIN", "B_rotate", GRID_OFF_X + 140, GRID_OFF_Y - 70, 50, 50, "rotate_piece();")

add_button("Start game", "B_start", GRID_OFF_X + (GRID_WIDTH*PX_SIZE)/2-50, GRID_OFF_Y + (GRID_HEIGHT*PX_SIZE)/2-50, 100, 100, "initGame();")

add_text("Type here for keyboard controls (Arrow Keys)", "T_input", GRID_OFF_X + 0, GRID_OFF_Y - 200, GRID_WIDTH*PX_SIZE, 50, "handle_input(event);")

add_text("Score: 0", "T_score", GRID_OFF_X + GRID_WIDTH*PX_SIZE+10, GRID_OFF_Y + GRID_HEIGHT*PX_SIZE-50, 100, 50, "")

filled_pdf = PDF_FILE_TEMPLATE.replace("###FIELDS###", fields_text)
filled_pdf = filled_pdf.replace("###FIELD_LIST###", " ".join([f"{i} 0 R" for i in field_indexes]))
filled_pdf = filled_pdf.replace("###GRID_WIDTH###", f"{GRID_WIDTH}")
filled_pdf = filled_pdf.replace("###GRID_HEIGHT###", f"{GRID_HEIGHT}")

with open("snake_game.pdf", "w") as pdffile:
    pdffile.write(filled_pdf)
