import random
import json
import os
from datetime import datetime

DIFFS = {
    "easy":   {"range": 50,  "max": 15},
    "medium": {"range": 100, "max": 10},
    "hard":   {"range": 200, "max": 7},
}
HINT_PENALTY = 2
SCORES_FILE = "ng_scores.json"


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def load_scores():
    try:
        with open(SCORES_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_scores(scores):
    with open(SCORES_FILE, "w") as f:
        json.dump(scores, f, indent=2)


def add_score(scores, name, score, diff, target):
    scores.append({
        "name": name,
        "score": score,
        "diff": diff,
        "target": target,
        "date": datetime.now().strftime("%Y-%m-%d"),
    })
    scores.sort(key=lambda x: x["score"])
    return scores[:10]


def calc_score(attempts, hints, diff):
    modifiers = {"easy": 1.0, "medium": 0.8, "hard": 0.6}
    return round((attempts + hints * HINT_PENALTY) * modifiers[diff])


def get_hint(number, guesses, hints_used):
    options = [
        lambda: f"The number is {'even' if number % 2 == 0 else 'odd'}.",
        lambda: f"The sum of its digits is {sum(int(d) for d in str(number))}.",
        lambda: f"The number has {len(str(number))} digit(s).",
    ]
    for d in [2, 3, 5, 7]:
        if number % d == 0:
            options.append(lambda d=d: f"The number is divisible by {d}.")
            break
    if guesses:
        options.append(lambda: f"You are {abs(number - guesses[-1])} away from the number.")
    return random.choice(options)()


def warmth(diff, number, guess):
    d = abs(number - guess)
    if diff == "easy":
        if d <= 3: return " Very close!"
        if d <= 10: return " Getting warmer."
        if d <= 20: return " Getting there."
    elif diff == "medium":
        if d <= 5: return " Very close!"
        if d <= 15: return " Getting warmer."
        if d <= 30: return " Getting there."
    else:
        if d <= 10: return " Very close!"
        if d <= 30: return " Getting warmer."
        if d <= 60: return " Getting there."
    return ""


def show_progress(attempts, max_attempts, hints):
    filled = round((attempts / max_attempts) * 20)
    bar = "█" * filled + "░" * (20 - filled)
    print(f"\n  Attempts [{bar}] {attempts}/{max_attempts}   Hints used: {hints}")


def show_history(guesses, number):
    if not guesses:
        return
    chips = []
    for g in guesses:
        if g > number:
            chips.append(f"{g}↑")
        elif g < number:
            chips.append(f"{g}↓")
        else:
            chips.append(str(g))
    print("  History:", "  ".join(chips))


def choose_difficulty():
    while True:
        clear()
        print("\n  NUMBER GUESSER\n")
        print("  1. Easy    (1–50,  15 attempts)")
        print("  2. Medium  (1–100, 10 attempts)")
        print("  3. Hard    (1–200,  7 attempts)\n")
        choice = input("  Choose difficulty [1/2/3]: ").strip()
        if choice == "1": return "easy"
        if choice == "2": return "medium"
        if choice == "3": return "hard"
        print("  Invalid choice.")


def show_leaderboard(scores):
    clear()
    print("\n  LEADERBOARD  (lower score = better)\n")
    if not scores:
        print("  No scores yet.")
    else:
        print(f"  {'#':<4}{'Name':<16}{'Score':<8}{'Diff':<10}{'Target':<8}{'Date'}")
        print("  " + "-" * 52)
        for i, s in enumerate(scores, 1):
            print(f"  {i:<4}{s['name'][:15]:<16}{s['score']:<8}{s['diff']:<10}{s['target']:<8}{s['date']}")
    print()
    input("  Press Enter to continue...")


def play_round(diff, scores):
    cfg = DIFFS[diff]
    number = random.randint(1, cfg["range"])
    attempts = 0
    hints = 0
    guesses = []
    max_hints = 3

    clear()
    print(f"\n  Guess the number between 1 and {cfg['range']}.")
    print(f"  You have {cfg['max']} attempts.  Type 'hint' for a clue (costs {HINT_PENALTY} extra).\n")

    while attempts < cfg["max"]:
        show_progress(attempts, cfg["max"], hints)
        show_history(guesses, number)

        raw = input("\n  Your guess: ").strip().lower()

        if raw == "hint":
            if hints >= max_hints:
                print("  No more hints available.")
                continue
            hints += 1
            print(f"  Hint: {get_hint(number, guesses, hints)}")
            continue

        try:
            guess = int(raw)
        except ValueError:
            print("  Enter a valid number or 'hint'.")
            continue

        if guess < 1 or guess > cfg["range"]:
            print(f"  Number must be between 1 and {cfg['range']}.")
            continue

        attempts += 1
        guesses.append(guess)

        if guess == number:
            score = calc_score(attempts, hints, diff)
            clear()
            print(f"\n  You got it! The number was {number}.")
            print(f"  Attempts: {attempts}   Hints: {hints}   Score: {score}\n")
            name = input("  Enter your name for the leaderboard (or Enter to skip): ").strip()
            if name:
                scores = add_score(scores, name, score, diff, number)
                save_scores(scores)
                print("  Score saved.")
            return scores, True

        direction = "Too high." if guess > number else "Too low."
        print(f"  {direction}{warmth(diff, number, guess)}")

    clear()
    print(f"\n  Out of attempts. The number was {number}.\n")
    return scores, False


def main():
    scores = load_scores()

    while True:
        clear()
        print("\n  NUMBER GUESSER\n")
        print("  1. Play")
        print("  2. Leaderboard")
        print("  3. Quit\n")
        choice = input("  Choose [1/2/3]: ").strip()

        if choice == "1":
            diff = choose_difficulty()
            scores, _ = play_round(diff, scores)
            input("\n  Press Enter to return to menu...")
        elif choice == "2":
            show_leaderboard(scores)
        elif choice == "3":
            print("\n  Goodbye!\n")
            break
        else:
            print("  Invalid choice.")


if __name__ == "__main__":
    main()
