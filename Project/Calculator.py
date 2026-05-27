def add(x, y):
    return x + y


def subtract(x, y):
    return x - y


def multiply(x, y):
    return x * y


def divide(x, y):
    if y == 0:
        return "Error! Division by zero."
    return x / y


def get_number(message):
    while True:
        try:
            return float(input(message))
        except ValueError:
            print("Invalid input. Please enter a valid number.")


def show_menu():
    print("\n===== Simple Calculator =====")
    print("1. Add")
    print("2. Subtract")
    print("3. Multiply")
    print("4. Divide")
    print("5. Exit")


def calculator():
    operations = {
        "1": ("+", add),
        "2": ("-", subtract),
        "3": ("*", multiply),
        "4": ("/", divide)
    }

    while True:
        show_menu()
        choice = input("Select an option (1-5): ").strip()

        # Exit the calculator
        if choice == "5":
            print("Calculator closed.")
            break

        # Validate user choice
        if choice not in operations:
            print("Invalid choice. Please try again.")
            continue

        # Get user input numbers
        num1 = get_number("Enter first number: ")
        num2 = get_number("Enter second number: ")

        symbol, operation = operations[choice]
        result = operation(num1, num2)

        # Display formatted result
        print(f"\nResult: {num1} {symbol} {num2} = {result}")


if __name__ == "__main__":
    calculator()
