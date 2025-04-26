import random

# Welcome message and game instructions
print("Welcome to the number guessing game!")
print("I'm thinking of a number between 1 and 100.")
print("Try to guess it in as few attempts as possible.")

# Generate a random number between 1 and 100
number = random.randint(1, 100)

# Initialize the attempt counter
attempts = 0

# Main game loop
while True:
    # Get the player's guess
    guess = input("Guess a number between 1 and 100: ")
    
    # Try to convert the input to an integer and handle invalid inputs
    try:
        guess = int(guess)
        attempts += 1  # Increment attempts for each valid guess
    except ValueError:
        print("Please enter a valid number.")
        continue  # Skip to the next iteration if input is invalid
    
    # Check the guess and provide feedback
    if guess == number:
        print("Congratulations! You guessed it.")
        print(f"It took you {attempts} attempts to guess the number.")
        break  # Exit the loop when the correct number is guessed
    elif guess > number:
        print("Too high.")
    else:
        print("Too low.")
