# Length conversions
def meters_to_feet(meters):
    return meters * 3.28084

def feet_to_meters(feet):
    return feet / 3.28084

# Weight conversions
def kilograms_to_pounds(kg):
    return kg * 2.20462

def pounds_to_kilograms(pounds):
    return pounds / 2.20462

# Temperature conversions
def celsius_to_fahrenheit(celsius):
    return celsius * 9/5 + 32

def fahrenheit_to_celsius(fahrenheit):
    return (fahrenheit - 32) * 5/9

def unit_converter():
    print("Welcome to the Unit Converter!")
    print("Select the type of conversion:")
    print("1. Length")
    print("2. Weight")
    print("3. Temperature")

    choice = input("Enter choice (1/2/3): ")

    if choice == '1':
        print("Length Conversion:")
        print("a. Meters to Feet")
        print("b. Feet to Meters")
        length_choice = input("Enter choice (a/b): ")

        if length_choice == 'a':
            meters = float(input("Enter value in meters: "))
            print(f"{meters} meters is {meters_to_feet(meters):.2f} feet")
        elif length_choice == 'b':
            feet = float(input("Enter value in feet: "))
            print(f"{feet} feet is {feet_to_meters(feet):.2f} meters")
        else:
            print("Invalid choice.")

    elif choice == '2':
        print("Weight Conversion:")
        print("a. Kilograms to Pounds")
        print("b. Pounds to Kilograms")
        weight_choice = input("Enter choice (a/b): ")

        if weight_choice == 'a':
            kg = float(input("Enter value in kilograms: "))
            print(f"{kg} kilograms is {kilograms_to_pounds(kg):.2f} pounds")
        elif weight_choice == 'b':
            pounds = float(input("Enter value in pounds: "))
            print(f"{pounds} pounds is {pounds_to_kilograms(pounds):.2f} kilograms")
        else:
            print("Invalid choice.")

    elif choice == '3':
        print("Temperature Conversion:")
        print("a. Celsius to Fahrenheit")
        print("b. Fahrenheit to Celsius")
        temp_choice = input("Enter choice (a/b): ")

        if temp_choice == 'a':
            celsius = float(input("Enter value in Celsius: "))
            print(f"{celsius} degrees Celsius is {celsius_to_fahrenheit(celsius):.2f} degrees Fahrenheit")
        elif temp_choice == 'b':
            fahrenheit = float(input("Enter value in Fahrenheit: "))
            print(f"{fahrenheit} degrees Fahrenheit is {fahrenheit_to_celsius(fahrenheit):.2f} degrees Celsius")
        else:
            print("Invalid choice.")

    else:
        print("Invalid choice.")

if __name__ == "__main__":
    unit_converter()
