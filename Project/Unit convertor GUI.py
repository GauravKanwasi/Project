import tkinter as tk
from tkinter import ttk, messagebox

# --- Conversion Functions ---
def length_conversion(input_value, from_unit, to_unit):
    if from_unit == to_unit: return input_value
    conversions = {
        'Meters': 1.0,
        'Feet': 3.28084,
        'Inches': 39.3701,
        'Centimeters': 100.0
    }
    meters = input_value / conversions[from_unit]
    return meters * conversions[to_unit]

def weight_conversion(input_value, from_unit, to_unit):
    if from_unit == to_unit: return input_value
    conversions = {
        'Kilograms': 1.0,
        'Pounds': 2.20462,
        'Grams': 1000.0,
        'Ounces': 35.274
    }
    kg = input_value / conversions[from_unit]
    return kg * conversions[to_unit]

def temperature_conversion(input_value, from_unit, to_unit):
    if from_unit == to_unit: return input_value
    
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

# --- Main Application Logic ---
def convert():
    try:
        input_text = entry_input.get().strip()
        if not input_text:
            messagebox.showwarning("Warning", "Please enter a value to convert.")
            return
            
        input_value = float(input_text)
        from_unit = from_var.get()
        to_unit = to_var.get()
        conversion_type = type_var.get()
        
        if not from_unit or not to_unit:
            messagebox.showwarning("Warning", "Please select both 'From' and 'To' units.")
            return
        
        if conversion_type == 'Length':
            result = length_conversion(input_value, from_unit, to_unit)
        elif conversion_type == 'Weight':
            result = weight_conversion(input_value, from_unit, to_unit)
        elif conversion_type == 'Temperature':
            result = temperature_conversion(input_value, from_unit, to_unit)
        else:
            result_label.config(text="Invalid conversion type")
            return
        
        result_label.config(text=f"{input_value:g} {from_unit} = {result:.3f} {to_unit}")
        
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid numeric value.")

def update_units(*args):
    selection = type_var.get()
    if selection == 'Length':
        units = ['Meters', 'Feet', 'Inches', 'Centimeters']
    elif selection == 'Weight':
        units = ['Kilograms', 'Pounds', 'Grams', 'Ounces']
    elif selection == 'Temperature':
        units = ['Celsius', 'Fahrenheit', 'Kelvin']
    else:
        units = []

    from_combobox['values'] = units
    to_combobox['values'] = units

    # Prevent empty string errors by auto-selecting valid defaults
    if units:
        from_combobox.current(0)
        to_combobox.current(1 if len(units) > 1 else 0)

# --- GUI Setup ---
root = tk.Tk()
root.title("Unit Converter")
root.geometry("350x300")  
root.resizable(False, False) 

main_frame = ttk.Frame(root, padding="20 20 20 20")
main_frame.pack(fill=tk.BOTH, expand=True)

type_var = tk.StringVar(value='Length')
from_var = tk.StringVar()
to_var = tk.StringVar()

ttk.Label(main_frame, text="Category:", font=("Helvetica", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
type_combobox = ttk.Combobox(main_frame, textvariable=type_var, state="readonly", width=18)
type_combobox['values'] = ('Length', 'Weight', 'Temperature')
type_combobox.grid(row=0, column=1, pady=5, sticky=tk.E)
type_combobox.bind('<<ComboboxSelected>>', update_units) 

ttk.Label(main_frame, text="Value:", font=("Helvetica", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
entry_input = ttk.Entry(main_frame, width=20)
entry_input.grid(row=1, column=1, pady=5, sticky=tk.E)

ttk.Label(main_frame, text="From Unit:", font=("Helvetica", 10)).grid(row=2, column=0, sticky=tk.W, pady=5)
from_combobox = ttk.Combobox(main_frame, textvariable=from_var, state="readonly", width=18)
from_combobox.grid(row=2, column=1, pady=5, sticky=tk.E)

ttk.Label(main_frame, text="To Unit:", font=("Helvetica", 10)).grid(row=3, column=0, sticky=tk.W, pady=5)
to_combobox = ttk.Combobox(main_frame, textvariable=to_var, state="readonly", width=18)
to_combobox.grid(row=3, column=1, pady=5, sticky=tk.E)

convert_button = ttk.Button(main_frame, text="Convert", command=convert)
convert_button.grid(row=4, column=0, columnspan=2, pady=15, sticky=tk.EW)

result_label = ttk.Label(main_frame, text="Result will appear here", font=("Helvetica", 11, "bold"), foreground="#333333")
result_label.grid(row=5, column=0, columnspan=2, pady=5)

update_units()
root.mainloop()
