import sys
import imagematrix

class ResizeableImage(imagematrix.ImageMatrix):
    def best_seam(self, dp=True):

        # Dynamic programming section
        if dp:
            energy = [[self.energy(col, row) for row in range(self.height)] for col in range(self.width)]
            table = [[0] * self.height for _ in range(self.width)]
            backtrack = [[0] * self.height for _ in range(self.width)]

            for col in range(self.width):
                table[col][self.height - 1] = energy[col][self.height - 1]

            for row in range(self.height - 2, -1, -1):
                for col in range(self.width):
                    best_choice = table[col][row + 1]
                    backtrack[col][row] = col
                    if col > 0 and table[col - 1][row + 1] < best_choice:
                        best_choice = table[col - 1][row + 1]
                        backtrack[col][row] = col - 1
                    if col < self.width - 1 and table[col + 1][row + 1] < best_choice:
                        best_choice = table[col + 1][row + 1]
                        backtrack[col][row] = col + 1
                    table[col][row] = energy[col][row] + best_choice

            min_energy = float('inf')
            min_col = 0
            for col in range(self.width):
                if table[col][0] < min_energy:
                    min_energy = table[col][0]
                    min_col = col

            path = []
            col = min_col
            for row in range(self.height):
                path.append((col, row))
                col = backtrack[col][row]

            return path

        # Naive recursive section
        else:
            sys.setrecursionlimit(10000)
            memo = {}
            def best_seam_from(col, row):
                # Check previous vals
                if (col, row) in memo:
                    return memo[(col, row)]

                # Base case: last row
                if row == self.height - 1:
                    return [(col, row)], self.energy(col, row)

                # Recursive case: find the best seam from each of the three possible next pixels
                neighbors = []
                if col > 0: # Down to the left
                    neighbors.append(best_seam_from(col - 1, row + 1))
                neighbors.append(best_seam_from(col, row + 1))
                if col < self.width - 1: # Down to the right
                    neighbors.append(best_seam_from(col + 1, row + 1))

                best_next_seam, best_next_energy = min(neighbors, key=lambda x: x[1])
                result = ([(col, row)] + best_next_seam, self.energy(col, row) + best_next_energy)
                memo[(col, row)] = result
                return result

            best_seam = None
            best_energy = float('inf')
            for col in range(self.width):
                seam, energy = best_seam_from(col, 0)
                if energy < best_energy:
                    best_seam = seam
                    best_energy = energy

            return best_seam





    def remove_best_seam(self):
        self.remove_seam(self.best_seam())
