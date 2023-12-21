"""
Tic Tac Toe Player
"""

X = "X"
O = "O"
EMPTY = None
positive_infinity = float('inf')
negative_infinity = float('-inf')

def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """

    current = "X"

    for i in range(3):
        for j in range(3):
            if board[i][j] != EMPTY:
                current = "O" if current == "X" else "X"

    return current


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """

    actions = set()

    for i in range(3):
        for j in range(3):
            if not board[i][j]:
                actions.add((i, j))

    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    if action is None:
        return board

    newBoard = [[None, None, None],[None, None, None],[None, None, None]]

    for i in range(3):
        for j in range(3):
            newBoard[i][j] = board[i][j]

    i, j = action
    newBoard[i][j] = player(board)
    return newBoard


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    for i in range(3):
        if board[i][0] is not None and board[i][0] == board[i][1] == board[i][2]:
            return board[i][0]

        if board[0][i] is not None and board[0][i] == board[1][i] == board[2][i]:
            return board[0][i]

    if board[0][0] is not None and board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]

    if board[0][2] is not None and board[2][0] == board[1][1] == board[0][2]:
        return board[0][2]

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    return utility(board) != 0 or len(actions(board)) == 0


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """

    w = winner(board)

    if w == "X":
        return 1
    elif w == "O":
        return -1

    return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    if terminal(board):
        return None

    current = player(board)
    # printboard(board)

    best_actions = None
    action_list = actions(board)

    for action in action_list:

        state = result(board, action)
        max_value = maxValue(state)
        min_value = minValue(state)

        if current == "X":

            if max_value == 1 and min_value == 0:
                best_actions = action
                break

            if max_value == min_value == 0:
                best_actions = action

            if max_value == min_value == 1:
                best_actions = action

        elif current == "O":

            if max_value == 0 and min_value == -1:
                best_actions = action
                break

            if max_value == min_value == 0:
                best_actions = action

            if max_value == min_value == -1:
                best_actions = action

        # print(f"{action}, player {current} {best_actions} max: {max_value} min: {min_value}")

    # print(f"choice: {best_actions}")
    return best_actions


def minValue(board):

    if terminal(board):
        return utility(board)

    v = positive_infinity

    for action in actions(board):
        v = min(v, maxValue(result(board, action)))

    return v


def maxValue(board):

    if terminal(board):
        return utility(board)

    v = negative_infinity

    for action in actions(board):
        v = max(v, minValue(result(board, action)))

    return v


def printboard(board):

    for row in range(3):
        for col in range(3):
            player = board[row][col] or ""
            print(f" {player:2}", end=" |" if col < 2 else None)
