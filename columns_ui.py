# Eric Wolfe 76946154 eawolfe@uci.edu
import columns_game as game


def start_game() -> None:
    rows = get_int()
    cols = get_int()
    state = game.GameState(rows, cols)

    line = next_line()
    if line == 'CONTENTS':
        rowList = []
        for i in range(rows):
            row = []
            line = raw_next_line()
            for index in range(cols):
                row.append(line[index])
            rowList.append(row)
        state.set_board_contents(rowList)

    while True:
        display_board(state)
        line = next_line()
        if line == 'Q':
            return
        if line == '':
            if state.tick():
                display_board(state)
                break
        else:
            process_command(line, state)
    print('GAME OVER')


def process_command(command: str, state: game.GameState) -> None:
    if command == 'R':
        state.rotate_faller()
    elif command == '<':
        state.move_faller_side(game.LEFT)
    elif command == '>':
        state.move_faller_side(game.RIGHT)
    elif command[0] == 'F':
        try:
            args = command.split(' ')
            columnNumber = int(args[1])
            faller = [args[4], args[3], args[2]]
            state.spawn_faller(columnNumber, faller)
        except:
            return


def display_board(state: game.GameState) -> None:
    for row in range(state.get_rows()):
        rowString = "|"
        for col in range(state.get_columns()):
            cellValue = state.get_cell_contents(row, col)
            cellState = state.get_cell_state(row, col)
            if cellState == game.EMPTY_CELL:
                rowString += '   '
            elif cellState == game.OCCUPIED_CELL:
                rowString += (' ' + cellValue + ' ')
            elif cellState == game.FALLER_MOVING_CELL:
                rowString += ('[' + cellValue + ']')
            elif cellState == game.FALLER_STOPPED_CELL:
                rowString += ('|' + cellValue + '|')
            elif cellState == game.MATCHED_CELL:
                rowString += ('*' + cellValue + '*')
        rowString += '|'
        print(rowString)
    finalLine = ' '
    for col in range(state.get_columns()):
        finalLine += '---'
    finalLine += ' '
    print(finalLine)


def get_int() -> int:
    line = input().strip()
    return int(line)


def next_line() -> str:
    return input().strip()


def raw_next_line() -> str:
    return input()

if __name__ == '__main__':
    start_game()
