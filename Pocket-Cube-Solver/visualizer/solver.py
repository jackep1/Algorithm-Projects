from typing import List, Optional, Dict, Deque, Tuple
from collections import deque
import rubik

def count_inversions(perm: rubik.Permutation) -> int:
    inversions = 0
    for i in range(len(perm)):
        for j in range(i + 1, len(perm)):
            if perm[i] > perm[j]:
                inversions += 1
    return inversions

def is_solvable(position: rubik.Position) -> bool:
    inversions = count_inversions(position)
    return inversions % 2 == 0

def shortest_path(start: rubik.Position, end: rubik.Position) -> Optional[List[rubik.Permutation]]:
    # If already at target position, quit
    if start == end:
        return []
    if not is_solvable(start):
        return None

    # Initialization
    forward_queue: Deque[Tuple[rubik.Position, List[str]]] = deque([(start, [])])
    backward_queue: Deque[Tuple[rubik.Position, List[str]]] = deque([(end, [])])

    # Lists of visited positions
    forward_visited: Dict[rubik.Position, List[str]] = {start: []}
    backward_visited: Dict[rubik.Position, List[str]] = {end: []}

    def convert_to_permutation(move: str) -> rubik.Permutation:
        for key, value in rubik.quarter_twists_names.items():
            if value == move:
                return key

    # Helper function to perform one step of BFS
    def bfs_step(queue: Deque, visited: Dict, other_visited: Dict) -> Optional[List[str]]:
        current_position: rubik.Position
        path: List[str]
        current_position, path = queue.popleft()

        # Try each move for this position
        for move in rubik.quarter_twists:
            new_position = rubik.perm_apply(move, current_position)
            new_move_name = rubik.quarter_twists_names[move]  # Get the move name (character)

            # If this position has been visited from the other end, return the path
            if new_position in other_visited:
                # Reverse the path from the other end and append to the current path
                other_visited[new_position].reverse()
                key_perms = [convert_to_permutation(m) for m in other_visited[new_position]]
                inverse_moves = [rubik.perm_inverse(kp) for kp in key_perms]
                return path + [new_move_name] + [rubik.quarter_twists_names[i_move] for i_move in inverse_moves]

            # If we haven't been here, add it to the visited list
            if new_position not in visited:
                visited[new_position] = path + [new_move_name]
                queue.append((new_position, path + [new_move_name]))

        # If all moves are tried and there's no path, return None
        return None

    # Termination: BFS Loop
    while forward_queue and backward_queue:
        result = bfs_step(forward_queue, forward_visited, backward_visited)
        if result:
            return [convert_to_permutation(m) for m in result]  # Return the path as is

        result = bfs_step(backward_queue, backward_visited, forward_visited)
        if result:
            result.reverse()
            # Return the result with moves inverted, mapping inverses back to names
            return [rubik.perm_inverse(convert_to_permutation(m)) for m in result]

    # If no path is found, return None
    return None