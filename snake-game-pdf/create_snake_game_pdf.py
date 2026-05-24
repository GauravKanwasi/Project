"""
Enhanced PDF Snake Game Generator
---------------------------------
Creates an interactive Snake game inside a PDF using Acrobat JavaScript.

Requirements:
- Python 3.x
- Adobe Acrobat Reader (browser PDF viewers usually block JavaScript)
"""

GRID_W = 12
GRID_H = 12
CELL = 24

PDF_TEMPLATE = r"""%PDF-1.7

1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
/OpenAction 5 0 R
/AcroForm <<
/Fields [FIELDS]
>>
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
/MediaBox [0 0 700 700]
/Annots [ANNOTS]
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
<< /Length JS_LEN >>
stream

var gridW = """ + str(GRID_W) + r""";
var gridH = """ + str(GRID_H) + r""";

var snake;
var food;
var dx;
var dy;
var score;
var timer;

function startGame() {
    snake = [{x:2,y:2}];
    dx = 1;
    dy = 0;
    score = 0;

    spawnFood();

    if (timer) {
        app.clearInterval(timer);
    }

    timer = app.setInterval("tick()", 250);

    render();
}

function spawnFood() {
    food = {
        x: Math.floor(Math.random() * gridW),
        y: Math.floor(Math.random() * gridH)
    };
}

function tick() {

    var head = {
        x: snake[0].x + dx,
        y: snake[0].y + dy
    };

    // Wall collision
    if (
        head.x < 0 ||
        head.y < 0 ||
        head.x >= gridW ||
        head.y >= gridH
    ) {
        gameOver();
        return;
    }

    // Self collision
    for (var i = 0; i < snake.length; i++) {
        if (
            snake[i].x == head.x &&
            snake[i].y == head.y
        ) {
            gameOver();
            return;
        }
    }

    snake.unshift(head);

    // Eat food
    if (
        head.x == food.x &&
        head.y == food.y
    ) {
        score += 10;
        spawnFood();
    } else {
        snake.pop();
    }

    render();
}

function gameOver() {
    app.clearInterval(timer);
    app.alert("Game Over! Score: " + score);
}

function render() {

    // Clear board
    for (var y = 0; y < gridH; y++) {
        for (var x = 0; x < gridW; x++) {

            var field = this.getField(
                "P_" + x + "_" + y
            );

            field.fillColor = color.gray;
        }
    }

    // Draw snake
    for (var i = 0; i < snake.length; i++) {

        var s = snake[i];

        this.getField(
            "P_" + s.x + "_" + s.y
        ).fillColor = color.green;
    }

    // Draw food
    this.getField(
        "P_" + food.x + "_" + food.y
    ).fillColor = color.red;

    // Update score
    this.getField("score").value =
        "Score: " + score;
}

function left() {
    if (dx != 1) {
        dx = -1;
        dy = 0;
    }
}

function right() {
    if (dx != -1) {
        dx = 1;
        dy = 0;
    }
}

function up() {
    if (dy != -1) {
        dx = 0;
        dy = 1;
    }
}

function down() {
    if (dy != 1) {
        dx = 0;
        dy = -1;
    }
}

app.execMenuItem("FitPage");

endstream
endobj

OBJECTS

trailer
<<
/Root 1 0 R
>>
%%EOF
"""

objects = []
annots = []
fields = []

obj_id = 10


def add_object(content):
    global obj_id

    objects.append(
        f"{obj_id} 0 obj\n{content}\nendobj"
    )

    current = obj_id
    obj_id += 1

    return current


def add_button(name, label, x, y, w, h, js):

    js_stream = add_object(
        f"<< /Length {len(js)} >>\n"
        f"stream\n{js}\nendstream"
    )

    button = f"""
<<
/Type /Annot
/Subtype /Widget
/FT /Btn
/T ({name})
/Rect [{x} {y} {x+w} {y+h}]
/A <<
/S /JavaScript
/JS {js_stream} 0 R
>>
/MK <<
/CA ({label})
>>
>>
"""

    oid = add_object(button)

    annots.append(f"{oid} 0 R")
    fields.append(f"{oid} 0 R")


def add_text(name, value, x, y, w, h):

    text = f"""
<<
/Type /Annot
/Subtype /Widget
/FT /Tx
/T ({name})
/Rect [{x} {y} {x+w} {y+h}]
/V ({value})
>>
"""

    oid = add_object(text)

    annots.append(f"{oid} 0 R")
    fields.append(f"{oid} 0 R")


def add_pixel(x, y):

    px = 80 + x * CELL
    py = 120 + y * CELL

    pixel = f"""
<<
/Type /Annot
/Subtype /Widget
/FT /Btn
/Ff 1
/T (P_{x}_{y})
/Rect [{px} {py} {px+CELL} {py+CELL}]
/MK <<
/BG [0.8]
>>
>>
"""

    oid = add_object(pixel)

    annots.append(f"{oid} 0 R")
    fields.append(f"{oid} 0 R")


# Create game board
for y in range(GRID_H):
    for x in range(GRID_W):
        add_pixel(x, y)


# Controls
add_button(
    "start",
    "START",
    420,
    500,
    120,
    40,
    "startGame();"
)

add_button(
    "left",
    "LEFT",
    420,
    420,
    80,
    40,
    "left();"
)

add_button(
    "right",
    "RIGHT",
    510,
    420,
    80,
    40,
    "right();"
)

add_button(
    "up",
    "UP",
    465,
    470,
    80,
    40,
    "up();"
)

add_button(
    "down",
    "DOWN",
    465,
    370,
    80,
    40,
    "down();"
)


# Score field
add_text(
    "score",
    "Score: 0",
    420,
    320,
    150,
    30
)


# Build final PDF
final_pdf = PDF_TEMPLATE

final_pdf = final_pdf.replace(
    "ANNOTS",
    " ".join(annots)
)

final_pdf = final_pdf.replace(
    "FIELDS",
    " ".join(fields)
)

final_pdf = final_pdf.replace(
    "OBJECTS",
    "\n\n".join(objects)
)

final_pdf = final_pdf.replace(
    "JS_LEN",
    "5000"
)


# Save PDF
with open("snake_game.pdf", "w", encoding="latin1") as f:
    f.write(final_pdf)

print("snake_game.pdf created successfully!")
