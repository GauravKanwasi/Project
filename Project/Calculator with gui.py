import tkinter as tk
from tkinter import messagebox

def add():
    try:
        result = float(entry1.get()) + float(entry2.get())
        result_label.config(text=f"Result: {result}")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers")

def subtract():
    try:
        result = float(entry1.get()) - float(entry2.get())
        result_label.config(text=f"Result: {result}")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers")

def multiply():
    try:
        result = float(entry1.get()) * float(entry2.get())
        result_label.config(text=f"Result: {result}")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers")

def divide():
    try:
        if float(entry2.get()) != 0:
            result = float(entry1.get()) / float(entry2.get())
            result_label.config(text=f"Result: {result}")
        else:
            messagebox.showerror("Error", "Division by zero is not allowed")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers")

# Create the main window
root = tk.Tk()
root.title("Simple Calculator")

# Create and place the widgets
entry1 = tk.Entry(root, width=10)
entry1.grid(row=0, column=0, padx=10, pady=10)

entry2 = tk.Entry(root, width=10)
entry2.grid(row=0, column=1, padx=10, pady=10)

add_button = tk.Button(root, text="Add", command=add)
add_button.grid(row=1, column=0, padx=10, pady=10)

subtract_button = tk.Button(root, text="Subtract", command=subtract)
subtract_button.grid(row=1, column=1, padx=10, pady=10)

multiply_button = tk.Button(root, text="Multiply", command=multiply)
multiply_button.grid(row=2, column=0, padx=10, pady=10)

divide_button = tk.Button(root, text="Divide", command=divide)
divide_button.grid(row=2, column=1, padx=10, pady=10)

result_label = tk.Label(root, text="Result: ")
result_label.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# Run the main loop
root.mainloop()