"""
Universal Unit Converter
Supports:
1. Length conversions
2. Weight conversions
3. Temperature conversions

Enhanced Features:
- Cleaner structure
- Input validation
- Reusable conversion system
- Better user experience
- Loop support for multiple conversions
"""

# =========================
# Conversion Functions
# =========================

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
    return (celsius * 9 / 5) + 32


def fahrenheit_to_celsius(fahrenheit):
    return (fahrenheit - 32) * 5 / 9


# =========================
# Helper Functions
# =========================

def get_float_input(message):
    """
    Safely takes numeric input from the user.
    Keeps asking until a valid number is entered.
    """
    while True:
        try:
            return float(input(message))
        except ValueError:
            print("Invalid input. Please enter a numeric value.")


def display_result(value, from_unit, converted_value, to_unit):
    """
    Displays formatted conversion result.
    """
    print(f"\n{value:.2f} {from_unit} = {converted_value:.2f} {to_unit}\n")


# =========================
# Main Converter Logic
# =========================

def unit_converter():

    # Dictionary-based conversion system
    # Makes the program scalable and easier to maintain
    conversions = {

        "1": {
            "name": "Length",
            "options": {
                "a": ("Meters", "Feet", meters_to_feet),
                "b": ("Feet", "Meters", feet_to_meters),
            },
        },

        "2": {
            "name": "Weight",
            "options": {
                "a": ("Kilograms", "Pounds", kilograms_to_pounds),
                "b": ("Pounds", "Kilograms", pounds_to_kilograms),
            },
        },

        "3": {
            "name": "Temperature",
            "options": {
                "a": ("Celsius", "Fahrenheit", celsius_to_fahrenheit),
                "b": ("Fahrenheit", "Celsius", fahrenheit_to_celsius),
            },
        },
    }

    print("=" * 45)
    print("      Welcome to the Unit Converter")
    print("=" * 45)

    while True:

        # Main menu
        print("\nSelect the type of conversion:")
        print("1. Length")
        print("2. Weight")
        print("3. Temperature")
        print("4. Exit")

        choice = input("\nEnter choice (1/2/3/4): ").strip()

        # Exit condition
        if choice == "4":
            print("\nThank you for using the Unit Converter!")
            break

        # Validate category choice
        if choice not in conversions:
            print("Invalid choice. Please try again.")
            continue

        category = conversions[choice]

        print(f"\n{category['name']} Conversion:")

        # Display available options dynamically
        for key, (from_unit, to_unit, _) in category["options"].items():
            print(f"{key}. {from_unit} to {to_unit}")

        sub_choice = input("\nEnter choice: ").strip().lower()

        # Validate conversion option
        if sub_choice not in category["options"]:
            print("Invalid conversion choice.")
            continue

        from_unit, to_unit, conversion_function = \
            category["options"][sub_choice]

        # Get user input safely
        value = get_float_input(f"Enter value in {from_unit}: ")

        # Perform conversion
        result = conversion_function(value)

        # Display formatted result
        display_result(value, from_unit, result, to_unit)


# =========================
# Program Entry Point
# =========================

if __name__ == "__main__":
    unit_converter()
