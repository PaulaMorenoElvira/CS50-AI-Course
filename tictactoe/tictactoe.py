import math
import copy

X = "X"
O = "O"
EMPTY = None


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
    X empieza primero.
    Luego alternan según cuántas X y O haya en el tablero.
    Cómo funciona:
    Cuenta cuántas X y O hay.
    Si hay igual o menos X que O → toca X.
    Si hay más X que O → toca O
    If the board is terminal, return can be anything.
    """
    if terminal(board):
        return None  # Any return is acceptable
    x_count = sum(row.count(X) for row in board)
    o_count = sum(row.count(O) for row in board)
    return X if x_count <= o_count else O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    Devuelve todas las celdas vacías donde se puede jugar.
    Cada acción es una tupla (fila, columna).
    Si el tablero ya terminó, devuelve un set vacío
    """
    if terminal(board):
        return set()  # Any return is acceptable
    return {(i, j) for i in range(3) for j in range(3) if board[i][j] == EMPTY}


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    Raises an exception if action is invalid.
    Devuelve un nuevo tablero con el movimiento aplicado.
    No modifica el tablero original (importante para Minimax, que simula muchos escenarios).
    Usa copy.deepcopy para clonar el tablero.
    Si el movimiento no es válido, lanza un error
    """
    if action not in actions(board):
        raise ValueError("Invalid action")
    new_board = copy.deepcopy(board)
    new_board[action[0]][action[1]] = player(board)
    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    Verifica si alguien ganó:
    Filas iguales
    Columnas iguales
    Diagonales iguales
    Devuelve "X" o "O" si hay ganador, None si no hay.
    """
    # Check rows and columns
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] and board[i][0] is not None:
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] and board[0][i] is not None:
            return board[0][i]
    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] is not None:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] is not None:
        return board[0][2]
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    Devuelve True si el juego terminó:
    Alguien ganó (winner(board) no es None)
    Tablero lleno (empate)
    Si el juego aún está en progreso → devuelve False.
    """
    return winner(board) is not None or all(cell is not EMPTY for row in board for cell in row)


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    Assumes board is terminal.
    """
    w = winner(board)
    if w == X:
        return 1
    elif w == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    If board is terminal, returns None.
    Implementa el algoritmo Minimax: busca el mejor movimiento posible.
    Para X (maximizador):
    Quiere maximizar la utilidad → busca el movimiento que le dé +1.
    Para O (minimizador):
    Quiere minimizar la utilidad → busca el movimiento que le dé -1.
    Se usan funciones recursivas max_value y min_value para simular todos los posibles futuros tableros.
    Devuelve la acción (i, j) óptima.
    Si el tablero ya terminó → devuelve None.
    """

    if terminal(board):
        return None

    current_player = player(board)

    def max_value(board):
        if terminal(board):
            return utility(board)
        v = -math.inf
        for action in actions(board):
            v = max(v, min_value(result(board, action)))
        return v

    def min_value(board):
        if terminal(board):
            return utility(board)
        v = math.inf
        for action in actions(board):
            v = min(v, max_value(result(board, action)))
        return v

    best_action = None

    if current_player == X:
        best_val = -math.inf
        for action in actions(board):
            val = min_value(result(board, action))
            if val > best_val:
                best_val = val
                best_action = action
    else:  # current_player == O
        best_val = math.inf
        for action in actions(board):
            val = max_value(result(board, action))
            if val < best_val:
                best_val = val
                best_action = action

    return best_action
