import random
import os
from collections import deque

# ANSI color codes for cube faces
COLORS = {
    'R': '\033[41m R \033[0m',  # Red background
    'O': '\033[48;5;208m O \033[0m',  # Orange
    'G': '\033[42m G \033[0m',  # Green
    'B': '\033[44m B \033[0m',  # Blue
    'W': '\033[107m W \033[0m',  # White
    'Y': '\033[103m Y \033[0m',  # Yellow
}

# Function to create a solved Rubik's Cube
def create_solved_cube():
    return {
        'F': [['R']*3 for _ in range(3)],  # Front: Red
        'B': [['O']*3 for _ in range(3)],  # Back: Orange
        'L': [['G']*3 for _ in range(3)],  # Left: Green
        'R': [['B']*3 for _ in range(3)],  # Right: Blue
        'U': [['W']*3 for _ in range(3)],  # Up: White
        'D': [['Y']*3 for _ in range(3)]   # Down: Yellow
    }

# Helper function to rotate a face clockwise
def rotate_face_clockwise(face):
    return [list(row) for row in zip(*face[::-1])]

# Move functions for clockwise turns
def turn_F_clockwise(cube):
    new_cube = {face: [row[:] for row in cube[face]] for face in cube}
    new_cube['F'] = rotate_face_clockwise(cube['F'])
    temp = cube['U'][2][:]
    new_cube['U'][2][:] = [cube['L'][2][2], cube['L'][1][2], cube['L'][0][2]]
    new_cube['L'][0][2] = cube['D'][0][2]
    new_cube['L'][1][2] = cube['D'][0][1]
    new_cube['L'][2][2] = cube['D'][0][0]
    new_cube['D'][0][:] = [cube['R'][2][0], cube['R'][1][0], cube['R'][0][0]]
    new_cube['R'][0][0] = temp[0]
    new_cube['R'][1][0] = temp[1]
    new_cube['R'][2][0] = temp[2]
    return new_cube

def turn_U_clockwise(cube):
    new_cube = {face: [row[:] for row in cube[face]] for face in cube}
    new_cube['U'] = rotate_face_clockwise(cube['U'])
    temp = cube['F'][0][:]
    new_cube['F'][0][:] = cube['L'][0][:]
    new_cube['L'][0][:] = cube['B'][0][:]
    new_cube['B'][0][:] = cube['R'][0][:]
    new_cube['R'][0][:] = temp
    return new_cube

def turn_R_clockwise(cube):
    new_cube = {face: [row[:] for row in cube[face]] for face in cube}
    new_cube['R'] = rotate_face_clockwise(cube['R'])
    temp = [cube['U'][i][2] for i in range(3)]
    new_cube['U'][0][2] = cube['B'][2][0]
    new_cube['U'][1][2] = cube['B'][1][0]
    new_cube['U'][2][2] = cube['B'][0][0]
    new_cube['B'][0][0] = cube['D'][2][2]
    new_cube['B'][1][0] = cube['D'][1][2]
    new_cube['B'][2][0] = cube['D'][0][2]
    new_cube['D'][0][2] = cube['F'][0][2]
    new_cube['D'][1][2] = cube['F'][1][2]
    new_cube['D'][2][2] = cube['F'][2][2]
    new_cube['F'][0][2] = temp[0]
    new_cube['F'][1][2] = temp[1]
    new_cube['F'][2][2] = temp[2]
    return new_cube

def turn_L_clockwise(cube):
    new_cube = {face: [row[:] for row in cube[face]] for face in cube}
    new_cube['L'] = rotate_face_clockwise(cube['L'])
    temp = [cube['U'][i][0] for i in range(3)]
    new_cube['U'][0][0] = cube['B'][2][2]
    new_cube['U'][1][0] = cube['B'][1][2]
    new_cube['U'][2][0] = cube['B'][0][2]
    new_cube['B'][0][2] = cube['D'][2][0]
    new_cube['B'][1][2] = cube['D'][1][0]
    new_cube['B'][2][2] = cube['D'][0][0]
    new_cube['D'][0][0] = cube['F'][0][0]
    new_cube['D'][1][0] = cube['F'][1][0]
    new_cube['D'][2][0] = cube['F'][2][0]
    new_cube['F'][0][0] = temp[0]
    new_cube['F'][1][0] = temp[1]
    new_cube['F'][2][0] = temp[2]
    return new_cube

def turn_B_clockwise(cube):
    new_cube = {face: [row[:] for row in cube[face]] for face in cube}
    new_cube['B'] = rotate_face_clockwise(cube['B'])
    temp = cube['U'][0][:]
    new_cube['U'][0][:] = [cube['L'][2][0], cube['L'][1][0], cube['L'][0][0]]
    new_cube['L'][0][0] = cube['D'][2][2]
    new_cube['L'][1][0] = cube['D'][2][1]
    new_cube['L'][2][0] = cube['D'][2][0]
    new_cube['D'][2][:] = [cube['R'][2][2], cube['R'][1][2], cube['R'][0][2]]
    new_cube['R'][0][2] = temp[2]
    new_cube['R'][1][2] = temp[1]
    new_cube['R'][2][2] = temp[0]
    return new_cube

def turn_D_clockwise(cube):
    new_cube = {face: [row[:] for row in cube[face]] for face in cube}
    new_cube['D'] = rotate_face_clockwise(cube['D'])
    temp = cube['F'][2][:]
    new_cube['F'][2][:] = cube['L'][2][:]
    new_cube['L'][2][:] = cube['B'][2][:]
    new_cube['B'][2][:] = cube['R'][2][:]
    new_cube['R'][2][:] = temp
    return new_cube

# Create inverse moves using clockwise rotations
def turn_F_counter(cube):
    for _ in range(3): cube = turn_F_clockwise(cube)
    return cube

def turn_U_counter(cube):
    for _ in range(3): cube = turn_U_clockwise(cube)
    return cube

def turn_R_counter(cube):
    for _ in range(3): cube = turn_R_clockwise(cube)
    return cube

def turn_L_counter(cube):
    for _ in range(3): cube = turn_L_clockwise(cube)
    return cube

def turn_B_counter(cube):
    for _ in range(3): cube = turn_B_clockwise(cube)
    return cube

def turn_D_counter(cube):
    for _ in range(3): cube = turn_D_clockwise(cube)
    return cube

# Dictionary of all move functions
moves_dict = {
    'F': turn_F_clockwise,
    "F'": turn_F_counter,
    'U': turn_U_clockwise,
    "U'": turn_U_counter,
    'R': turn_R_clockwise,
    "R'": turn_R_counter,
    'L': turn_L_clockwise,
    "L'": turn_L_counter,
    'B': turn_B_clockwise,
    "B'": turn_B_counter,
    'D': turn_D_clockwise,
    "D'": turn_D_counter
}

# Function to display the cube in a net format with colors
def display_cube(cube):
    os.system('cls' if os.name == 'nt' else 'clear')
    print("          UP")
    for i in range(3):
        print("    ", end="")
        for j in range(3):
            print(COLORS[cube['U'][i][j]], end=" ")
        print()
    print()
    
    print("LEFT     FRONT    RIGHT    BACK")
    for i in range(3):
        for face in ['L', 'F', 'R', 'B']:
            for j in range(3):
                print(COLORS[cube[face][i][j]], end=" ")
            print("  ", end="")
        print()
    print()
    
    print("         DOWN")
    for i in range(3):
        print("    ", end="")
        for j in range(3):
            print(COLORS[cube['D'][i][j]], end=" ")
        print()

# Display available commands
def show_help():
    print("\nAVAILABLE COMMANDS:")
    print("Moves: F, F', U, U', R, R', L, L', B, B', D, D'")
    print("Multiple moves: F U R' (space separated)")
    print("Scramble: 'scramble'")
    print("Reset: 'reset'")
    print("Undo: 'undo'")
    print("History: 'history'")
    print("Solve: 'solve'")
    print("Help: 'help'")
    print("Quit: 'quit'")

# Generate a random scramble sequence
def generate_scramble(length=20):
    moves = ['F', "F'", 'U', "U'", 'R', "R'", 'L', "L'", 'B', "B'", 'D', "D'"]
    return [random.choice(moves) for _ in range(length)]

# Main interactive loop
def main():
    cube = create_solved_cube()
    history = deque(maxlen=100)
    scramble_moves = []
    
    print("Welcome to the Enhanced Rubik's Cube Simulator!")
    print("Type 'help' for available commands")
    
    while True:
        display_cube(cube)
        command = input("\nEnter command: ").strip()
        
        if not command:
            continue
            
        if command == 'quit':
            print("Goodbye!")
            break
            
        elif command == 'reset':
            cube = create_solved_cube()
            history.clear()
            scramble_moves = []
            print("Cube reset to solved state.")
            
        elif command == 'scramble':
            scramble_moves = generate_scramble()
            history.append(("scramble", scramble_moves))
            for move in scramble_moves:
                cube = moves_dict[move](cube)
            print(f"Cube scrambled with {len(scramble_moves)} moves.")
            
        elif command == 'solve':
            if scramble_moves:
                solve_moves = []
                for move in reversed(scramble_moves):
                    if "'" in move:
                        solve_moves.append(move[0])
                    else:
                        solve_moves.append(move + "'")
                
                for move in solve_moves:
                    cube = moves_dict[move](cube)
                history.append(("solve", solve_moves))
                scramble_moves = []
                print("Cube solved by reversing scramble sequence.")
            else:
                print("No scramble sequence to solve!")
                
        elif command == 'undo':
            if history:
                action, moves = history.pop()
                if action == "scramble":
                    solve_moves = []
                    for move in reversed(moves):
                        if "'" in move:
                            solve_moves.append(move[0])
                        else:
                            solve_moves.append(move + "'")
                    
                    for move in solve_moves:
                        cube = moves_dict[move](cube)
                    print(f"Undid scramble of {len(moves)} moves.")
                elif action == "moves":
                    for move in reversed(moves):
                        if "'" in move:
                            cube = moves_dict[move[0]](cube)
                        else:
                            cube = moves_dict[move + "'"](cube)
                    print(f"Undid {len(moves)} moves.")
            else:
                print("Nothing to undo!")
                
        elif command == 'history':
            if history:
                print("\nMove History:")
                for i, (action, moves) in enumerate(history, 1):
                    if action == "scramble":
                        print(f"{i}. Scramble: {' '.join(moves)}")
                    elif action == "moves":
                        print(f"{i}. Moves: {' '.join(moves)}")
            else:
                print("No history available")
                
        elif command == 'help':
            show_help()
            
        else:
            # Process multiple moves
            moves_list = command.split()
            valid_moves = []
            invalid = False
            
            for move in moves_list:
                if move in moves_dict:
                    valid_moves.append(move)
                    cube = moves_dict[move](cube)
                else:
                    print(f"Invalid move: {move}")
                    invalid = True
                    break
                    
            if not invalid and valid_moves:
                history.append(("moves", valid_moves))

if __name__ == "__main__":
    main()
