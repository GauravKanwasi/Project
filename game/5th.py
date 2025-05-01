import tkinter as tk

# Functions to handle drawing and controls
def start_drawing(event):
    global prev_x, prev_y
    prev_x = event.x
    prev_y = event.y
    # Draw a small dot when clicking
    canvas.create_oval(prev_x - line_width/2, prev_y - line_width/2,
                       prev_x + line_width/2, prev_y + line_width/2,
                       fill=current_color, outline=current_color)

def draw(event):
    global prev_x, prev_y
    if prev_x is not None and prev_y is not None:
        canvas.create_line(prev_x, prev_y, event.x, event.y,
                           fill=current_color, width=line_width)
        prev_x = event.x
        prev_y = event.y

def clear_canvas():
    canvas.delete("all")

def set_color(color):
    global current_color
    current_color = color

# Create the main window
root = tk.Tk()
root.title("Basic Drawing App")

# Create a frame for buttons at the bottom
button_frame = tk.Frame(root)
button_frame.pack(side="bottom")

# Create the canvas
canvas = tk.Canvas(root, width=800, height=600, bg="white")
canvas.pack(expand=True, fill="both")

# Initialize global variables
current_color = "black"
line_width = 2
prev_x = None
prev_y = None

# Create the clear button
clear_button = tk.Button(button_frame, text="Clear", command=clear_canvas)
clear_button.pack(side="left")

# Create color buttons
colors = ["black", "red", "green", "blue", "white"]
for color in colors:
    button = tk.Button(button_frame, text=color,
                       command=lambda c=color: set_color(c))
    button.pack(side="left")

# Bind mouse events to the canvas
canvas.bind("<Button-1>", start_drawing)
canvas.bind("<B1-Motion>", draw)

# Start the application
root.mainloop()
