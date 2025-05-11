import tkinter as tk
import math

class ScientificCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Scientific Calculator")
        self.root.geometry("400x600")
        self.root.resizable(0, 0)
        self.expression = ""
        self.memory = 0
        self.input_text = tk.StringVar()
        self.angle_mode = 'deg'

        # Input field as Label
        self.input_field = tk.Label(self.root, font=('arial', 20, 'bold'), textvariable=self.input_text, 
                                    width=25, bg="#f0f0f0", bd=5, anchor='e')
        self.input_field.pack(pady=5)

        # Mode toggle button
        self.mode_button = tk.Button(self.root, text="DEG", font=('arial', 10), relief='flat', 
                                     command=self.toggle_mode)
        self.mode_button.pack()

        # Buttons frame
        btns_frame = tk.Frame(self.root, bg="#e0e0e0")
        btns_frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Define hover colors
        self.hover_colors = {
            '#ff6666': '#ff9999',  # Red to lighter red
            '#66b3ff': '#99ccff',  # Blue to lighter blue
            '#f2f2f2': '#ffffff',  # Light gray to white
            '#c0c0c0': '#d9d9d9',  # Medium gray to lighter gray
            '#99ff99': '#b3ffb3',  # Green to lighter green
            '#ffcc00': '#ffe066',  # Orange to lighter orange
            '#ffff99': '#ffffcc'   # Yellow to lighter yellow
        }

        # Button layout
        buttons = [
            ['AC', 'C', '(', ')'],
            ['sin', 'cos', 'tan', '√'],
            ['sin⁻¹', 'cos⁻¹', 'tan⁻¹', 'xʸ'],
            ['log', 'ln', 'eˣ', 'x!'],
            ['7', '8', '9', '/'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '-'],
            ['0', '.', '±', '+'],
            ['π', 'e', '%', '='],
            ['M+', 'M-', 'MR', 'MC']
        ]

        # Create buttons with hover effects
        for row, button_row in enumerate(buttons):
            for col, text in enumerate(button_row):
                if row == 0:
                    bg = '#ff6666'  # Reset functions
                elif 1 <= row <= 3:
                    bg = '#66b3ff'  # Scientific functions
                elif 4 <= row <= 7:
                    bg = '#f2f2f2' if col < 3 else '#c0c0c0'  # Numbers vs operators
                elif row == 8:
                    bg = '#ffcc00' if text == '=' else '#99ff99'  # Equals vs constants
                elif row == 9:
                    bg = '#ffff99'  # Memory functions
                btn = tk.Button(btns_frame, text=text, font=('arial', 12, 'bold'), fg="black", bg=bg, 
                                width=8, height=2, bd=1, cursor="hand2", 
                                command=lambda x=text: self.on_button_click(x))
                btn.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
                btn.bind("<Enter>", lambda event, b=btn, hc=self.hover_colors.get(bg, bg): b.config(bg=hc))
                btn.bind("<Leave>", lambda event, b=btn, oc=bg: b.config(bg=oc))

        # Configure grid for even button sizing
        for i in range(10):
            btns_frame.grid_rowconfigure(i, weight=1)
        for i in range(4):
            btns_frame.grid_columnconfigure(i, weight=1)

        # Bind keyboard events
        self.root.bind("<Key>", self.on_key_press)

    def toggle_mode(self):
        """Toggle between degree and radian modes."""
        if self.angle_mode == 'deg':
            self.angle_mode = 'rad'
            self.mode_button.config(text="RAD")
        else:
            self.angle_mode = 'deg'
            self.mode_button.config(text="DEG")

    def on_button_click(self, char):
        """Handle button clicks."""
        if char == '=':
            try:
                result = eval(self.expression.replace('π', str(math.pi)).replace('e', str(math.e)))
                self.input_text.set(result)
                self.expression = str(result)
            except Exception:
                self.set_error()
                self.expression = ""
        elif char == 'C':
            self.expression = self.expression[:-1]
            self.input_text.set(self.expression)
        elif char == 'AC':
            self.expression = ""
            self.input_text.set("")
        elif char == '±':
            self.expression = '-' + self.expression if self.expression and self.expression[0] != '-' else self.expression[1:]
            self.input_text.set(self.expression)
        elif char in ['M+', 'M-', 'MR', 'MC']:
            self.handle_memory(char)
        elif char in ['sin', 'cos', 'tan', 'sin⁻¹', 'cos⁻¹', 'tan⁻¹', 'log', 'ln', '√', 'xʸ', 'eˣ', 'x!']:
            self.handle_scientific(char)
        else:
            self.expression += char
            self.input_text.set(self.expression)

    def handle_scientific(self, func):
        """Handle scientific function calculations."""
        try:
            value = float(eval(self.expression)) if self.expression else 0
            if func in ['sin', 'cos', 'tan']:
                angle = math.radians(value) if self.angle_mode == 'deg' else value
                result = {'sin': math.sin, 'cos': math.cos, 'tan': math.tan}[func](angle)
            elif func in ['sin⁻¹', 'cos⁻¹', 'tan⁻¹']:
                if func in ['sin⁻¹', 'cos⁻¹'] and (value < -1 or value > 1):
                    raise ValueError
                result = {'sin⁻¹': math.asin, 'cos⁻¹': math.acos, 'tan⁻¹': math.atan}[func](value)
                if self.angle_mode == 'deg':
                    result = math.degrees(result)
            elif func == 'log':
                if value <= 0: raise ValueError
                result = math.log10(value)
            elif func == 'ln':
                if value <= 0: raise ValueError
                result = math.log(value)
            elif func == '√':
                if value < 0: raise ValueError
                result = math.sqrt(value)
            elif func == 'xʸ':
                self.expression += '**'
                self.input_text.set(self.expression)
                return
            elif func == 'eˣ':
                result = math.exp(value)
            elif func == 'x!':
                if value < 0 or not float(value).is_integer(): raise ValueError
                result = math.factorial(int(value))
            self.expression = str(result)
            self.input_text.set(result)
        except Exception:
            self.set_error()
            self.expression = ""

    def handle_memory(self, func):
        """Handle memory operations."""
        try:
            value = float(eval(self.expression)) if self.expression else 0
            if func == 'M+':
                self.memory += value
            elif func == 'M-':
                self.memory -= value
            elif func == 'MR':
                self.expression = str(self.memory)
                self.input_text.set(self.expression)
            elif func == 'MC':
                self.memory = 0
        except Exception:
            self.set_error()
            self.expression = ""

    def on_key_press(self, event):
        """Handle keyboard input."""
        key = event.keysym
        if key in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']:
            self.expression += key
            self.input_text.set(self.expression)
        elif key in ['plus', 'minus', 'asterisk', 'slash']:
            op = {'plus': '+', 'minus': '-', 'asterisk': '*', 'slash': '/'}[key]
            self.expression += op
            self.input_text.set(self.expression)
        elif key == 'Return':
            self.on_button_click('=')
        elif key == 'BackSpace':
            self.expression = self.expression[:-1]
            self.input_text.set(self.expression)
        elif key in ['parenleft', 'parenright']:
            paren = {'parenleft': '(', 'parenright': ')'}[key]
            self.expression += paren
            self.input_text.set(self.expression)

    def set_error(self):
        """Display error with visual feedback."""
        self.input_text.set("Error")
        self.input_field.config(bg='red')
        self.root.after(1000, lambda: self.input_field.config(bg='#f0f0f0'))

if __name__ == "__main__":
    root = tk.Tk()
    calc = ScientificCalculator(root)
    root.mainloop()
