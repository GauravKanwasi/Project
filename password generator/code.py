import argparse
import secrets
import string

def generate_password(length, uppercase=True, lowercase=True, digits=True, symbols=True):
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

    while True:
        password = ''.join(secrets.choice(''.join(characters)) for _ in range(length))
        if (
            (not uppercase or any(c.isupper() for c in password)) and
            (not lowercase or any(c.islower() for c in password)) and
            (not digits or any(c.isdigit() for c in password)) and
            (not symbols or any(c in string.punctuation for c in password))
        ):
            return password

def main():
    parser = argparse.ArgumentParser(description="Generate secure passwords")
    parser.add_argument("length", type=int, help="Password length (minimum 8)")
    parser.add_argument("--no-uppercase", action="store_false", dest="uppercase", help="Exclude uppercase letters")
    parser.add_argument("--no-lowercase", action="store_false", dest="lowercase", help="Exclude lowercase letters")
    parser.add_argument("--no-digits", action="store_false", dest="digits", help="Exclude digits")
    parser.add_argument("--no-symbols", action="store_false", dest="symbols", help="Exclude symbols")
    
    args = parser.parse_args()
    
    if args.length < 8:
        parser.error("Password length must be at least 8 characters")
    
    try:
        password = generate_password(
            args.length,
            uppercase=args.uppercase,
            lowercase=args.lowercase,
            digits=args.digits,
            symbols=args.symbols
        )
        print(f"Generated password: {password}")
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
