import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


class CalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Calculator")
        self.root.geometry("420x500")
        self.root.resizable(False, False)

        # Theme Colors
        self.bg_color = "#1e1e1e"
        self.frame_color = "#2d2d2d"
        self.button_color = "#3c3f41"
        self.text_color = "#ffffff"
        self.accent_color = "#4CAF50"

        self.root.configure(bg=self.bg_color)

        self.history = []

        self.create_widgets()
        self.bind_keys()

    def create_widgets(self):
        # Title
        title = tk.Label(
            self.root,
            text="Calculator",
            font=("Arial", 22, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        title.pack(pady=15)

        # Input Frame
        input_frame = tk.Frame(self.root, bg=self.frame_color, padx=10, pady=10)
        input_frame.pack(padx=20, pady=10, fill="x")

        # Number 1
        tk.Label(
            input_frame,
            text="First Number",
            bg=self.frame_color,
            fg=self.text_color,
            font=("Arial", 11)
        ).grid(row=0, column=0, sticky="w", pady=5)

        self.entry1 = ttk.Entry(input_frame, font=("Arial", 14))
        self.entry1.grid(row=1, column=0, padx=5, pady=5)

        # Number 2
        tk.Label(
            input_frame,
            text="Second Number",
            bg=self.frame_color,
            fg=self.text_color,
            font=("Arial", 11)
        ).grid(row=0, column=1, sticky="w", pady=5)

        self.entry2 = ttk.Entry(input_frame, font=("Arial", 14))
        self.entry2.grid(row=1, column=1, padx=5, pady=5)

        # Buttons Frame
        button_frame = tk.Frame(self.root, bg=self.bg_color)
        button_frame.pack(pady=15)

        buttons = [
            ("+", self.add),
            ("-", self.subtract),
            ("×", self.multiply),
            ("÷", self.divide),
            ("Power", self.power),
            ("Clear", self.clear_fields),
        ]

        row = 0
        col = 0

        for text, command in buttons:
            btn = tk.Button(
                button_frame,
                text=text,
                command=command,
                width=12,
                height=2,
                font=("Arial", 12, "bold"),
                bg=self.button_color,
                fg=self.text_color,
                activebackground=self.accent_color,
                relief="flat",
                cursor="hand2"
            )

            btn.grid(row=row, column=col, padx=8, pady=8)

            col += 1
            if col > 1:
                col = 0
                row += 1

        # Result Label
        self.result_label = tk.Label(
            self.root,
            text="Result: ",
            font=("Arial", 18, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        self.result_label.pack(pady=15)

        # History Section
        history_frame = tk.Frame(self.root, bg=self.frame_color)
        history_frame.pack(padx=20, pady=10, fill="both", expand=True)

        tk.Label(
            history_frame,
            text="Calculation History",
            font=("Arial", 12, "bold"),
            bg=self.frame_color,
            fg=self.text_color
        ).pack(pady=5)

        self.history_box = tk.Text(
            history_frame,
            height=8,
            bg="#121212",
            fg="#00ff90",
            font=("Consolas", 11),
            relief="flat"
        )
        self.history_box.pack(fill="both", expand=True, padx=10, pady=10)

    def bind_keys(self):
        self.root.bind("<Return>", lambda event: self.add())
        self.root.bind("<Escape>", lambda event: self.clear_fields())

    def get_numbers(self):
        try:
            num1 = float(self.entry1.get())
            num2 = float(self.entry2.get())
            return num1, num2
        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Please enter valid numeric values."
            )
            return None

    def format_result(self, result):
        if result.is_integer():
            return int(result)
        return round(result, 6)

    def update_result(self, expression, result):
        formatted_result = self.format_result(float(result))

        self.result_label.config(text=f"Result: {formatted_result}")

        history_entry = f"{expression} = {formatted_result}\n"
        self.history.append(history_entry)

        self.history_box.insert(tk.END, history_entry)
        self.history_box.see(tk.END)

    def add(self):
        values = self.get_numbers()
        if values:
            num1, num2 = values
            result = num1 + num2
            self.update_result(f"{num1} + {num2}", result)

    def subtract(self):
        values = self.get_numbers()
        if values:
            num1, num2 = values
            result = num1 - num2
            self.update_result(f"{num1} - {num2}", result)

    def multiply(self):
        values = self.get_numbers()
        if values:
            num1, num2 = values
            result = num1 * num2
            self.update_result(f"{num1} × {num2}", result)

    def divide(self):
        values = self.get_numbers()
        if values:
            num1, num2 = values

            if num2 == 0:
                messagebox.showerror(
                    "Math Error",
                    "Division by zero is not allowed."
                )
                return

            result = num1 / num2
            self.update_result(f"{num1} ÷ {num2}", result)

    def power(self):
        values = self.get_numbers()
        if values:
            num1, num2 = values
            result = num1 ** num2
            self.update_result(f"{num1} ^ {num2}", result)

    def clear_fields(self):
        self.entry1.delete(0, tk.END)
        self.entry2.delete(0, tk.END)
        self.result_label.config(text="Result: ")
        self.entry1.focus()


# Main Application
if __name__ == "__main__":
    root = tk.Tk()
    app = CalculatorApp(root)
    root.mainloop()
