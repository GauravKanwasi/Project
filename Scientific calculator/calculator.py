import tkinter as tk
import math

class ScientificCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Scientific Calculator")
        self.root.geometry("400x600")  # Set window size
        self.root.resizable(0, 0)      # Disable resizing
        self.expression = ""
        self.memory = 0                # Memory storage
        self.input_text = tk.StringVar()

        # Input field
        input_field = tk.Entry(self.root, font=('arial', 20, 'bold'), textvariable=self.input_text, 
                               width=25, bg="#f0f0f0", bd=5, justify=tk.RIGHT)
        input_field.pack(pady=10)

        # Buttons frame
        btns_frame = tk.Frame(self.root, bg="#e0e0e0")
        btns_frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Button layout with enhanced design
        buttons = [
            ['AC', 'C', '(', ')', 'bg=#ff9999'],
            ['sin', 'cos', 'tan', '√', 'bg=#99ccff'],
            ['sin⁻¹', 'cos⁻¹', 'tan⁻¹', 'xʸ', 'bg=#99ccff'],
            ['log', 'ln', 'eˣ', 'x!', 'bg=#99ccff'],
            ['7', '8', '9', '/', 'bg=#d9d9d9'],
            ['4', '5', '6', '*', 'bg=#d9d9d9'],
            ['1', '2', '3', '-', 'bg=#d9d9d9'],
            ['0', '.', '±', '+', 'bg=#d9d9d9'],
            ['π', 'e', '%', '=', 'bg=#b3ffb3'],
            ['M+', 'M-', 'MR', 'MC', 'bg=#ffff99']
        ]

        # Create and place buttons
        for row, button_row in enumerate(buttons):
            for col, button in enumerate(button_row):
                bg_color = button_row[-1].split('=')[1] if 'bg=' in button_row[-1] else '#d9d9d9'
                text = button if 'bg=' not in button else button
                btn = tk.Button(btns_frame, text=text, font=('arial', 12, 'bold'), fg="black", bg=bg_color, 
                                width=8, height=2, bd=1, cursor="hand2", 
                                command=lambda x=text: self.on_button_click(x))
                btn.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")

        # Configure grid to expand buttons evenly
        for i in range(10):
            btns_frame.grid_rowconfigure(i, weight=1)
        for i in range(4):
            btns_frame.grid_columnconfigure(i, weight=1)

    def on_button_click(self, char):
        if char == '=':
            try:
                result = eval(self.expression.replace('π', str(math.pi)).replace('e', str(math.e)))
                self.input_text.set(result)
                self.expression = str(result)
            except Exception:
                self.input_text.set("Error")
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
        try:
            value = float(eval(self.expression)) if self.expression else 0
            if func == 'sin':
                result = math.sin(math.radians(value))
            elif func == 'cos':
                result = math.cos(math.radians(value))
            elif func == 'tan':
                result = math.tan(math.radians(value))
            elif func == 'sin⁻¹':
                if value < -1 or value > 1: raise ValueError
                result = math.degrees(math.asin(value))
            elif func == 'cos⁻¹':
                if value < -1 or value > 1: raise ValueError
                result = math.degrees(math.acos(value))
            elif func == 'tan⁻¹':
                result = math.degrees(math.atan(value))
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
            self.input_text.set("Error")
            self.expression = ""

    def handle_memory(self, func):
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
            self.input_text.set("Error")
            self.expression = ""

if __name__ == "__main__":
    root = tk.Tk()
    calc = ScientificCalculator(root)
    root.mainloop()
