# Eric Wolfe 76946154 eawolfe@uci.edu

# State of a cell
EMPTY_CELL = ' '
FALLER_MOVING_CELL = '['
FALLER_STOPPED_CELL = '|'
OCCUPIED_CELL = 'X'
MATCHED_CELL = '*'

# Directions
LEFT = -1
RIGHT = 1
DOWN = 0

# Contents of a cell
_NONE = 'NONE'
EMPTY = ' '
S = 'S'
T = 'Y'
V = 'V'
W = 'W'
X = 'X'
Y = 'Y'
Z = 'Z'


class GameState:
    def __init__(self, rows: int, columns: int) -> None:
        super().__init__()
        self.rows = rows
        self.columns = columns
        self.boardRows = []
        self.boardStates = []
        self.faller = Faller()
        for i in range(rows):
            row = []
            stateRow = []
            for j in range(columns):
                row.append(EMPTY)
                stateRow.append(EMPTY_CELL)
            self.boardRows.append(row)
            self.boardStates.append(stateRow)

    def set_board_contents(self, contents: [[str]]) -> None:
        return

    def tick(self) -> bool:
        # Handle the faller first
        if self.faller.active:
            # If the faller had stopped last tick then check if it is still on solid ground
            if self.faller.state == FALLER_STOPPED:
                # Do an update on the faller state to see what state it is now in
                self._update_faller_state()
                # If the faller is still stopped after the update then solidify it
                if self.faller.state == FALLER_STOPPED:
                    # Set a value for is part of this faller is solidified above the top of the game board
                    value = False
                    # If part of the faller is above the top of the game board then set the value to true
                    if self.faller.get_row() - 2 < 0:
                        value = True

                    # If all of the faller is in play then we solidify it
                    for i in range(3):
                        self._set_cell(self.faller.get_row() - i, self.faller.get_col(), self.faller.contents[i],
                                       OCCUPIED_CELL)
                    self.faller.active = False

                    # The game ends if part of this faller was solidified above the top of the game board
                    self._matching()
                    return value

            # If we get here then the faller isnt on solid ground for sure so move it down
            self._move_faller_down()
            # Update the faller now so it is in the correct state
            self._update_faller_state()

        # Handle matching and gem gravity
        self._matching()
        return False

    def spawn_faller(self, column: int, faller: [str, str, str]) -> None:
        if self.faller.active:
            return

        self.faller.active = True
        self.faller.contents = faller
        self.faller.set_row(0)
        self.faller.set_col(column - 1)
        self._set_cell(0, self.faller.get_col(), self.faller.contents[0], FALLER_MOVING_CELL)

        # Check if the ground immediately under the faller is solid and if it is then update the fallers state
        self._update_faller_state()

    def rotate_faller(self) -> None:
        # Only works if there is an active faller
        if not self.faller.active:
            return

        one = self.faller.contents[0]
        two = self.faller.contents[1]
        three = self.faller.contents[2]

        self.faller.contents = [two, three, one]
        for i in range(3):
            self._set_cell_contents(self.faller.get_row() - i, self.faller.get_col(), self.faller.contents[i])
        self._update_faller_state()

    def move_faller_side(self, direction: int) -> None:
        # Only works if there is an active faller
        if not self.faller.active:
            return

        # They can only move left and right from this method
        if not direction == RIGHT and not direction == LEFT:
            return

        # They can't move passed the leftmost or rightmost column
        if (direction == LEFT and self.faller.get_col() == 0) or (
                direction == RIGHT and self.faller.get_col() == self.get_columns() - 1):
            return

        targetColumn = self.faller.get_col() + direction
        # Here we are going to check if we can move the faller
        for i in range(3):
            # If the check is going to check a row that is above the top, then we are clear to move the faller
            if self.faller.get_row() - i < 0:
                break

            if self.get_cell_state(self.faller.get_row() - i, targetColumn) == OCCUPIED_CELL:
                return

        # Move the faller to its new column
        for i in range(3):
            # If we are going to go out of bounds then we are done moving
            if self.faller.get_row() - i < 0:
                break
            # Move the cell to the new column
            self._move_cell(self.faller.get_row() - i, self.faller.get_col(), direction)

        # Set the new faller column
        self.faller.set_col(targetColumn)

        # Update the fallers state now that it has moved
        self._update_faller_state()

    def get_rows(self) -> int:
        return self.rows

    def get_columns(self) -> int:
        return self.columns

    def get_cell_state(self, row: int, col: int) -> str:
        return self.boardStates[row][col]

    def get_cell_contents(self, row: int, col: int) -> str:
        return self.boardRows[row][col]

    def _set_cell(self, row: int, col: int, contents: str, state: str) -> None:
        # Not allowed to set cells that fall above the board
        if row < 0:
            return
        self._set_cell_contents(row, col, contents)
        self._set_cell_state(row, col, state)

    def _set_cell_contents(self, row: int, col: int, contents: str) -> None:
        if row < 0:
            return
        self.boardRows[row][col] = contents

    def _set_cell_state(self, row: int, col: int, state: str) -> None:
        if row < 0:
            return
        self.boardStates[row][col] = state

    def _gem_gravity(self) -> None:
        for col in range(self.get_columns()):
            for row in range(self.get_rows() - 1, -1, -1):
                state = self.get_cell_state(row, col)
                # Ignore the crawler when propagating gravity
                if state == FALLER_MOVING_CELL or state == FALLER_STOPPED_CELL:
                    continue
                if state == OCCUPIED_CELL:
                    i = 1
                    while not self._is_solid(row + i, col):
                        self._move_cell(row + i - 1, col, DOWN)
                        i += 1

    def _matching(self) -> None:
        # First thing we do is get rid of any cells that are marked as matched from the previous tick
        for row in range(self.get_rows()):
            for col in range(self.get_columns()):
                if self.get_cell_state(row, col) == MATCHED_CELL:
                    self._set_cell(row, col, EMPTY, EMPTY_CELL)
        # Then we propagate gravity so everything moves down again
        self._gem_gravity()

        # Now we go through all the cells and flag all the matching ones
        # We start at the bottom left corner and move up and to the right while always looking for matches up and right
        #   so this way we never need to worry about looking in all directions. This is because any cell to the left
        #   and down will already have been checked because we moved from that cell
        matches = 0
        gem = _NONE
        # for currentCol in range(self.get_columns()):
        for currentRow in range(self.get_rows() - 1, -1, -1):

            # First thing we do is check along the X-axis (to the right)
            matches = 0
            gem = _NONE
            for col in range(0, self.get_columns()):
                if self.get_cell_contents(currentRow, col) == gem and self.get_cell_state(currentRow, col) == OCCUPIED_CELL:
                    matches += 1
                if self.get_cell_contents(currentRow, col) != gem or col == self.get_columns() - 1:
                    if matches >= 3:
                        if gem != EMPTY:
                            if self.get_cell_contents(currentRow, col) != gem:
                                self._mark_matched_cells(currentRow, col - 1, LEFT, matches)
                            else:
                                self._mark_matched_cells(currentRow, col, LEFT, matches)
                    if self.get_cell_state(currentRow,col) == OCCUPIED_CELL:
                        gem = self.get_cell_contents(currentRow, col)
                        matches = 1
                    else:
                        gem = _NONE
                        matches = 0

    def _mark_matched_cells(self, row: int, col: int, direction: int, amount: int) -> None:
        if direction == LEFT:
            for targetCol in range(col, col - amount, -1):
                self._set_cell_state(row, targetCol, MATCHED_CELL)

    def _update_faller_state(self) -> None:

        state = None
        targetRow = self.faller.get_row() + 1
        if self._is_solid(targetRow, self.faller.get_col()):
            state = FALLER_STOPPED_CELL
            self.faller.state = FALLER_STOPPED
        else:
            state = FALLER_MOVING_CELL
            self.faller.state = FALLER_MOVING

        for i in range(3):
            row = self.faller.get_row() - i
            if row < 0:
                return
            self._set_cell(row, self.faller.get_col(), self.faller.contents[i], state)

    def _is_solid(self, row: int, col: int) -> bool:
        # If the target is below the bottom row than it is solid
        if row >= self.get_rows():
            return True

        if self.get_cell_state(row, col) == OCCUPIED_CELL:
            return True

        return False

    def _move_faller_down(self) -> None:
        # If the faller cant move down then return
        if self._is_solid(self.faller.get_row() + 1, self.faller.get_col()):
            return

        # Move the bottom of the faller down
        self._move_cell(self.faller.get_row(), self.faller.get_col(), DOWN)
        # If the middle of the faller is in play then move it down
        if self.faller.get_row() - 1 >= 0:
            self._move_cell(self.faller.get_row() - 1, self.faller.get_col(), DOWN)
            # If the top of the faller is in play then move it down
            if self.faller.get_row() - 2 >= 0:
                self._move_cell(self.faller.get_row() - 2, self.faller.get_col(), DOWN)
            else:  # If the top of the faller wasnt in play then we set its location to be where the middle was
                self._set_cell(self.faller.get_row() - 1, self.faller.get_col(), self.faller.contents[2],
                               FALLER_MOVING_CELL)
        else:  # If the middle wasnt in play then spawn it where the fallers location was
            self._set_cell(self.faller.get_row(), self.faller.get_col(), self.faller.contents[1], FALLER_MOVING_CELL)

        self.faller.set_row(self.faller.get_row() + 1)

    def _move_cell(self, row: int, col: int, direction: int) -> None:
        oldValue = self.boardRows[row][col]
        oldState = self.boardStates[row][col]

        self.boardRows[row][col] = EMPTY
        self.boardStates[row][col] = EMPTY_CELL

        if direction == DOWN:
            targetRow = row + 1
            self.boardRows[targetRow][col] = oldValue
            self.boardStates[targetRow][col] = oldState
        else:
            targetCol = col + direction
            self.boardRows[row][targetCol] = oldValue
            self.boardStates[row][targetCol] = oldState


FALLER_STOPPED = 0
FALLER_MOVING = 1


class Faller:
    def __init__(self) -> None:
        self.active = False
        self.row = 0
        self.col = 0
        self.contents = [EMPTY, EMPTY, EMPTY]
        self.state = FALLER_MOVING

    def get_row(self) -> int:
        return self.row

    def get_col(self) -> int:
        return self.col

    def set_row(self, row: int) -> None:
        self.row = row

    def set_col(self, col: int) -> None:
        self.col = col
