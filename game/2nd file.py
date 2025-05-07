import random
import os
import time
from datetime import datetime

class NumberGuessingGame:
    def __init__(self):
        self.high_scores = []
        self.load_high_scores()
        self.max_attempts = {
            'easy': 15,
            'medium': 10,
            'hard': 7
        }
        self.range_by_difficulty = {
            'easy': 50,
            'medium': 100,
            'hard': 200
        }
        self.hint_penalty = 2

    def clear_screen(self):
        """Clear the console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def load_high_scores(self):
        """Load high scores from file if it exists."""
        try:
            with open("number_game_scores.txt", "r") as file:
                for line in file:
                    parts = line.strip().split(',')
                    if len(parts) == 5:
                        name, score, difficulty, date, target = parts
                        self.high_scores.append({
                            'name': name,
                            'score': int(score),
                            'difficulty': difficulty,
                            'date': date,
                            'target': int(target)
                        })
        except FileNotFoundError:
            # No scores file exists yet
            pass

    def save_high_scores(self):
        """Save high scores to file."""
        with open("number_game_scores.txt", "w") as file:
            for score in self.high_scores:
                file.write(f"{score['name']},{score['score']},{score['difficulty']},{score['date']},{score['target']}\n")

    def add_high_score(self, name, score, difficulty, target):
        """Add a new high score to the list."""
        today = datetime.now().strftime("%Y-%m-%d")
        self.high_scores.append({
            'name': name,
            'score': score,
            'difficulty': difficulty,
            'date': today,
            'target': target
        })
        # Sort high scores by score (lower is better)
        self.high_scores = sorted(self.high_scores, key=lambda x: x['score'])[:10]
        self.save_high_scores()

    def display_high_scores(self):
        """Display the high scores table."""
        self.clear_screen()
        print("\n🏆 HIGH SCORES 🏆")
        print("="*50)
        print(f"{'Rank':<5}{'Name':<15}{'Score':<8}{'Difficulty':<10}{'Date':<12}{'Target':<6}")
        print("-"*50)
        
        if not self.high_scores:
            print("No high scores yet!")
        else:
            for i, score in enumerate(self.high_scores[:10], 1):
                print(f"{i:<5}{score['name'][:14]:<15}{score['score']:<8}{score['difficulty']:<10}{score['date']:<12}{score['target']:<6}")
        
        print("="*50)
        input("\nPress Enter to continue...")

    def calculate_score(self, attempts, max_attempts, hints_used, difficulty):
        """Calculate score based on attempts, hints used and difficulty."""
        # Base score is the attempts taken
        score = attempts
        
        # Add penalty for hints
        score += hints_used * self.hint_penalty
        
        # Apply difficulty modifier (harder difficulties get more points for same performance)
        difficulty_modifier = {'easy': 1.0, 'medium': 0.8, 'hard': 0.6}
        score = int(score * difficulty_modifier[difficulty])
        
        return score

    def get_hint(self, number, guesses, difficulty):
        """Provide a hint based on previous guesses and difficulty."""
        if not guesses:
            return "Make your first guess to get a hint!"
        
        hint_type = random.randint(1, 5)
        
        if hint_type == 1:
            # Divisibility hint
            divisors = [2, 3, 5]
            divisor = random.choice(divisors)
            if number % divisor == 0:
                return f"The number is divisible by {divisor}."
            else:
                return f"The number is not divisible by {divisor}."
                
        elif hint_type == 2:
            # Digit sum hint
            digit_sum = sum(int(digit) for digit in str(number))
            return f"The sum of the digits is {digit_sum}."
            
        elif hint_type == 3:
            # Distance hint
            last_guess = guesses[-1]
            distance = abs(number - last_guess)
            
            if difficulty == 'easy':
                return f"You are {distance} away from the number."
            elif difficulty == 'medium':
                if distance <= 5:
                    return "You are very close! (Within 5)"
                elif distance <= 15:
                    return "You are getting close! (Within 15)"
                else:
                    return "You are still quite far from the number."
            else:  # hard
                if distance <= 10:
                    return "You are somewhat close."
                else:
                    return "You are not close yet."
                    
        elif hint_type == 4:
            # Even/Odd hint
            if number % 2 == 0:
                return "The number is even."
            else:
                return "The number is odd."
                
        elif hint_type == 5:
            # Digit length hint
            return f"The number has {len(str(number))} digit(s)."

    def print_progress(self, attempts, max_attempts, hints_used):
        """Display progress bar and stats."""
        progress = attempts / max_attempts
        bar_length = 20
        filled_length = int(bar_length * progress)
        
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        print(f"\nAttempts: {attempts}/{max_attempts} [{bar}] Hints used: {hints_used}")

    def print_welcome(self):
        """Display welcome message and game title."""
        self.clear_screen()
        print("""
        ╔═══════════════════════════════════════════════╗
        ║                                               ║
        ║   NUMBER GUESSING GAME - ENHANCED EDITION     ║
        ║                                               ║
        ╚═══════════════════════════════════════════════╝
        """)
        
    def choose_difficulty(self):
        """Let the player choose a difficulty level."""
        while True:
            self.clear_screen()
            print("""
            Choose a difficulty level:
            
            1. Easy   (1-50, 15 attempts)
            2. Medium (1-100, 10 attempts)
            3. Hard   (1-200, 7 attempts)
            """)
            
            choice = input("Enter your choice (1-3): ")
            
            if choice == '1':
                return 'easy'
            elif choice == '2':
                return 'medium'
            elif choice == '3':
                return 'hard'
            else:
                print("Invalid choice. Please try again.")
                time.sleep(1)

    def play_game(self):
        """Main game loop."""
        play_again = True
        
        while play_again:
            self.print_welcome()
            time.sleep(1)
            
            difficulty = self.choose_difficulty()
            number_range = self.range_by_difficulty[difficulty]
            max_attempts = self.max_attempts[difficulty]
            
            # Generate a random number
            number = random.randint(1, number_range)
            
            self.clear_screen()
            print(f"\nI'm thinking of a number between 1 and {number_range}.")
            print(f"You have {max_attempts} attempts to guess it.")
            print("Type 'hint' to get a hint (costs 2 extra attempts).")
            print("Let's begin!\n")
            
            attempts = 0
            hints_used = 0
            guesses = []
            
            while attempts < max_attempts:
                self.print_progress(attempts, max_attempts, hints_used)
                
                guess_input = input("\nEnter your guess (or 'hint'): ")
                
                if guess_input.lower() == 'hint':
                    hints_used += 1
                    hint = self.get_hint(number, guesses, difficulty)
                    print(f"HINT: {hint}")
                    continue
                
                try:
                    guess = int(guess_input)
                    attempts += 1
                    guesses.append(guess)
                    
                    if guess < 1 or guess > number_range:
                        print(f"Please enter a number between 1 and {number_range}.")
                        attempts -= 1  # Don't count invalid guesses
                        guesses.pop()  # Remove invalid guess
                        continue
                    
                    if guess == number:
                        self.clear_screen()
                        print("\n🎉 CONGRATULATIONS! 🎉")
                        print(f"You guessed the number {number} in {attempts} attempts!")
                        
                        score = self.calculate_score(attempts, max_attempts, hints_used, difficulty)
                        print(f"Your score: {score} (lower is better)")
                        
                        name = input("Enter your name for the high score table: ")
                        if name.strip():
                            self.add_high_score(name, score, difficulty, number)
                        
                        break
                    elif guess > number:
                        print("📉 Too high!")
                    else:
                        print("📈 Too low!")
                        
                except ValueError:
                    print("Please enter a valid number.")
            
            if attempts >= max_attempts:
                print(f"\n😢 Sorry, you've used all {max_attempts} attempts.")
                print(f"The number was {number}.")
            
            while True:
                choice = input("\nDo you want to play again? (y/n): ")
                if choice.lower() in ['y', 'yes']:
                    play_again = True
                    break
                elif choice.lower() in ['n', 'no']:
                    play_again = False
                    break
                else:
                    print("Please enter 'y' or 'n'.")
            
            # Show high scores after each game
            self.display_high_scores()
        
        print("\nThanks for playing! Goodbye!")


if __name__ == "__main__":
    game = NumberGuessingGame()
    game.play_game()
