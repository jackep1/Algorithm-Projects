import sys
import timeit

def read_n_preferences(n, lines):
    """
    Reads n lines from file, interpreting each as an individual followed by the
    names of the individual's preferred partners in order. Aborts early if the
    number of preferences is incorrect, or if the preferences aren't unique.

    Parameters:
    n (int): Number of lines to read/preference lists to store
    file (file): The file from which to read

    Returns:
    preferences (dict): Keys as people, values as lists of their preferences
    """
    preferences = {}
    for _ in range(n):
        line = lines.pop(0).split()
        person, prefs = line[0], line[1:]
        if len(prefs) != n:
            sys.exit(1) # Exit if someone doesn't have exactly n preferences
        preferences[person] = prefs
    return preferences

# Function to parse the input from the file and extract preferences
def readfile(file_path):
    """
    Reads the input file and extracts the number of knights, knights' preferences, and ladies' preferences.

    Parameters:
    file_path (str): The path to the input file

    Returns:
    n (int): The number of knights (and ladies)
    knights_preferences (dict): The preferences of knights
    ladies_preferences (dict): The preferences of ladies
    """
    try:
        with open(file_path, 'r', encoding='latin-1') as f:
            lines = f.readlines()

        if len(lines) == 0:
            sys.exit(1)  # Invariant: The file should not be empty, so exit if no lines exist

        # The first line of the input file contains the number of knights (which equals the number of ladies)
        n = int(lines.pop(0).strip())

        # Invariant: The total number of lines should be exactly 2 * n
        # This accounts for 1 line with 'n' being popped, and n lines for knights and n lines for ladies
        if len(lines) != 2 * n:
            sys.exit(1)  # Exit if the line count does not match the expected number

        # Dictionaries to store the preferences of knights and ladies
        # Dictionaries used for easy access based on person's name
        knights_preferences = read_n_preferences(n, lines)
        ladies_preferences = read_n_preferences(n, lines)

        # Invariant: At this point, knights_preferences and ladies_preferences should both have 'n' entries
        assert len(knights_preferences) == n and len(ladies_preferences) == n
        assert len(knights_preferences) == len(set(knights_preferences)) and len(ladies_preferences) == len(set(ladies_preferences))
        return n, knights_preferences, ladies_preferences

    except:
        sys.exit(1)  # Invariant: The program should exit if any error occurs during file reading or parsing

# Gale-Shapley algorithm to solve the Stable Marriage Problem
# This algorithm ensures that all knights and ladies are paired in a stable way.
# Inspired by the explanation from GeeksforGeeks on the Stable Marriage Problem.
# https://www.geeksforgeeks.org/stable-marriage-problem/
def gale_shapley(n, knights_preferences, ladies_preferences):
    """
    Gale-Shapley algorithm to solve the Stable Marriage Problem.
    This algorithm ensures that all knights and ladies are paired in a stable way.

    Parameters:
    n (int): The number of knights (and ladies)
    knights_preferences (dict): The preferences of knights
    ladies_preferences (dict): The preferences of ladies

    Returns:
    None
    """
    # Dictionary to store current engagements (lady -> knight)
    # Dictionary chosen for easy access/checking if lady is engaged
    engagements = {}

    # Invariant: All knights are initially free and are ready to propose
    # List works fine for this purpose as we only need to keep track of free knights
    free_knights = list(knights_preferences.keys())

    # Continue until all knights are engaged
    while free_knights:
        # Invariant: At the beginning of each iteration, 'free_knights' contains only unengaged knights
        knight = free_knights.pop(0)  # Select a free knight

        # The knight proposes to ladies in order of preference
        for lady in knights_preferences[knight]:
            if lady not in engagements:
                # Invariant: If the lady is not engaged, she accepts the proposal immediately
                engagements[lady] = knight
                break
            else:
                current_knight = engagements[lady]
                # Invariant: The lady is already engaged, so she compares the current knight with the proposing knight
                # If the lady prefers this knight over her current engagement
                if ladies_preferences[lady].index(knight) < ladies_preferences[lady].index(current_knight):
                    # The lady breaks up with her current knight and engages the new knight
                    engagements[lady] = knight
                    # Invariant: The previously engaged knight becomes free again and is added back to the free_knights list
                    free_knights.append(current_knight)  # The dumped knight becomes free again
                    break

    # Invariant: After the while loop terminates, all knights must be engaged
    # Print the final pairings (knight -> lady) in the format "knight lady"
    for lady, knight in engagements.items():
        print(f"{knight} {lady}")

# Main function
if __name__ == "__main__":
    # Ensure exactly one argument is provided
    if len(sys.argv) != 2:
        sys.exit(1)  # Invariant: The program must exit if the input file is not provided

    input_file = sys.argv[1]

    # Parse the input to get n, knights' preferences, and ladies' preferences
    n, knights_preferences, ladies_preferences = readfile(input_file)

    # call Gale-Shapley algorithm
    execution_time = timeit.timeit(lambda: gale_shapley(n, knights_preferences, ladies_preferences), number=1)
    print(f"Execution time: {execution_time:.6f} seconds", file=sys.stderr)