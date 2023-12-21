import functools
import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if self.count == len(self.cells) and self.count > 0:
            return self.cells

        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell not in self.cells:
            self.count += 1
            self.cells.add(cell)

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def get_surrounding_cells(self, cell):
        """
        Get surrounding cells withing the grid based on the specified cell that
        are not currently known if they are a mine or safe cell. Knowledge will
        be used to deduce the state of the cell
        """

        (row, col) = cell

        row1 = row - 1 if row > 0 else 0
        row2 = row + 1 if row < self.height - 1 else self.height - 1

        col1 = col - 1 if col > 0 else 0
        col2 = col + 1 if col < self.width - 1 else self.width - 1

        cells = set()
        for i in range(row1, row2 + 1, 1):
            for j in range(col1, col2 + 1, 1):
                surrounding_cell = (i, j)
                if surrounding_cell != cell and surrounding_cell not in self.safes:
                    cells.add(surrounding_cell)

        return cells

    def log_minefield(self, grid, title):
        print()
        print(f"==> {title}")
        print(f"\t##", end="")
        for x in range(0, self.width):
            print(f"{x}", end="|")
        print()
        print("\t" + "-" * ((self.width * 2) + 3))
        for y in range(0, self.height):
            print(f"\t{y}|", end="")
            for x in range(0, self.width):
                print(f"{grid[y][x]}", end="|")
            print()

    def log_knowledge(self):

        grid = [['-'] * self.width for i in range(self.height)]

        for sentence in self.knowledge:
            for cell in sentence.cells:
                (y, x) = cell
                if grid[y][x] == "-":
                    grid[y][x] = sentence.count

            for cell in sentence.known_safes():
                (y, x) = cell
                grid[y][x] = "S"
            for cell in sentence.known_mines():
                (y, x) = cell
                grid[y][x] = "M"

        self.log_minefield(grid, "KNOWLEDGE")

        for sentence1 in self.knowledge:
            print(sentence1)

    def log_cells(self, cells, title, symbol="*"):

        grid = [['-'] * self.width for i in range(self.height)]

        for y in range(0, self.height):
            for x in range(0, self.width):
                cell = (y, x)
                if cell in cells:
                    grid[y][x] = symbol

        self.log_minefield(grid, title)

    def log_data(self):

        grid = [['-'] * self.width for i in range(self.height)]

        for y in range(0, self.height):
            for x in range(0, self.width):
                cell = (y, x)
                if cell in self.mines:
                    grid[y][x] = "M"
                elif cell in self.safes:
                    grid[y][x] = "S"
                elif cell in self.moves_made:
                    grid[y][x] = "?"

        self.log_minefield(grid, "DATA")

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        surrounding_cells = self.get_surrounding_cells(cell)

        # 1) mark the cell as a move that has been made
        self.moves_made.add(cell)
        # 2) mark the cell as safe
        self.mark_safe(cell)
        # 3 / add a new sentence to the AI's knowledge base based on the value of `cell` and `count`
        self.knowledge.append(Sentence(surrounding_cells, count))

        # 4) mark any additional cells as safe or as mines if it can be concluded based on the AI's knowledge base
        for sentence in self.knowledge:
            for cell1 in sentence.known_mines().copy():
                self.mark_mine(cell1)

        for sentence in self.knowledge:
            for cell1 in sentence.known_safes().copy():
                self.mark_safe(cell1)

        # if count = 0 then all surrounding cells are safe
        if count == 0:
            for x in surrounding_cells:
                self.mark_safe(x)

        # 5) add any new sentences to the AI's knowledge base if they can be inferred from existing knowledge
        # Notes: More generally, any time we have two sentences set1 = count1 and set2 = count2 where set1 is
        # a subset of set2, then we can construct the new sentence set2 - set1 = count2 - count1.
        for sentence1 in self.knowledge:
            for sentence2 in self.knowledge:
                if sentence1 is sentence2:
                    continue
                elif sentence1 == sentence2:
                    self.knowledge.remove(sentence2)
                elif sentence1.cells.issubset(sentence2.cells):
                    new_knowledge = Sentence(sentence2.cells - sentence1.cells, sentence2.count - sentence1.count)
                    if new_knowledge not in self.knowledge:
                        print(f"Adding knowledge: {new_knowledge}")
                        self.knowledge.append(new_knowledge)

        for sentence in self.knowledge:
            for cell1 in sentence.known_mines().copy():
                self.mark_mine(cell1)

        for sentence in self.knowledge:
            for cell1 in sentence.known_safes().copy():
                self.mark_safe(cell1)

        self.log_cells(surrounding_cells, f"MOVE {cell} {count}")
        self.log_knowledge()
        self.log_data()

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """

        moves = self.safes - self.moves_made
        move = moves.pop() if len(moves) > 0 else None
        print(f"SAFE MOVE = {move}")
        return move

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        # create a list of available cells that have not been chosen
        cells = set()
        for y in range(0, self.height):
            for x in range(0, self.width):
                cell = (y, x)
                if cell not in self.moves_made and cell not in self.mines:
                    cells.add((y, x))

        if len(cells) == 0:
            return None

        move = cells.pop()
        print(f"RANDOM MOVE = {move}")
        return move