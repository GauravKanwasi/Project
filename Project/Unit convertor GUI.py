import tkinter as tk
from tkinter import messagebox

# Conversion functions
def length_conversion(input_value, from_unit, to_unit):
    conversions = {
        'Meters': 1.0,
        'Feet': 3.28084,
        'Inches': 39.3701,
        'Centimeters': 100.0
    }
    meters = input_value / conversions[from_unit]
    return meters * conversions[to_unit]

def weight_conversion(input_value, from_unit, to_unit):
    conversions = {
        'Kilograms': 1.0,
        'Pounds': 2.20462,
        'Grams': 1000.0,
        'Ounces': 35.274
    }
    kg = input_value / conversions[from_unit]
    return kg * conversions[to_unit]

def temperature_conversion(input_value, from_unit, to_unit):
    if from_unit == 'Celsius' and to_unit == 'Fahrenheit':
        return input_value * 9/5 + 32
    elif from_unit == 'Fahrenheit' and to_unit == 'Celsius':
        return (input_value - 32) * 5/9
    elif from_unit == 'Celsius' and to_unit == 'Kelvin':
        return input_value + 273.15
    elif from_unit == 'Kelvin' and to_unit == 'Celsius':
        return input_value - 273.15
    elif from_unit == 'Fahrenheit' and to_unit == 'Kelvin':
        return (input_value - 32) * 5/9 + 273.15
    elif from_unit == 'Kelvin' and to_unit == 'Fahrenheit':
        return (input_value - 273.15) * 9/5 + 32
    return input_value

# Convert function based on user selection
def convert():
    try:
        input_value = float(entry_input.get())
        from_unit = from_var.get()
        to_unit = to_var.get()
        conversion_type = type_var.get()
        
        if conversion_type == 'Length':
            result = length_conversion(input_value, from_unit, to_unit)
        elif conversion_type == 'Weight':
            result = weight_conversion(input_value, from_unit, to_unit)
        elif conversion_type == 'Temperature':
            result = temperature_conversion(input_value, from_unit, to_unit)
        else:
            result_label.config(text="Invalid conversion type")
            return
        
        result_label.config(text=f"Result: {result:.2f} {to_unit}")
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number")

# Update unit options based on selected type
def update_units(*args):
    if type_var.get() == 'Length':
        units = ['Meters', 'Feet', 'Inches', 'Centimeters']
    elif type_var.get() == 'Weight':
        units = ['Kilograms', 'Pounds', 'Grams', 'Ounces']
    elif type_var.get() == 'Temperature':
        units = ['Celsius', 'Fahrenheit', 'Kelvin']
    else:
        units = []

    from_var.set('')
    to_var.set('')
    from_menu['menu'].delete(0, 'end')
    to_menu['menu'].delete(0, 'end')

    for unit in units:
        from_menu['menu'].add_command(label=unit, command=tk._setit(from_var, unit))
        to_menu['menu'].add_command(label=unit, command=tk._setit(to_var, unit))

# Create main window
root = tk.Tk()
root.title("Unit Converter")

# Conversion type selection
type_var = tk.StringVar(value='Length')
tk.Label(root, text="Select conversion type:").grid(row=0, column=0, padx=10, pady=10)
type_menu = tk.OptionMenu(root, type_var, 'Length', 'Weight', 'Temperature', command=update_units)
type_menu.grid(row=0, column=1, padx=10, pady=10)

# Input value
tk.Label(root, text="Enter value:").grid(row=1, column=0, padx=10, pady=10)
entry_input = tk.Entry(root, width=10)
entry_input.grid(row=1, column=1, padx=10, pady=10)

# From unit selection
tk.Label(root, text="From unit:").grid(row=2, column=0, padx=10, pady=10)
from_var = tk.StringVar()
from_menu = tk.OptionMenu(root, from_var, '')
from_menu.grid(row=2, column=1, padx=10, pady=10)

# To unit selection
tk.Label(root, text="To unit:").grid(row=3, column=0, padx=10, pady=10)
to_var = tk.StringVar()
to_menu = tk.OptionMenu(root, to_var, '')
to_menu.grid(row=3, column=1, padx=10, pady=10)

# Convert button
convert_button = tk.Button(root, text="Convert", command=convert)
convert_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

# Result label
result_label = tk.Label(root, text="Result: ")
result_label.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

# Initialize options
update_units()

# Run main loop
root.mainloop()
