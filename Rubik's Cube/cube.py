import random
import os
import time
from collections import deque

# ============================================================
# ANSI COLORS FOR TERMINAL DISPLAY
# ============================================================

COLORS = {
    'R': '\033[41m R \033[0m',
    'O': '\033[48;5;208m O \033[0m',
    'G': '\033[42m G \033[0m',
    'B': '\033[44m B \033[0m',
    'W': '\033[107m W \033[0m',
    'Y': '\033[103m Y \033[0m',
}

# ============================================================
# CREATE SOLVED CUBE
# ============================================================

def create_cube():

    return {
        'F': [['R'] * 3 for _ in range(3)],
        'B': [['O'] * 3 for _ in range(3)],
        'L': [['G'] * 3 for _ in range(3)],
        'R': [['B'] * 3 for _ in range(3)],
        'U': [['W'] * 3 for _ in range(3)],
        'D': [['Y'] * 3 for _ in range(3)]
    }

# ============================================================
# ROTATE FACE CLOCKWISE
# ============================================================

def rotate_face(face):

    return [list(row) for row in zip(*face[::-1])]

# ============================================================
# COPY CUBE SAFELY
# ============================================================

def copy_cube(cube):

    return {
        face: [row[:] for row in cube[face]]
        for face in cube
    }

# ============================================================
# FRONT MOVE
# ============================================================

def move_F(cube):

    cube = copy_cube(cube)

    cube['F'] = rotate_face(cube['F'])

    top = cube['U'][2][:]

    cube['U'][2] = [
        cube['L'][2][2],
        cube['L'][1][2],
        cube['L'][0][2]
    ]

    cube['L'][0][2] = cube['D'][0][0]
    cube['L'][1][2] = cube['D'][0][1]
    cube['L'][2][2] = cube['D'][0][2]

    cube['D'][0] = [
        cube['R'][2][0],
        cube['R'][1][0],
        cube['R'][0][0]
    ]

    cube['R'][0][0] = top[0]
    cube['R'][1][0] = top[1]
    cube['R'][2][0] = top[2]

    return cube

# ============================================================
# UP MOVE
# ============================================================

def move_U(cube):

    cube = copy_cube(cube)

    cube['U'] = rotate_face(cube['U'])

    temp = cube['F'][0][:]

    cube['F'][0] = cube['L'][0][:]
    cube['L'][0] = cube['B'][0][:]
    cube['B'][0] = cube['R'][0][:]
    cube['R'][0] = temp

    return cube

# ============================================================
# RIGHT MOVE
# ============================================================

def move_R(cube):

    cube = copy_cube(cube)

    cube['R'] = rotate_face(cube['R'])

    temp = [cube['U'][i][2] for i in range(3)]

    for i in range(3):
        cube['U'][i][2] = cube['B'][2 - i][0]
        cube['B'][2 - i][0] = cube['D'][i][2]
        cube['D'][i][2] = cube['F'][i][2]
        cube['F'][i][2] = temp[i]

    return cube

# ============================================================
# LEFT MOVE
# ============================================================

def move_L(cube):

    cube = copy_cube(cube)

    cube['L'] = rotate_face(cube['L'])

    temp = [cube['U'][i][0] for i in range(3)]

    for i in range(3):
        cube['U'][i][0] = cube['B'][2 - i][2]
        cube['B'][2 - i][2] = cube['D'][i][0]
        cube['D'][i][0] = cube['F'][i][0]
        cube['F'][i][0] = temp[i]

    return cube

# ============================================================
# BACK MOVE
# ============================================================

def move_B(cube):

    cube = copy_cube(cube)

    cube['B'] = rotate_face(cube['B'])

    top = cube['U'][0][:]

    cube['U'][0] = [
        cube['L'][2][0],
        cube['L'][1][0],
        cube['L'][0][0]
    ]

    cube['L'][0][0] = cube['D'][2][2]
    cube['L'][1][0] = cube['D'][2][1]
    cube['L'][2][0] = cube['D'][2][0]

    cube['D'][2] = [
        cube['R'][2][2],
        cube['R'][1][2],
        cube['R'][0][2]
    ]

    cube['R'][0][2] = top[2]
    cube['R'][1][2] = top[1]
    cube['R'][2][2] = top[0]

    return cube

# ============================================================
# DOWN MOVE
# ============================================================

def move_D(cube):

    cube = copy_cube(cube)

    cube['D'] = rotate_face(cube['D'])

    temp = cube['F'][2][:]

    cube['F'][2] = cube['L'][2][:]
    cube['L'][2] = cube['B'][2][:]
    cube['B'][2] = cube['R'][2][:]
    cube['R'][2] = temp

    return cube

# ============================================================
# GENERATE COUNTER CLOCKWISE MOVE
# ============================================================

def reverse_move(move_function, cube):

    for _ in range(3):
        cube = move_function(cube)

    return cube

# ============================================================
# ALL MOVES
# ============================================================

MOVES = {
    'F': move_F,
    "F'": lambda c: reverse_move(move_F, c),

    'U': move_U,
    "U'": lambda c: reverse_move(move_U, c),

    'R': move_R,
    "R'": lambda c: reverse_move(move_R, c),

    'L': move_L,
    "L'": lambda c: reverse_move(move_L, c),

    'B': move_B,
    "B'": lambda c: reverse_move(move_B, c),

    'D': move_D,
    "D'": lambda c: reverse_move(move_D, c)
}

# ============================================================
# DISPLAY CUBE
# ============================================================

def display_cube(cube, move_count, elapsed):

    os.system('cls' if os.name == 'nt' else 'clear')

    print("=" * 60)
    print("           ADVANCED RUBIK'S CUBE SIMULATOR")
    print("=" * 60)

    print(f"\nMoves Played : {move_count}")
    print(f"Time Elapsed : {elapsed:.2f} seconds\n")

    print("                 UP")

    for row in cube['U']:
        print("          ", end="")
        for cell in row:
            print(COLORS[cell], end=" ")
        print()

    print("\nLEFT        FRONT       RIGHT       BACK")

    for i in range(3):

        for face in ['L', 'F', 'R', 'B']:

            for cell in cube[face][i]:
                print(COLORS[cell], end=" ")

            print("   ", end="")

        print()

    print("\n                DOWN")

    for row in cube['D']:
        print("          ", end="")
        for cell in row:
            print(COLORS[cell], end=" ")
        print()

# ============================================================
# CHECK IF CUBE IS SOLVED
# ============================================================

def is_solved(cube):

    for face in cube:

        first = cube[face][0][0]

        for row in cube[face]:
            for cell in row:
                if cell != first:
                    return False

    return True

# ============================================================
# GENERATE SCRAMBLE
# ============================================================

def generate_scramble(length=25):

    possible = list(MOVES.keys())

    return [random.choice(possible) for _ in range(length)]

# ============================================================
# HELP MENU
# ============================================================

def show_help():

    print("\nAVAILABLE COMMANDS")
    print("-" * 30)

    print("Moves:")
    print("F  F'  U  U'  R  R'")
    print("L  L'  B  B'  D  D'")

    print("\nOther Commands:")
    print("scramble  -> Shuffle cube")
    print("reset     -> Reset cube")
    print("undo      -> Undo moves")
    print("history   -> Show move history")
    print("solve     -> Auto reverse scramble")
    print("help      -> Show commands")
    print("quit      -> Exit program")

# ============================================================
# MAIN APPLICATION
# ============================================================

def main():

    cube = create_cube()

    history = deque(maxlen=200)

    scramble_sequence = []

    move_count = 0

    start_time = time.time()

    print("Loading Rubik's Cube Simulator...")

    time.sleep(1)

    while True:

        elapsed = time.time() - start_time

        display_cube(cube, move_count, elapsed)

        if is_solved(cube):
            print("\nCube Status : SOLVED")
        else:
            print("\nCube Status : MIXED")

        command = input("\nEnter Command : ").strip()

        if not command:
            continue

        # ====================================================
        # EXIT PROGRAM
        # ====================================================

        if command == "quit":

            print("\nThanks for using the simulator!")
            break

        # ====================================================
        # HELP MENU
        # ====================================================

        elif command == "help":

            show_help()

            input("\nPress Enter to continue...")

        # ====================================================
        # RESET CUBE
        # ====================================================

        elif command == "reset":

            cube = create_cube()

            history.clear()

            scramble_sequence.clear()

            move_count = 0

            print("\nCube reset complete.")

            time.sleep(1)

        # ====================================================
        # SCRAMBLE
        # ====================================================

        elif command == "scramble":

            scramble_sequence = generate_scramble()

            for move in scramble_sequence:
                cube = MOVES[move](cube)

            history.append(scramble_sequence)

            move_count += len(scramble_sequence)

            print("\nCube scrambled successfully.")

            time.sleep(1)

        # ====================================================
        # SOLVE
        # ====================================================

        elif command == "solve":

            if scramble_sequence:

                reverse = []

                for move in reversed(scramble_sequence):

                    if "'" in move:
                        reverse.append(move[0])
                    else:
                        reverse.append(move + "'")

                for move in reverse:
                    cube = MOVES[move](cube)

                move_count += len(reverse)

                scramble_sequence.clear()

                print("\nCube solved.")

            else:
                print("\nNo scramble history found.")

            time.sleep(1)

        # ====================================================
        # HISTORY
        # ====================================================

        elif command == "history":

            print("\nMove History")
            print("-" * 30)

            if history:

                for i, item in enumerate(history, 1):
                    print(f"{i}. {' '.join(item)}")

            else:
                print("No history available.")

            input("\nPress Enter to continue...")

        # ====================================================
        # UNDO LAST ACTION
        # ====================================================

        elif command == "undo":

            if history:

                last_moves = history.pop()

                reverse = []

                for move in reversed(last_moves):

                    if "'" in move:
                        reverse.append(move[0])
                    else:
                        reverse.append(move + "'")

                for move in reverse:
                    cube = MOVES[move](cube)

                move_count += len(reverse)

                print("\nUndo successful.")

            else:
                print("\nNothing to undo.")

            time.sleep(1)

        # ====================================================
        # PROCESS NORMAL MOVES
        # ====================================================

        else:

            user_moves = command.split()

            valid_moves = []

            invalid = False

            for move in user_moves:

                if move in MOVES:

                    cube = MOVES[move](cube)

                    valid_moves.append(move)

                    move_count += 1

                else:

                    print(f"\nInvalid move : {move}")

                    invalid = True

                    break

            if not invalid and valid_moves:
                history.append(valid_moves)

# ============================================================
# START PROGRAM
# ============================================================

if __name__ == "__main__":
    main()
