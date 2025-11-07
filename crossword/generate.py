import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # cada variable (var) representa una posición vacía en el crucigrama
        # self.domains[var] es el conjunto de palabras posibles que podrían llenar ese espacio.

        for var in self.domains:
            # Usamos una copia del dominio para evitar modificar mientras iteramos
            for word in set(self.domains[var]):
                if len(word) != var.length: # cada palabra debe tener la misma longitud que la casilla.
                    self.domains[var].remove(word)


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        overlap = self.crossword.overlaps[x, y]   # devuelve la coordenada donde x e y intersectan

        
        if overlap is None:
            return False

        i, j = overlap

        # Para cada palabra de x, verificamos si existe alguna palabra en y que sea compatible
        to_remove = set()
        for word_x in set(self.domains[x]):
            match_found = False
            for word_y in self.domains[y]:
                if word_x[i] == word_y[j]:
                    match_found = True
                    break

            # Si no existe ninguna coincidencia, eliminamos word_x del dominio de x
            if not match_found: 
                to_remove.add(word_x)

        # Si se eliminaron palabras, marcamos revisión
        if to_remove:
            self.domains[x] -= to_remove
            revised = True

        return revised


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # Si no se pasa una lista de arcos, se crean todos los pares (x, y) donde x e y son neighbors
        if arcs is None:
            arcs = [
                (x, y)
                for x in self.crossword.variables
                for y in self.crossword.neighbors(x)
            ]

        # Se pone todo en una cola
        queue = list(arcs)

        # Mientras haya arcos por revisar
        while queue:
            (X, Y) = queue.pop(0)

            if self.revise(X, Y):
                # Si se deja vacío, no hay solución posible
                if len(self.domains[X]) == 0:
                    return False

                # Volvemos a añadir los vecinos de X (excepto Y)
                for Z in self.crossword.neighbors(X) - {Y}:
                    queue.append((Z, X))

        # Cuando la cola se vacía, significa que todos los arcos están consistentes
        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # Cada variable debe estar asignada

        # El crucigrama está completo si: Todas las variables están en el diccionario, y ninguna tiene valor None
        return all(
            var in assignment and assignment[var] is not None
            for var in self.crossword.variables)


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # 1️ Palabras únicas ( no se pueden repetir)
        words = list(assignment.values())
        if len(words) != len(set(words)):
            return False

        # 2️ Longitudes correctas y solapamientos coherentes
        for var, word in assignment.items():
            if len(word) != var.length: # cuando la longitud es distinta
                return False

            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    overlap = self.crossword.overlaps[var, neighbor]
                    if overlap is None:
                        continue
                    i, j = overlap
                    if word[i] != assignment[neighbor][j]: # cuando hay un conflicto de letras en cruces
                        return False

        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list should rule out the fewest.
        """
        # Ordena las palabras del dominio de var según cuántas opciones eliminan en los vecinos
        # Cuantas menos restricciones imponga, antes se prueba

        def conflicts(word):
            count = 0
            for neighbor in self.crossword.neighbors(var):
                if neighbor not in assignment:
                    overlap = self.crossword.overlaps[var, neighbor]
                    if overlap is None:
                        continue
                    i, j = overlap
                    for neighbor_word in self.domains[neighbor]:
                        if word[i] != neighbor_word[j]:
                            count += 1
            return count

        return sorted(self.domains[var], key=conflicts)


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If tie, choose the variable with the highest degree.
        """
        unassigned = [v for v in self.crossword.variables if v not in assignment]

        # Ordenamos con MRV primero
        # si hay empate, se elige la que tiene más vecinos
        
        def heuristic(v):
            return (len(self.domains[v]), -len(self.crossword.neighbors(v)))

        return min(unassigned, key=heuristic)


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible.
        """
        # Caso base: asignación completa
        if self.assignment_complete(assignment):
            return assignment

        # Elegimos variable no asignada
        var = self.select_unassigned_variable(assignment)

        # Intentamos cada palabra posible
        for value in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = value

            if self.consistent(new_assignment):
                # Aplicamos backtracking recursivo
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result

        # Ninguna opción funcionó
        return None

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
