START_POSITION_BLACK_PAWN = 1
START_POSITION_WHITE_PAWN = 6


class GameState:
    def __init__(self):

        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.shadows = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [-4, - 2, - 5, - 2, - 2, - 5, - 2, - 4],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [4, 2, 5, 2, 2, 5, 2, 4],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
        ]

        self.pinned = []  # pozicije na kojima se nalaze figure koje su na putu izmedju figure koja jede i kralja
        self.allowed_pinned = []  # slucajevi ukoliko 'pinovane' figure mogu da pojedu figuru koja preti
        self.moveFunctions = {"P": self.getPawnMoves, "R": self.getRookMoves, "N": self.getKnightMoves,
                              "B": self.getBishopMoves, "Q": self.getQueenMoves, "K": self.getKingMoves}
        self.white_king = (0, 4)
        self.black_king = (7, 4)
        self.king_check = False
        self.values = {"P": 1, "R": 5, "N": 3, "B": 3, "Q": 9, "K": 100}
        self.multiplicator = {"b": -1, "w": 1}
        self.whiteToMove = True
        self.moveLog = []

    def makeMove(self, move):
        self.board[move.start_row][move.start_column] = "--"
        self.board[move.end_row][move.end_column] = move.piece_moved
        self.moveLog.append(move)  # sacuvamo potez
        self.whiteToMove = not self.whiteToMove
        if (move.start_row, move.start_column) == self.white_king:
            self.white_king = (move.end_row, move.end_column)
        elif (move.start_row, move.start_column) == self.black_king:
            self.black_king = (move.end_row, move.end_column)

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.start_row][move.start_column] = move.piece_moved
            self.board[move.end_row][move.end_column] = move.piece_captured
            self.whiteToMove = not self.whiteToMove
            if (move.end_row, move.end_column) == self.white_king:
                self.white_king = (move.start_row, move.start_column)
            elif (move.end_row, move.end_column) == self.black_king:
                self.black_king = (move.start_row, move.start_column)

    def getValidMoves(self):
        moves = []
        enemy_moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)
                elif (turn == "w" and not self.whiteToMove) or (turn == "b" and self.whiteToMove):
                    self.whiteToMove = not self.whiteToMove
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, enemy_moves)
                    self.whiteToMove = not self.whiteToMove
        return moves, enemy_moves

    def getPawnMoves(self, r, c, moves):
        one_offset = 0
        two_offset = 0
        start_row = 0
        skip_check = 0
        enemy = "w"
        if self.whiteToMove:
            one_offset = -1
            two_offset = -2
            start_row = START_POSITION_WHITE_PAWN
            skip_check = 0
            enemy = "b"
        elif not self.whiteToMove:
            one_offset = 1
            two_offset = 2
            skip_check = 7
            start_row = START_POSITION_BLACK_PAWN
            enemy = "w"

        if r != skip_check:
            if self.board[r + one_offset][c] == "--":
                moves.append(Move((r, c), (r + one_offset, c), self.board))
                if r == start_row and self.board[r + two_offset][c] == "--":
                    moves.append(Move((r, c), (r + two_offset, c), self.board))
            if c - 1 >= 0:
                if self.board[r + one_offset][c - 1][0] == enemy:
                    moves.append(Move((r, c), (r + one_offset, c - 1), self.board))
                    if self.board[r + one_offset][c - 1][1] == "K":
                        self.king_check = True
            if c + 1 <= 7:
                if self.board[r + one_offset][c + 1][0] == enemy:
                    moves.append(Move((r, c), (r + one_offset, c + 1), self.board))
                    if self.board[r + one_offset][c + 1][1] == "K":
                        self.king_check = True

        # dodaj promociju piuna posle

    def GetKingRookMoves(self, r, c, moves):
        enemy = "w"
        if self.whiteToMove:
            enemy = "b"
        elif not self.whiteToMove:
            enemy = "w"

        for i in range(r + 1, 8):
            if self.board[i][c] == "--":
                moves.append(Move((r, c), (i, c), self.board))
            elif self.board[i][c][0] == enemy:
                moves.append(Move((r, c), (i, c), self.board))
            break

        for i in range(r - 1, -1, -1):
            if self.board[i][c] == "--":
                moves.append(Move((r, c), (i, c), self.board))
            elif self.board[i][c][0] == enemy:
                moves.append(Move((r, c), (i, c), self.board))
            break

        for i in range(c + 1, 8):
            if self.board[r][i] == "--":
                moves.append(Move((r, c), (r, i), self.board))
            elif self.board[r][i][0] == enemy:
                moves.append(Move((r, c), (r, i), self.board))
            break

        for i in range(c - 1, -1, -1):
            if self.board[r][i] == "--":
                moves.append(Move((r, c), (r, i), self.board))
            elif self.board[r][i][0] == enemy:
                moves.append(Move((r, c), (r, i), self.board))
            break

    def getRookMoves(self, r, c, moves):
        enemy = "w"
        if self.whiteToMove:
            enemy = "b"
        elif not self.whiteToMove:
            enemy = "w"

        pinning = False
        old_enemy_r = 0
        old_enemy_c = 0
        for i in range(r + 1, 8):
            if self.board[i][c] == "--" and not pinning:
                moves.append(Move((r, c), (i, c), self.board))
            elif self.board[i][c][0] == enemy:
                if not pinning:
                    moves.append(Move((r, c), (i, c), self.board))
                    if self.board[i][c][1] == "K":
                        self.king_check = True
                        break
                    pinning = True
                    old_enemy_r = i
                    old_enemy_c = c
                else:
                    if self.board[i][c][1] == "K":
                        self.pinned.append((old_enemy_r, old_enemy_c))
                        self.allowed_pinned.append(Move((old_enemy_r, old_enemy_c), (r, c), self.board))
                    else:
                        break
            elif not pinning:
                break

        pinning = False
        old_enemy_r = 0
        old_enemy_c = 0
        for i in range(r - 1, -1, -1):
            if self.board[i][c] == "--" and not pinning:
                moves.append(Move((r, c), (i, c), self.board))
            elif self.board[i][c][0] == enemy:
                if not pinning:
                    moves.append(Move((r, c), (i, c), self.board))
                    if self.board[i][c][1] == "K":
                        self.king_check = True
                        break
                    pinning = True
                    old_enemy_r = i
                    old_enemy_c = c
                else:
                    if self.board[i][c][1] == "K":
                        self.pinned.append((old_enemy_r, old_enemy_c))
                        self.allowed_pinned.append(Move((old_enemy_r, old_enemy_c), (r, c), self.board))
                    else:
                        break
            else:
                break

        pinning = False
        old_enemy_r = 0
        old_enemy_c = 0
        for i in range(c + 1, 8):
            if self.board[r][i] == "--" and not pinning:
                moves.append(Move((r, c), (r, i), self.board))
            elif self.board[r][i][0] == enemy:
                if not pinning:
                    moves.append(Move((r, c), (r, i), self.board))
                    if self.board[r][i][1] == "K":
                        self.king_check = True
                        break
                    pinning = True
                    old_enemy_r = r
                    old_enemy_c = i
                else:
                    if self.board[r][i][1] == "K":
                        self.pinned.append((old_enemy_r, old_enemy_c))
                        self.allowed_pinned.append(Move((old_enemy_r, old_enemy_c), (r, c), self.board))
                    else:
                        break
            elif not pinning:
                break

        pinning = False
        old_enemy_r = 0
        old_enemy_c = 0
        for i in range(c - 1, -1, -1):
            if self.board[r][i] == "--" and not pinning:
                moves.append(Move((r, c), (r, i), self.board))
            elif self.board[r][i][0] == enemy:
                if not pinning:
                    moves.append(Move((r, c), (r, i), self.board))
                    if self.board[r][i][1] == "K":
                        self.king_check = True
                        break
                    pinning = True
                    old_enemy_r = r
                    old_enemy_c = i
                else:
                    if self.board[r][i][1] == "K":
                        self.pinned.append((old_enemy_r, old_enemy_c))
                        self.allowed_pinned.append(Move((old_enemy_r, old_enemy_c), (r, c), self.board))
                    else:
                        break
            elif not pinning:
                break

    def getKnightMoves(self, r, c, moves):
        friend = "w"
        if self.whiteToMove:
            friend = "w"
        elif not self.whiteToMove:
            friend = "b"
        if r + 1 < 8 and c + 2 < 8 and self.board[r + 1][c + 2][0] != friend:
            moves.append(Move((r, c), (r + 1, c + 2), self.board))
            if self.board[r + 1][c + 2][1] == "K":
                self.king_check = True
        if r + 1 < 8 and c - 2 >= 0 and self.board[r + 1][c - 2][0] != friend:
            moves.append(Move((r, c), (r + 1, c - 2), self.board))
            if self.board[r + 1][c - 2][1] == "K":
                self.king_check = True
        if r - 1 >= 0 and c + 2 < 8 and self.board[r - 1][c + 2][0] != friend:
            moves.append(Move((r, c), (r - 1, c + 2), self.board))
            if self.board[r - 1][c + 2][1] == "K":
                self.king_check = True
        if r - 1 >= 0 and c - 2 >= 0 and self.board[r - 1][c - 2][0] != friend:
            moves.append(Move((r, c), (r - 1, c - 2), self.board))
            if self.board[r - 1][c - 2][1] == "K":
                self.king_check = True
        if r + 2 < 8 and c + 1 < 8 and self.board[r + 2][c + 1][0] != friend:
            moves.append(Move((r, c), (r + 2, c + 1), self.board))
            if self.board[r + 2][c + 1][1] == "K":
                self.king_check = True
        if r + 2 < 8 and c - 1 >= 0 and self.board[r + 2][c - 1][0] != friend:
            moves.append(Move((r, c), (r + 2, c - 1), self.board))
            if self.board[r + 2][c - 1][1] == "K":
                self.king_check = True
        if r - 2 >= 0 and c + 1 < 8 and self.board[r - 2][c + 1][0] != friend:
            moves.append(Move((r, c), (r - 2, c + 1), self.board))
            if self.board[r - 2][c + 1][1] == "K":
                self.king_check = True
        if r - 2 >= 0 and c - 1 >= 0 and self.board[r - 2][c - 1][0] != friend:
            moves.append(Move((r, c), (r - 2, c - 1), self.board))
            if self.board[r - 2][c - 1][1] == "K":
                self.king_check = True

    def getKingMoves(self, r, c, moves):
        self.GetKingRookMoves(r, c, moves)
        self.getKingBishopMoves(r, c, moves)

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingBishopMoves(self, r, c, moves):
        enemy = "w"
        if self.whiteToMove:
            enemy = "b"
        elif not self.whiteToMove:
            enemy = "w"

        new_c = c
        for i in range(r + 1, 8):
            new_c = new_c + 1
            if new_c >= 8:
                break
            if self.board[i][new_c] == "--":
                moves.append(Move((r, c), (i, new_c), self.board))
            elif self.board[i][new_c][0] == enemy:
                moves.append(Move((r, c), (i, new_c), self.board))
                if self.board[i][new_c][1] == "K":
                    self.king_check = True
            break

        new_c = c
        for i in range(r - 1, -1, -1):
            new_c = new_c - 1
            if new_c < 0:
                break
            if self.board[i][new_c] == "--":
                moves.append(Move((r, c), (i, new_c), self.board))
            elif self.board[i][new_c][0] == enemy:
                moves.append(Move((r, c), (i, new_c), self.board))
                if self.board[i][new_c][1] == "K":
                    self.king_check = True
            break

        new_r = r
        for i in range(c + 1, 8):
            new_r = new_r - 1
            if new_r < 0:
                break
            if self.board[new_r][i] == "--":
                moves.append(Move((r, c), (new_r, i), self.board))
            elif self.board[new_r][i][0] == enemy:
                moves.append(Move((r, c), (new_r, i), self.board))
                if self.board[new_r][i][1] == "K":
                    self.king_check = True
            break

        new_r = r
        for i in range(c - 1, -1, -1):
            new_r = new_r + 1
            if new_r >= 8:
                break
            if self.board[new_r][i] == "--":
                moves.append(Move((r, c), (new_r, i), self.board))
            elif self.board[new_r][i][0] == enemy:
                moves.append(Move((r, c), (new_r, i), self.board))
                if self.board[new_r][i][1] == "K":
                    self.king_check = True
            break

    def getBishopMoves(self, r, c, moves):
        enemy = "w"
        if self.whiteToMove:
            enemy = "b"
        elif not self.whiteToMove:
            enemy = "w"

        new_c = c
        pinning = False
        old_enemy_r = 0
        old_enemy_c = 0
        for i in range(r + 1, 8):
            new_c = new_c + 1
            if new_c >= 8:
                break
            if self.board[i][new_c] == "--" and not pinning:
                moves.append(Move((r, c), (i, new_c), self.board))
            elif self.board[i][new_c][0] == enemy:
                if not pinning:
                    moves.append(Move((r, c), (i, new_c), self.board))
                    if self.board[i][new_c][1] == "K":
                        self.king_check = True
                        break
                    old_enemy_c = new_c
                    old_enemy_r = i
                    pinning = True
                else:
                    if self.board[i][new_c][1] == "K":
                        self.pinned.append((old_enemy_r, old_enemy_c))
                        self.allowed_pinned.append(Move((old_enemy_r, old_enemy_c), (r, c), self.board))
                    else:
                        break
            elif not pinning:
                break

        new_c = c
        pinning = False
        old_enemy_r = 0
        old_enemy_c = 0
        for i in range(r - 1, -1, -1):
            new_c = new_c - 1
            if new_c < 0:
                break
            if self.board[i][new_c] == "--" and not pinning:
                moves.append(Move((r, c), (i, new_c), self.board))
            elif self.board[i][new_c][0] == enemy:
                if not pinning:
                    moves.append(Move((r, c), (i, new_c), self.board))
                    if self.board[i][new_c][1] == "K":
                        self.king_check = True
                        break
                    old_enemy_c = new_c
                    old_enemy_r = i
                    pinning = True
                else:
                    if self.board[i][new_c][1] == "K":
                        self.pinned.append((old_enemy_r, old_enemy_c))
                        self.allowed_pinned.append(Move((old_enemy_r, old_enemy_c), (r, c), self.board))
                    else:
                        break
            elif not pinning:
                break

        new_r = r
        pinning = False
        old_enemy_r = 0
        old_enemy_c = 0
        for i in range(c + 1, 8):
            new_r = new_r - 1
            if new_r < 0:
                break
            if self.board[new_r][i] == "--" and not pinning:
                moves.append(Move((r, c), (new_r, i), self.board))
            elif self.board[new_r][i][0] == enemy:
                if not pinning:
                    moves.append(Move((r, c), (new_r, i), self.board))
                    if self.board[new_r][i][1] == "K":
                        self.king_check = True
                        break
                    old_enemy_c = i
                    old_enemy_r = new_r
                    pinning = True
                else:
                    if self.board[new_r][i][1] == "K":
                        self.pinned.append((old_enemy_r, old_enemy_c))
                        self.allowed_pinned.append(Move((old_enemy_r, old_enemy_c), (r, c), self.board))
                    else:
                        break
            elif not pinning:
                break

        new_r = r
        pinning = False
        old_enemy_r = 0
        old_enemy_c = 0
        for i in range(c - 1, -1, -1):
            new_r = new_r + 1
            if new_r >= 8:
                break
            if self.board[new_r][i] == "--" and not pinning:
                moves.append(Move((r, c), (new_r, i), self.board))
            elif self.board[new_r][i][0] == enemy:
                if not pinning:
                    moves.append(Move((r, c), (new_r, i), self.board))
                    if self.board[new_r][i][1] == "K":
                        self.king_check = True
                        break
                    old_enemy_c = i
                    old_enemy_r = new_r
                    pinning = True
                else:
                    if self.board[new_r][i][1] == "K":
                        self.pinned.append((old_enemy_r, old_enemy_c))
                        self.allowed_pinned.append(Move((old_enemy_r, old_enemy_c), (r, c), self.board))
                    else:
                        break
            elif not pinning:
                break


class Move:
    rank_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in rank_to_rows.items()}
    files_to_cols = {"h": 7, "g": 6, "f": 5, "e": 4, "d": 3, "c": 2, "b": 1, "a": 0}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_square, end_square, board):  # konstruktor klase
        self.start_row = start_square[0]
        self.start_column = start_square[1]
        self.end_row = end_square[0]
        self.end_column = end_square[1]
        self.piece_moved = board[self.start_row][self.start_column]
        self.piece_captured = board[self.end_row][self.end_column]

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.getChessNotation() == other.getChessNotation()
        return False

    def getChessNotation(self):
        return self.getRankFile(self.start_row, self.start_column) + self.getRankFile(self.end_row, self.end_column)

    def getRankFile(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]
