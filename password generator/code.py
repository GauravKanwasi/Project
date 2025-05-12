import secrets
import string

def generate_password(length, uppercase=True, lowercase=True, digits=True, symbols=True):
    """
    Generate a single secure password based on user preferences.
    
    Args:
        length (int): Desired length of the password
        uppercase (bool): Include uppercase letters if True
        lowercase (bool): Include lowercase letters if True
        digits (bool): Include digits if True
        symbols (bool): Include symbols if True
    
    Returns:
        str: A secure password meeting the specified criteria
    """
    characters = []
    if uppercase:
        characters.append(string.ascii_uppercase)
    if lowercase:
        characters.append(string.ascii_lowercase)
    if digits:
        characters.append(string.digits)
    if symbols:
        characters.append(string.punctuation)

    if not characters:
        raise ValueError("At least one character type must be enabled")

    # Keep generating until all selected criteria are met
    while True:
        password = ''.join(secrets.choice(''.join(characters)) for _ in range(length))
        if (
            (not uppercase or any(c.isupper() for c in password)) and
            (not lowercase or any(c.islower() for c in password)) and
            (not digits or any(c.isdigit() for c in password)) and
            (not symbols or any(c in string.punctuation for c in password))
        ):
            return password

def get_user_preferences():
    """
    Interactively collect user preferences for password generation.
    
    Returns:
        tuple: (num_passwords, length, uppercase, lowercase, digits, symbols)
    """
    print("\n=== Let's set up your password preferences ===")
    
    # Get number of passwords
    while True:
        try:
            num_passwords = int(input("How many passwords would you like to generate (1-10)? "))
            if 1 <= num_passwords <= 10:
                break
            else:
                print("Please enter a number between 1 and 10.")
        except ValueError:
            print("Oops! That’s not a valid number. Try again.")

    # Get password length
    while True:
        try:
            length = int(input("How long should each password be (minimum 8)? "))
            if length >= 8:
                break
            else:
                print("Password length must be at least 8 characters.")
        except ValueError:
            print("Please enter a valid number.")

    # Get character type preferences
    print("\nNow, let’s decide what to include in your passwords:")
    include_upper = input("Include uppercase letters (e.g., A, B, C)? (y/n): ").lower() == 'y'
    include_lower = input("Include lowercase letters (e.g., a, b, c)? (y/n): ").lower() == 'y'
    include_digits = input("Include digits (e.g., 1, 2, 3)? (y/n): ").lower() == 'y'
    include_symbols = input("Include symbols (e.g., !, @, #)? (y/n): ").lower() == 'y'

    # Ensure at least one character type is selected
    if not any([include_upper, include_lower, include_digits, include_symbols]):
        print("\nError: You must select at least one character type. Let’s try again.")
        return get_user_preferences()  # Recursively ask again

    return num_passwords, length, include_upper, include_lower, include_digits, include_symbols

def save_password(password):
    """
    Offer to save the selected password to a file.
    
    Args:
        password (str): The password to save
    """
    save = input("\nWould you like to save this password to a file? (y/n): ").lower()
    if save == 'y':
        filename = input("Enter a filename (press Enter for 'password.txt'): ") or "password.txt"
        try:
            with open(filename, 'a') as f:
                f.write(f"Password: {password}\n")
            print(f"Great! Your password has been saved to '{filename}'.")
        except Exception as e:
            print(f"Sorry, there was an error saving the file: {e}")
    else:
        print("No worries, your password won’t be saved.")

def main():
    """Run the interactive password generator."""
    print("=== Welcome to the Password Generator! ===")
    print("Generate secure passwords easily and pick your favorite.")
    print("You’ll answer a few questions to customize your passwords.\n")

    while True:
        # Get user preferences
        num_passwords, length, uppercase, lowercase, digits, symbols = get_user_preferences()

        # Generate and display passwords
        while True:
            passwords = [generate_password(length, uppercase, lowercase, digits, symbols) 
                        for _ in range(num_passwords)]
            print("\n=== Here are your generated passwords ===")
            for i, pwd in enumerate(passwords, 1):
                print(f"{i}. {pwd}")

            # Get user choice
            print("\nWhat would you like to do?")
            choice = input("Enter a number to select a password, 'r' to regenerate, or 'q' to quit: ").lower()

            if choice == 'q':
                print("\nThanks for using the Password Generator. Goodbye!")
                return
            elif choice == 'r':
                print("\nGenerating a new set of passwords...")
                continue  # Regenerate with same preferences
            else:
                try:
                    choice = int(choice)
                    if 1 <= choice <= num_passwords:
                        selected_password = passwords[choice - 1]
                        print(f"\nYou’ve selected: {selected_password}")
                        save_password(selected_password)
                        break  # Move to asking if they want more
                    else:
                        print(f"Please pick a number between 1 and {num_passwords}.")
                except ValueError:
                    print("Invalid choice. Use a number, 'r', or 'q'.")

        # Ask if they want to generate more
        generate_more = input("\nWould you like to generate another set of passwords? (y/n): ").lower()
        if generate_more != 'y':
            print("\nThanks for using the Password Generator. See you next time!")
            return
        print("\nAlright, let’s create some more passwords!")

if __name__ == "__main__":
    main()
