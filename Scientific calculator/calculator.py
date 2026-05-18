import tkinter as tk
from tkinter import ttk
import math


class ScientificCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Scientific Calculator")
        self.root.geometry("430x720")
        self.root.minsize(400, 650)

        # ===== Variables =====
        self.expression = ""
        self.memory = 0
        self.angle_mode = "DEG"

        # ===== Theme Colors =====
        self.bg_main = "#1e1e1e"
        self.bg_display = "#2d2d2d"
        self.btn_dark = "#333333"
        self.btn_light = "#444444"
        self.btn_operator = "#ff9500"
        self.btn_scientific = "#0066cc"
        self.btn_equal = "#00aa55"
        self.text_color = "white"

        self.root.configure(bg=self.bg_main)

        # ===== Display Frame =====
        display_frame = tk.Frame(root, bg=self.bg_main)
        display_frame.pack(fill="both", padx=10, pady=10)

        # Expression display
        self.expression_var = tk.StringVar()
        self.result_var = tk.StringVar()

        self.expression_label = tk.Label(
            display_frame,
            textvariable=self.expression_var,
            font=("Segoe UI", 14),
            bg=self.bg_display,
            fg="#bbbbbb",
            anchor="e",
            padx=10,
            pady=10
        )
        self.expression_label.pack(fill="both")

        # Result display
        self.result_label = tk.Label(
            display_frame,
            textvariable=self.result_var,
            font=("Segoe UI", 28, "bold"),
            bg=self.bg_display,
            fg=self.text_color,
            anchor="e",
            padx=10,
            pady=15
        )
        self.result_label.pack(fill="both")

        # ===== Top Control Buttons =====
        top_frame = tk.Frame(root, bg=self.bg_main)
        top_frame.pack(fill="x", padx=10)

        self.mode_button = tk.Button(
            top_frame,
            text="DEG",
            font=("Segoe UI", 11, "bold"),
            bg="#555555",
            fg="white",
            relief="flat",
            command=self.toggle_angle_mode
        )
        self.mode_button.pack(side="left", padx=5, pady=5)

        # ===== Buttons Layout =====
        buttons_frame = tk.Frame(root, bg=self.bg_main)
        buttons_frame.pack(expand=True, fill="both", padx=10, pady=10)

        buttons = [
            ['AC', '⌫', '(', ')'],
            ['sin', 'cos', 'tan', '√'],
            ['asin', 'acos', 'atan', '^'],
            ['log', 'ln', 'eˣ', '!'],
            ['7', '8', '9', '/'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '-'],
            ['0', '.', 'π', '+'],
            ['%', '±', 'Ans', '='],
            ['M+', 'M-', 'MR', 'MC']
        ]

        # ===== Create Buttons =====
        for r, row in enumerate(buttons):
            for c, text in enumerate(row):

                color = self.get_button_color(text)

                button = tk.Button(
                    buttons_frame,
                    text=text,
                    font=("Segoe UI", 14, "bold"),
                    bg=color,
                    fg="white",
                    relief="flat",
                    activebackground="#666666",
                    activeforeground="white",
                    borderwidth=0,
                    command=lambda value=text: self.button_click(value)
                )

                button.grid(
                    row=r,
                    column=c,
                    sticky="nsew",
                    padx=4,
                    pady=4,
                    ipadx=5,
                    ipady=15
                )

        # ===== Responsive Grid =====
        for i in range(10):
            buttons_frame.grid_rowconfigure(i, weight=1)

        for i in range(4):
            buttons_frame.grid_columnconfigure(i, weight=1)

        # ===== Keyboard Bindings =====
        self.root.bind("<Key>", self.handle_keyboard)

    # =========================================================
    # Return proper button colors
    # =========================================================
    def get_button_color(self, text):

        if text in ['+', '-', '*', '/', '=']:
            return self.btn_operator

        if text == '=':
            return self.btn_equal

        if text in [
            'sin', 'cos', 'tan',
            'asin', 'acos', 'atan',
            'log', 'ln', '√',
            'eˣ', '^', '!'
        ]:
            return self.btn_scientific

        if text in ['AC', '⌫']:
            return "#cc3333"

        return self.btn_dark

    # =========================================================
    # Toggle Degree / Radian mode
    # =========================================================
    def toggle_angle_mode(self):

        if self.angle_mode == "DEG":
            self.angle_mode = "RAD"
        else:
            self.angle_mode = "DEG"

        self.mode_button.config(text=self.angle_mode)

    # =========================================================
    # Main button click handler
    # =========================================================
    def button_click(self, value):

        try:

            # ===== Clear Everything =====
            if value == "AC":
                self.expression = ""
                self.result_var.set("")
                self.expression_var.set("")
                return

            # ===== Backspace =====
            if value == "⌫":
                self.expression = self.expression[:-1]
                self.expression_var.set(self.expression)
                return

            # ===== Calculate =====
            if value == "=":
                result = self.calculate(self.expression)

                self.result_var.set(str(result))
                self.expression = str(result)

                return

            # ===== Positive / Negative =====
            if value == "±":

                if self.expression.startswith("-"):
                    self.expression = self.expression[1:]
                else:
                    self.expression = "-" + self.expression

                self.expression_var.set(self.expression)
                return

            # ===== Memory Operations =====
            if value in ['M+', 'M-', 'MR', 'MC']:
                self.memory_operations(value)
                return

            # ===== Special Symbols =====
            replacements = {
                'π': str(math.pi),
                '^': '**'
            }

            self.expression += replacements.get(value, value)

            self.expression_var.set(self.expression)

        except Exception:
            self.show_error()

    # =========================================================
    # Safe calculator engine
    # =========================================================
    def calculate(self, expression):

        # Replace scientific keywords
        expression = expression.replace('√', 'math.sqrt')
        expression = expression.replace('log', 'math.log10')
        expression = expression.replace('ln', 'math.log')
        expression = expression.replace('eˣ', 'math.exp')
        expression = expression.replace('%', '/100')

        # ===== Trigonometric Functions =====
        if 'sin' in expression:
            expression = expression.replace(
                'sin',
                'math.sin'
            )

        if 'cos' in expression:
            expression = expression.replace(
                'cos',
                'math.cos'
            )

        if 'tan' in expression:
            expression = expression.replace(
                'tan',
                'math.tan'
            )

        if 'asin' in expression:
            expression = expression.replace(
                'asin',
                'math.asin'
            )

        if 'acos' in expression:
            expression = expression.replace(
                'acos',
                'math.acos'
            )

        if 'atan' in expression:
            expression = expression.replace(
                'atan',
                'math.atan'
            )

        # ===== Factorial Support =====
        if expression.endswith('!'):

            number = expression[:-1]

            result = math.factorial(int(eval(number)))

            return result

        # ===== Evaluate Expression Safely =====
        result = eval(expression, {"math": math})

        # ===== Convert radians to degrees if needed =====
        return round(result, 10)

    # =========================================================
    # Memory Operations
    # =========================================================
    def memory_operations(self, operation):

        try:

            current = float(self.result_var.get() or 0)

            if operation == "M+":
                self.memory += current

            elif operation == "M-":
                self.memory -= current

            elif operation == "MR":
                self.expression += str(self.memory)
                self.expression_var.set(self.expression)

            elif operation == "MC":
                self.memory = 0

        except Exception:
            self.show_error()

    # =========================================================
    # Keyboard Support
    # =========================================================
    def handle_keyboard(self, event):

        key = event.keysym

        allowed = "0123456789+-*/()."

        if event.char in allowed:
            self.expression += event.char
            self.expression_var.set(self.expression)

        elif key == "Return":
            self.button_click("=")

        elif key == "BackSpace":
            self.button_click("⌫")

        elif key == "Escape":
            self.button_click("AC")

    # =========================================================
    # Error Display
    # =========================================================
    def show_error(self):

        self.result_var.set("Error")
        self.root.after(1200, lambda: self.result_var.set(""))


# =============================================================
# Main Application
# =============================================================
if __name__ == "__main__":

    root = tk.Tk()

    app = ScientificCalculator(root)

    root.mainloop()
