from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_pdf_with_snake_game(file_name):
    c = canvas.Canvas(snake_game.pdf, pagesize=letter)
    
    #Title amd instructions
    c.setfont("Helvetica", 14)
    c.drawString(100, 750, "Snake Game")
    c.drawString(100, 730, "Press the 'Start Game' button to begin the game.")
    c.drawString(100, 710, "Use arrow keys to control the snake.")
    
    #Creating a canvas for the game
    c.setFont("Helvetica", 12)
    c.drawString(100, 680, "Game Canvas")
    c.rect(100, 100, 300, 300)# Create game canvas
    
    #Add buttons
    c.linkURL('javascript:startGame()', (100, 370, 200, 400), relative=1)
    
    #Add the Snake Game JavaScript
    snake_game_js = """
    var canvas = this.getField('gameCanvas');
    var ctx = canvas.getContext('2d');
    var snake, food, score;
    var gameInterval;
    var gridSize = 20;
    
    function initGame() {
        canvas = this.getField('gameCanvas');
        ctx = canvas.getContext('2d');
        resetGame();
        startGame();
    }
    
    function resetGame() {
        snake = [{x: 5 * gridSize, y: 5 * gridSize}];
        food = generateFood();
        score = 0;
    }
    
    function startGame() {
        var head = {...snake[0]};
        head.x += head.directionX * gridSize;
        head.y += head.directionY * gridSize;
        
        if (head.x <0 || head.x >= canvas.width || head.y < 0 || head.y >= canvas.height || checkCollision(head)){
            clearInterval(gameInterval);
            app.alert("Game Over! Your score is: " + score);
            return;
        }
        
        snake.unshift(head);
        
        if (head.x === food.x && head.y === food.y){
            score += 10;
            food = generateFood();
        } else {
            snake.pop();
        }
        
        renderGame();
    }
    
    function renderGame() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        ctx.fillStyle = "green";
        for (var i = 0; i < snake.length; i++){
            ctx.fillRect(snake[i].x, snake[i].y, gridSize, gridSize);
        }
        ctx.fillStyle = "red";
        ctx.fillRect(food.x, food.y, gridSize, gridSize);
        
        ctx.fillStyle = "black";
        ctx.fillText("Score: " + score, 10, 10);
        
    }
    
    function generateFood() {
        var foodX = Math.floor(Math.random() * canvas.width / gridSize) * gridSize;
        var foodY = Math.floor(Math.random() * canvas.height / gridSize) * gridSize;
        return {x: foodX, y: foodY};
    }
    
    function checkCollision(head) {
        for (var i = 1; i < snake.length; i++){
            if (head.x === snake[i].x && head.y === snake[i].y){
                return true;
            }
        }
        return false;
    }
    
    function onKeyDown(event) {
        if (event.key === "ArrowLeft" && snake[0].directionX === 0){
            snake[0].directionX = -1;
            snake[0].directionY = 0;
        }
    
        if (event.key === "ArrowRight" && snake[0].directionX === 0){
            snake[0].directionX = 1;
            snake[0].directionY = 0;
        }
    
        if (event.key === "ArrowUp" && snake[0].directionY === 0){
            snake[0].directionX = 0;
            snake[0].directionY = -1;
        }
    }
    """

    # Embed the JavaScript in the PDF
    c.addJavaScript(snake_game_js)

    # Save the PDF file
    c.save()

# Call the function to create the PDF
create_pdf_with_snake_game("snake_game.pdf")
