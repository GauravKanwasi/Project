import random

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

# Dictionary of move functions
moves_dict = {
    'F': turn_F_clockwise,
    'U': turn_U_clockwise,
    'R': turn_R_clockwise,
    'L': turn_L_clockwise,
    'B': turn_B_clockwise,
    'D': turn_D_clockwise
}

# Function to display the cube in a net format
def display_cube(cube):
    print('    ', ' '.join(cube['U'][0]))
    print('    ', ' '.join(cube['U'][1]))
    print('    ', ' '.join(cube['U'][2]))
    for i in range(3):
        print(' '.join(cube['L'][i]), ' '.join(cube['F'][i]), ' '.join(cube['R'][i]), ' '.join(cube['B'][i]))
    print('    ', ' '.join(cube['D'][0]))
    print('    ', ' '.join(cube['D'][1]))
    print('    ', ' '.join(cube['D'][2]))

# Main interactive loop
def main():
    cube = create_solved_cube()
    basic_moves = ['F', 'U', 'R', 'L', 'B', 'D']
    
    while True:
        display_cube(cube)
        command = input("\nEnter move (e.g., F, U', R2), 'scramble', 'reset', 'solve', or 'quit': ").strip()
        
        if command == 'quit':
            print("Goodbye!")
            break
        elif command == 'reset':
            cube = create_solved_cube()
            print("Cube reset to solved state.")
        elif command == 'scramble':
            scramble_moves = [random.choice(basic_moves) for _ in range(20)]
            for move in scramble_moves:
                cube = moves_dict[move](cube)
            print("Cube scrambled.")
        elif command == 'solve':
            print("Solver not implemented yet. Here's a hint: Try solving the bottom cross first!")
            # Future implementation can go here
        else:
            # Parse the move
            if command in moves_dict:
                cube = moves_dict[command](cube)
            elif len(command) == 2 and command[0] in moves_dict and command[1] == "'":
                move = command[0]
                # Counterclockwise = 3 clockwise turns
                for _ in range(3):
                    cube = moves_dict[move](cube)
            elif len(command) == 2 and command[0] in moves_dict and command[1] == '2':
                move = command[0]
                # 180 degrees = 2 clockwise turns
                for _ in range(2):
                    cube = moves_dict[move](cube)
            else:
                print("Invalid command. Use moves like F, U', R2, or commands like scramble/reset/quit/solve.")
        print()  # Add a newline for smooth readability

if __name__ == "__main__":
    main()
