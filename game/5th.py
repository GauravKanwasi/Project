import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
import os
import PIL.Image, PIL.ImageGrab
from PIL import ImageTk
import io

class EnhancedDrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Drawing App")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Set up variables
        self.current_color = "#000000"  # Black
        self.line_width = 2
        self.prev_x = None
        self.prev_y = None
        self.drawing_mode = "pen"  # Default drawing mode
        self.history = []  # For undo functionality
        self.redo_stack = []  # For redo functionality
        self.fill_var = tk.BooleanVar(value=False)  # Fill option for shapes
        self.brush_shape = tk.StringVar(value="round")  # Brush shape for pen/eraser
        
        # Create UI components
        self.create_widgets()
        self.setup_bindings()
        
        # Set initial mode
        self.set_drawing_mode("pen")
        
        # Set up status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Initialize canvas state
        self.save_state()
    
    def create_widgets(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Toolbar
        self.toolbar = ttk.Frame(self.main_frame, relief=tk.RAISED, borderwidth=1)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # Tool buttons
        tools = [
            ("Pen", "pen", "Draw with a pen"),
            ("Line", "line", "Draw a straight line"),
            ("Rectangle", "rectangle", "Draw a rectangle"),
            ("Oval", "oval", "Draw an oval"),
            ("Eraser", "eraser", "Erase part of the drawing"),
            ("Text", "text", "Add text to the drawing")
        ]
        self.tool_buttons = {}
        for text, mode, tooltip in tools:
            btn = ttk.Button(self.toolbar, text=text, command=lambda m=mode: self.set_drawing_mode(m))
            btn.pack(side=tk.LEFT, padx=2, pady=2)
            self.tool_buttons[mode] = btn
            self.create_tooltip(btn, tooltip)
        
        # Size slider
        ttk.Label(self.toolbar, text="Size:").pack(side=tk.LEFT, padx=(10, 0))
        self.size_slider = ttk.Scale(self.toolbar, from_=1, to=50, orient=tk.HORIZONTAL, 
                                    command=self.change_width, value=self.line_width)
        self.size_slider.pack(side=tk.LEFT, padx=5)
        
        # Brush shape selector
        ttk.Label(self.toolbar, text="Brush:").pack(side=tk.LEFT, padx=(10, 0))
        self.brush_combo = ttk.Combobox(self.toolbar, textvariable=self.brush_shape, 
                                       values=["round", "square"], width=7)
        self.brush_combo.pack(side=tk.LEFT, padx=5)
        self.create_tooltip(self.brush_combo, "Select brush shape")
        
        # Color picker
        self.color_button = ttk.Button(self.toolbar, text="Color", command=self.choose_color)
        self.color_button.pack(side=tk.LEFT, padx=5)
        
        # Color preview
        self.color_preview = tk.Canvas(self.toolbar, width=30, height=20, bg=self.current_color)
        self.color_preview.pack(side=tk.LEFT, padx=5)
        
        # Fill checkbox
        self.fill_check = ttk.Checkbutton(self.toolbar, text="Fill Shape", variable=self.fill_var)
        self.fill_check.pack(side=tk.LEFT, padx=5)
        self.create_tooltip(self.fill_check, "Fill shapes with the selected color")
        
        # Predefined colors
        self.color_frame = ttk.Frame(self.toolbar)
        self.color_frame.pack(side=tk.LEFT, padx=10)
        colors = ["#000000", "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF", "#FFFFFF"]
        for color in colors:
            btn = tk.Button(self.color_frame, bg=color, width=2, height=1,
                          command=lambda c=color: self.set_color(c))
            btn.pack(side=tk.LEFT, padx=1)
        
        # Edit buttons
        self.edit_frame = ttk.Frame(self.toolbar)
        self.edit_frame.pack(side=tk.LEFT, padx=20)
        ttk.Button(self.edit_frame, text="Undo", command=self.undo).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.edit_frame, text="Redo", command=self.redo).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.edit_frame, text="Clear", command=self.clear_canvas).pack(side=tk.LEFT, padx=2)
        
        # File buttons
        self.file_frame = ttk.Frame(self.toolbar)
        self.file_frame.pack(side=tk.RIGHT, padx=5)
        ttk.Button(self.file_frame, text="Save", command=self.save_drawing).pack(side=tk.RIGHT, padx=2)
        ttk.Button(self.file_frame, text="Load", command=self.load_drawing).pack(side=tk.RIGHT, padx=2)
        
        # Canvas and scrollbars
        self.canvas_frame = ttk.Frame(self.main_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.v_scrollbar = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL)
        self.h_scrollbar = ttk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL)
        self.canvas = tk.Canvas(self.canvas_frame, width=800, height=600, bg="white",
                               xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)
        self.v_scrollbar.config(command=self.canvas.yview)
        self.h_scrollbar.config(command=self.canvas.xview)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        self.canvas.config(scrollregion=(0, 0, 1500, 1000))
        
        # Context menu
        self.context_menu = tk.Menu(self.canvas, tearoff=0)
        self.context_menu.add_command(label="Undo", command=self.undo)
        self.context_menu.add_command(label="Redo", command=self.redo)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Clear", command=self.clear_canvas)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Select Color", command=self.choose_color)
    
    def setup_bindings(self):
        self.canvas.bind("<Button-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.end_drawing)
        self.canvas.bind("<Button-3>", self.show_context_menu)
        self.root.bind("<Control-z>", lambda event: self.undo())
        self.root.bind("<Control-y>", lambda event: self.redo())
        self.root.bind("<Control-s>", lambda event: self.save_drawing())
        self.root.bind("<Control-o>", lambda event: self.load_drawing())
        self.root.bind("<Escape>", lambda event: self.cancel_operation())
    
    def start_drawing(self, event):
        self.prev_x = self.canvas.canvasx(event.x)
        self.prev_y = self.canvas.canvasy(event.y)
        
        if self.drawing_mode == "line":
            self.temp_item = self.canvas.create_line(
                self.prev_x, self.prev_y, self.prev_x, self.prev_y,
                fill=self.current_color, width=self.line_width
            )
        elif self.drawing_mode == "rectangle":
            fill_color = self.current_color if self.fill_var.get() else ""
            self.temp_item = self.canvas.create_rectangle(
                self.prev_x, self.prev_y, self.prev_x, self.prev_y,
                outline=self.current_color, fill=fill_color, width=self.line_width
            )
        elif self.drawing_mode == "oval":
            fill_color = self.current_color if self.fill_var.get() else ""
            self.temp_item = self.canvas.create_oval(
                self.prev_x, self.prev_y, self.prev_x, self.prev_y,
                outline=self.current_color, fill=fill_color, width=self.line_width
            )
        elif self.drawing_mode == "pen":
            if self.brush_shape.get() == "round":
                self.canvas.create_oval(
                    self.prev_x - self.line_width/2, self.prev_y - self.line_width/2,
                    self.prev_x + self.line_width/2, self.prev_y + self.line_width/2,
                    fill=self.current_color, outline=self.current_color
                )
            else:  # square
                self.canvas.create_rectangle(
                    self.prev_x - self.line_width/2, self.prev_y - self.line_width/2,
                    self.prev_x + self.line_width/2, self.prev_y + self.line_width/2,
                    fill=self.current_color, outline=self.current_color
                )
        elif self.drawing_mode == "eraser":
            if self.brush_shape.get() == "round":
                self.canvas.create_oval(
                    self.prev_x - self.line_width, self.prev_y - self.line_width,
                    self.prev_x + self.line_width, self.prev_y + self.line_width,
                    fill="white", outline="white"
                )
            else:  # square
                self.canvas.create_rectangle(
                    self.prev_x - self.line_width, self.prev_y - self.line_width,
                    self.prev_x + self.line_width, self.prev_y + self.line_width,
                    fill="white", outline="white"
                )
        elif self.drawing_mode == "text":
            self.add_text(event)
    
    def draw(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        if self.drawing_mode == "pen":
            if self.prev_x is not None and self.prev_y is not None:
                cap = tk.ROUND if self.brush_shape.get() == "round" else tk.PROJECTING
                self.canvas.create_line(
                    self.prev_x, self.prev_y, x, y,
                    fill=self.current_color, width=self.line_width,
                    capstyle=cap, smooth=True
                )
        elif self.drawing_mode == "eraser":
            if self.prev_x is not None and self.prev_y is not None:
                cap = tk.ROUND if self.brush_shape.get() == "round" else tk.PROJECTING
                self.canvas.create_line(
                    self.prev_x, self.prev_y, x, y,
                    fill="white", width=self.line_width*2,
                    capstyle=cap, smooth=True
                )
        elif self.drawing_mode == "line":
            self.canvas.coords(self.temp_item, self.prev_x, self.prev_y, x, y)
        elif self.drawing_mode == "rectangle":
            self.canvas.coords(self.temp_item, self.prev_x, self.prev_y, x, y)
        elif self.drawing_mode == "oval":
            self.canvas.coords(self.temp_item, self.prev_x, self.prev_y, x, y)
        
        self.prev_x = x
        self.prev_y = y
    
    def end_drawing(self, event):
        if self.drawing_mode in ["line", "rectangle", "oval"]:
            self.temp_item = None
        self.save_state()
    
    def add_text(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        text_dialog = tk.Toplevel(self.root)
        text_dialog.title("Add Text")
        text_dialog.geometry("300x150")
        text_dialog.resizable(False, False)
        ttk.Label(text_dialog, text="Enter text:").pack(pady=5)
        text_entry = ttk.Entry(text_dialog, width=30)
        text_entry.pack(pady=5)
        text_entry.focus_set()
        font_sizes = [8, 10, 12, 14, 16, 18, 20, 24, 28, 32, 36, 48]
        font_var = tk.IntVar(value=12)
        ttk.Label(text_dialog, text="Font size:").pack(pady=5)
        font_combo = ttk.Combobox(text_dialog, values=font_sizes, width=5, textvariable=font_var)
        font_combo.pack(pady=5)
        
        def add_text_to_canvas():
            text = text_entry.get()
            if text:
                font_size = font_var.get()
                self.canvas.create_text(
                    x, y, text=text, fill=self.current_color,
                    font=("Arial", font_size), anchor=tk.NW
                )
                self.save_state()
            text_dialog.destroy()
        
        ttk.Button(text_dialog, text="Add", command=add_text_to_canvas).pack(pady=10)
        text_dialog.transient(self.root)
        text_dialog.update_idletasks()
        width = text_dialog.winfo_width()
        height = text_dialog.winfo_height()
        x_pos = (self.root.winfo_width() // 2) - (width // 2) + self.root.winfo_x()
        y_pos = (self.root.winfo_height() // 2) - (height // 2) + self.root.winfo_y()
        text_dialog.geometry(f"+{x_pos}+{y_pos}")
        text_dialog.grab_set()
    
    def set_drawing_mode(self, mode):
        self.drawing_mode = mode
        for tool, button in self.tool_buttons.items():
            if tool == mode:
                button.state(['pressed'])
            else:
                button.state(['!pressed'])
        # Enable/disable fill checkbox
        if mode in ["rectangle", "oval"]:
            self.fill_check.state(['!disabled'])
        else:
            self.fill_var.set(False)
            self.fill_check.state(['disabled'])
        # Enable/disable brush shape selector
        if mode in ["pen", "eraser"]:
            self.brush_combo.state(['!disabled'])
        else:
            self.brush_combo.state(['disabled'])
        self.status_var.set(f"Mode: {mode.capitalize()}")
    
    def change_width(self, val):
        self.line_width = int(float(val))
        self.status_var.set(f"Line width: {self.line_width}")
    
    def choose_color(self):
        color = colorchooser.askcolor(color=self.current_color)
        if color[1]:
            self.set_color(color[1])
    
    def set_color(self, color):
        self.current_color = color
        self.color_preview.config(bg=color)
        self.status_var.set(f"Color: {color}")
    
    def clear_canvas(self):
        if messagebox.askyesno("Clear Canvas", "Are you sure you want to clear the canvas?"):
            self.canvas.delete("all")
            self.save_state()
            self.status_var.set("Canvas cleared")
    
    def save_drawing(self):
        filetypes = [("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        filename = filedialog.asksaveasfilename(defaultextension=".png", filetypes=filetypes)
        if filename:
            try:
                ps_file = filename + ".ps"
                self.canvas.postscript(file=ps_file, colormode="color")
                img = PIL.Image.open(ps_file)
                img.save(filename)
                os.remove(ps_file)
                self.status_var.set(f"Drawing saved to {filename}")
            except Exception as e:
                messagebox.showerror("Save Error", str(e))
    
    def load_drawing(self):
        filetypes = [("Image files", "*.png *.jpg *.jpeg *.gif"), ("All files", "*.*")]
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            try:
                self.canvas.delete("all")
                img = PIL.Image.open(filename)
                self.loaded_image = ImageTk.PhotoImage(img)
                self.canvas.create_image(0, 0, image=self.loaded_image, anchor=tk.NW)
                self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
                self.save_state()
                self.status_var.set(f"Loaded image from {filename}")
            except Exception as e:
                messagebox.showerror("Load Error", str(e))
    
    def save_state(self):
        ps = self.canvas.postscript(colormode="color")
        self.history.append(ps)
        self.redo_stack = []
    
    def undo(self):
        if len(self.history) > 1:
            self.redo_stack.append(self.history.pop())
            ps = self.history[-1]
            self.restore_state(ps)
            self.status_var.set("Undo performed")
    
    def redo(self):
        if self.redo_stack:
            ps = self.redo_stack.pop()
            self.history.append(ps)
            self.restore_state(ps)
            self.status_var.set("Redo performed")
    
    def restore_state(self, ps):
        self.canvas.delete("all")
        try:
            img = PIL.Image.open(io.BytesIO(ps.encode('utf-8')))
            self.restored_image = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, image=self.restored_image, anchor=tk.NW)
        except Exception:
            pass
    
    def cancel_operation(self):
        if self.drawing_mode in ["line", "rectangle", "oval"] and hasattr(self, 'temp_item'):
            if self.temp_item:
                self.canvas.delete(self.temp_item)
                self.temp_item = None
    
    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)
    
    def create_tooltip(self, widget, text):
        def enter(event):
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.overrideredirect(True)
            self.tooltip.geometry(f"+{event.x_root+15}+{event.y_root+10}")
            label = ttk.Label(self.tooltip, text=text, background="#FFFFDD", relief=tk.SOLID, borderwidth=1)
            label.pack()
        def leave(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use('clam')
    app = EnhancedDrawingApp(root)
    root.mainloop()
