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

        self.check_path_to_king = []
        self.check_through_king = []
        self.potential_white_pawn_check = []
        self.potential_black_pawn_check = []
        self.whiteProtects = []
        self.blackProtects = []
        self.rokadaPossible = [False, False, False, False]  # BK-LBR, BK-RBR, WK-LWR, WK-RWR
        self.notEaten = 0

        self.figures_checking_king = 0
        self.white_king = (7, 4)
        self.black_king = (0, 4)
        self.whiteKingMoved = False
        self.blackKingMoved = False
        self.whiteRooksMoved = [False, False]
        self.blackRooksMoved = [False, False]

        self.king_check = False
        self.values = {"P": 1, "R": 5, "N": 3, "B": 3, "Q": 9, "K": 100}
        self.multiplicator = {"b": -1, "w": 1}
        self.whiteToMove = True
        self.moveLog = []

    def makeMove(self, move):
        self.board[move.start_row][move.start_column] = "--"
        if (move.piece_moved[1] == "P") and ((move.piece_moved[0] == "w" and move.end_row == 0) or (
                move.piece_moved[0] == "b" and move.end_row == 7)):
            if move.piece_moved[0] == "w":
                move.piece_moved = "wQ"
            else:
                move.piece_moved = "bQ"

        if self.board[move.end_row][move.end_column] != "--" or move.piece_moved[1] == "P":
            self.notEaten = 0
        else:
            self.notEaten += 1

        self.board[move.end_row][move.end_column] = move.piece_moved

        if move.rokada:
            if (move.end_row, move.end_column) == (0, 2):
                self.board[0][3] = "bR"
                self.board[0][0] = "--"
                self.blackKingMoved = True
            elif (move.end_row, move.end_column) == (0, 6):
                self.board[0][5] = "bR"
                self.board[0][7] = "--"
                self.blackKingMoved = True
            elif (move.end_row, move.end_column) == (7, 2):
                self.board[7][3] = "wR"
                self.board[7][0] = "--"
                self.whiteKingMoved = True
            elif (move.end_row, move.end_column) == (7, 6):
                self.board[7][5] = "wR"
                self.board[7][7] = "--"
                self.whiteKingMoved = True

        if (move.start_row, move.start_column) == self.white_king:
            self.white_king = (move.end_row, move.end_column)
            self.whiteKingMoved = True
        elif (move.start_row, move.start_column) == self.black_king:
            self.black_king = (move.end_row, move.end_column)
            self.blackKingMoved = True
        if move.start_row == 0:
            if move.start_column == 0:
                self.blackRooksMoved[0] = True
            if move.start_column == 7:
                self.blackRooksMoved[1] = True
        if move.start_row == 7:
            if move.start_column == 0:
                self.whiteRooksMoved[0] = True
            if move.start_column == 7:
                self.whiteRooksMoved[1] = True
        self.moveLog.append(move)  # sacuvamo potez
        self.whiteToMove = not self.whiteToMove

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
        # generator poteza, posle se skidaju ilegalni koji ovde nisu skinuti
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

        King = self.white_king
        if not self.whiteToMove:
            King = self.black_king
        next_to_king = []  # polja do aktuelnog kralja
        if King[0] > 0:
            next_to_king.append((King[0] - 1, King[1]))
            if King[1] > 0:
                next_to_king.append((King[0] - 1, King[1] - 1))
            if King[1] < 7:
                next_to_king.append((King[0] - 1, King[1] + 1))
        if King[0] < 7:
            next_to_king.append((King[0] + 1, King[1]))
            if King[1] < 7:
                next_to_king.append((King[0] + 1, King[1] + 1))
            if King[1] > 0:
                next_to_king.append((King[0] + 1, King[1] - 1))
        if King[1] > 0:
            next_to_king.append((King[0], King[1] - 1))
        if King[1] < 7:
            next_to_king.append((King[0], King[1] + 1))

        # izbacivanje svih pinnovanih figura da igraju poteze (one koje ne mogu da pojedu pretecu figuru ili da se
        # krecu po toj putanji
        i = 0
        king_play_indexes = []  # indeksi poteza koji predstavljaju kraljeve poteze (da ih ne bi trazio svaki put)
        while i < len(moves):
            move = moves.__getitem__(i)
            row = move.start_row
            col = move.start_column
            if move not in self.allowed_pinned and (row, col) in self.pinned:  # mozda postoji sansa ako 2 puta imam
                # figuru u ovoj listi da moram da izbacim svako njeno pojaljivanje iz iste
                moves.__delitem__(i)
                continue
            if (row, col) == King:
                king_play_indexes.append(i)
            i = i + 1

        # ako je sah zabranim rokadu
        if self.king_check:
            self.rokadaPossible[0] = False
            self.rokadaPossible[1] = False
            self.rokadaPossible[2] = False
            self.rokadaPossible[3] = False

        # kralj ne sme da se pomera tamo gde se krecu protivnicke figure (sem piuna za njih se gleda da li jedu)
        i = 0
        while i < len(enemy_moves):
            move = enemy_moves.__getitem__(i)
            row = move.start_row
            col = move.start_column
            if self.rokadaPossible[0] and move.end_row == 0 and 2 <= move.end_column < 4:
                self.rokadaPossible[0] = False
            if self.rokadaPossible[2] and move.end_row == 7 and 2 <= move.end_column < 4:
                self.rokadaPossible[2] = False
            if self.rokadaPossible[1] and move.end_row == 0 and 5 <= move.end_column < 7:
                self.rokadaPossible[1] = False
            if self.rokadaPossible[3] and move.end_row == 7 and 5 <= move.end_column < 7:
                self.rokadaPossible[3] = False

            if self.board[row][col][1] != "P" and (
                    move.end_row, move.end_column) in next_to_king:
                index = 0
                while index < len(king_play_indexes):
                    where = king_play_indexes.__getitem__(index)
                    king_move = moves.__getitem__(where)
                    if ((king_move.end_row, king_move.end_column) == (move.end_row, move.end_column)) or (
                            (king_move.end_row, king_move.end_column) in self.check_through_king):
                        moves.__delitem__(where)
                        king_play_indexes.__delitem__(index)
                        pom_brojac = index
                        while pom_brojac < len(king_play_indexes):
                            king_play_indexes[pom_brojac] = king_play_indexes[pom_brojac] - 1
                            pom_brojac = pom_brojac + 1
                        continue
                    index = index + 1
            i = i + 1

        # kralj ne sme da jede figure koje su zasticene
        protects = self.blackProtects
        if not self.whiteToMove:
            protects = self.whiteProtects
        i = 0
        while i < len(protects):
            move = protects.__getitem__(i)
            if move in next_to_king:
                index = 0
                while index < len(king_play_indexes):
                    where = king_play_indexes.__getitem__(index)
                    king_move = moves.__getitem__(where)
                    if (king_move.end_row, king_move.end_column) == (move[0], move[1]):
                        moves.__delitem__(where)
                        king_play_indexes.__delitem__(index)
                        pom_brojac = index
                        while pom_brojac < len(king_play_indexes):
                            king_play_indexes[pom_brojac] = king_play_indexes[pom_brojac] - 1
                            pom_brojac = pom_brojac + 1
                        continue
                    index = index + 1
            i += 1

        # zabrana da kralj kroci na put piuna
        i = 0
        if not self.whiteToMove:
            while i < len(self.potential_white_pawn_check):
                if self.potential_white_pawn_check.__getitem__(i) in next_to_king:
                    index = 0
                    while index < len(king_play_indexes):
                        where = king_play_indexes.__getitem__(index)
                        king_move = moves.__getitem__(where)
                        if (king_move.end_row, king_move.end_column) == self.potential_white_pawn_check.__getitem__(i):
                            moves.__delitem__(where)
                            king_play_indexes.__delitem__(index)
                            pom_brojac = index
                            while pom_brojac < len(king_play_indexes):
                                king_play_indexes[pom_brojac] = king_play_indexes[pom_brojac] - 1
                                pom_brojac = pom_brojac + 1
                            continue
                        index = index + 1
                i = i + 1
        else:
            while i < len(self.potential_black_pawn_check):
                if self.potential_black_pawn_check.__getitem__(i) in next_to_king:
                    index = 0
                    while index < len(king_play_indexes):
                        where = king_play_indexes.__getitem__(index)
                        king_move = moves.__getitem__(where)
                        if (king_move.end_row, king_move.end_column) == self.potential_black_pawn_check.__getitem__(i):
                            moves.__delitem__(where)
                            king_play_indexes.__delitem__(index)
                            pom_brojac = index
                            while pom_brojac < len(king_play_indexes):
                                king_play_indexes[pom_brojac] = king_play_indexes[pom_brojac] - 1
                                pom_brojac = pom_brojac + 1
                            continue
                        index = index + 1
                i = i + 1

        # na osnovu vrste saha odredjujem koje figure smeju da se pomeraju
        # - ukoliko jeste sah lakse je ubaciti u novu list dobre poteze nego brisati iz liste lose
        new_valid_moves = []
        if len(self.check_path_to_king) > 0 and self.figures_checking_king == 1:
            index = 0
            while index < len(moves):
                move = moves.__getitem__(index)
                row = move.end_row
                col = move.end_column
                if (move.start_row, move.start_column) == self.white_king or (
                        move.start_row, move.start_column) == self.black_king:
                    new_valid_moves.append(move)
                elif (row, col) in self.check_path_to_king:
                    new_valid_moves.append(move)
                index = index + 1
            moves = new_valid_moves
        elif len(self.check_path_to_king) > 0:
            index = 0
            while index < len(moves):
                move = moves.__getitem__(index)
                if (move.start_row, move.start_column) == self.white_king or (
                        move.start_row, move.start_column) == self.black_king:
                    new_valid_moves.append(move)
                index = index + 1
            moves = new_valid_moves

        # ako i dalje sme rokada dodam je u validne poteze
        if self.whiteToMove:
            if self.rokadaPossible[2]:
                moves.append(Move(self.white_king, (7, 2), self.board, True))
            if self.rokadaPossible[3]:
                moves.append(Move(self.white_king, (7, 6), self.board, True))
        else:
            if self.rokadaPossible[0]:
                moves.append(Move(self.black_king, (0, 2), self.board, True))
            if self.rokadaPossible[1]:
                moves.append(Move(self.black_king, (0, 6), self.board, True))

        # cistka svega
        self.potential_white_pawn_check = []
        self.potential_black_pawn_check = []
        self.check_path_to_king = []
        self.check_through_king = []
        self.blackProtects = []
        self.whiteProtects = []
        self.check_path_to_king = []
        self.pinned = []
        self.figures_checking_king = 0
        self.figures_checking_king = 0

        return moves, enemy_moves

    def getKingPosition(self):
        king_position = ()
        if self.king_check:
            if self.whiteToMove:
                king_position = self.white_king
            else:
                king_position = self.black_king
            self.king_check = False
        return king_position

    def getPawnMoves(self, r, c, moves):
        one_offset = -1
        two_offset = -2
        start_row = START_POSITION_WHITE_PAWN
        skip_check = 0
        enemy = "b"
        if not self.whiteToMove:
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
                        self.check_path_to_king.append((r, c))  # ako je piun napravio sah smem da pojedem piuna
                        self.figures_checking_king = self.figures_checking_king + 1
                        self.king_check = True
                elif self.board[r + one_offset][c - 1][0] != enemy:
                    if self.whiteToMove:
                        self.potential_white_pawn_check.append((r + one_offset, c - 1))
                    else:
                        self.potential_black_pawn_check.append((r + one_offset, c - 1))
            if c + 1 <= 7:
                if self.board[r + one_offset][c + 1][0] == enemy:
                    moves.append(Move((r, c), (r + one_offset, c + 1), self.board))
                    if self.board[r + one_offset][c + 1][1] == "K":
                        self.check_path_to_king.append((r, c))  # ako je piun napravio sah smem da pojedem piuna
                        self.figures_checking_king = self.figures_checking_king + 1
                        self.king_check = True
                elif self.board[r + one_offset][c + 1][0] != enemy:
                    if self.whiteToMove:
                        self.potential_white_pawn_check.append((r + one_offset, c + 1))
                    else:
                        self.potential_black_pawn_check.append((r + one_offset, c + 1))

    def getRookMoves(self, r, c, moves):
        enemy = "w"
        if self.whiteToMove:
            enemy = "b"
        elif not self.whiteToMove:
            enemy = "w"

        pinning = False
        old_enemy_r = 0
        old_enemy_c = 0
        check_road = []  # putic do kralja
        made_check = False  # da li sam bas ja napravio sah
        for i in range(r + 1, 8):
            if self.board[i][c] == "--" and not pinning:
                moves.append(Move((r, c), (i, c), self.board))
                check_road.append((i, c))  # putic topa do potencijalnog kralja
            elif self.board[i][c][0] == enemy:
                if not pinning:
                    moves.append(Move((r, c), (i, c), self.board))
                    if self.board[i][c][1] == "K":
                        self.king_check = True
                        made_check = True
                        # gledam polje iza da bih znao gde kralj ne sme da bezi
                        if i + 1 < 8:
                            self.check_through_king.append((i + 1, c))
                        break
                    pinning = True
                    old_enemy_r = i
                    old_enemy_c = c
                else:
                    if self.board[i][c][1] == "K":
                        self.pinned.append((old_enemy_r, old_enemy_c))
                        self.allowed_pinned.append(Move((old_enemy_r, old_enemy_c), (r, c), self.board))
                        for elem in check_road:  # dozvoljeno je kretati se putanjom kojom dolazi potencijalni sah
                            self.allowed_pinned.append(Move((old_enemy_r, old_enemy_c), elem, self.board))
                    break
            elif not pinning:
                if self.whiteToMove:
                    self.whiteProtects.append((i, c))
                else:
                    self.blackProtects.append((i, c))
                break

        if made_check:
            for elem in check_road:
                self.check_path_to_king.append(elem)
            self.check_path_to_king.append((r, c))
            self.figures_checking_king = self.figures_checking_king + 1

        pinning = False
        old_enemy_r = 0
        old_enemy_c = 0
        check_road = []  # putic do kralja
        made_check = False  # da li sam bas ja napravio sah
        for i in range(r - 1, -1, -1):
            if self.board[i][c] == "--" and not pinning:
                moves.append(Move((r, c), (i, c), self.board))
                check_road.append((i, c))  # putic topa do potencijalnog kralja
            elif self.board[i][c][0] == enemy:
                if not pinning:
                    moves.append(Move((r, c), (i, c), self.board))
                    if self.board[i][c][1] == "K":
                        self.king_check = True
                        made_check = True
                        if i - 1 >= 0:
                            self.check_through_king.append((i - 1, c))
                        break
                    pinning = True
                    old_enemy_r = i
                    old_enemy_c = c
                else:
                    if self.board[i][c][1] == "K":
                        self.pinned.append((old_enemy_r, old_enemy_c))
                        self.allowed_pinned.append(Move((old_enemy_r, old_enemy_c), (r, c), self.board))
                        for elem in check_road:
                            self.allowed_pinned.append(Move((old_enemy_r, old_enemy_c), elem, self.board))
                    break
            elif not pinning:
                if self.whiteToMove:
                    self.whiteProtects.append((i, c))
                else:
                    self.blackProtects.append((i, c))
                break

        if made_check:
            for elem in check_road:
                self.check_path_to_king.append(elem)
            self.check_path_to_king.append((r, c))
            self.figures_checking_king = self.figures_checking_king + 1

        pinning = False
        old_enemy_r = 0
        old_enemy_c = 0
        check_road = []  # putic do kralja
        made_check = False  # da li sam bas ja napravio sah
        for i in range(c + 1, 8):
            if self.board[r][i] == "--" and not pinning:
                moves.append(Move((r, c), (r, i), self.board))
                check_road.append((r, i))
            elif self.board[r][i][0] == enemy:
                if not pinning:
                    moves.append(Move((r, c), (r, i), self.board))
                    if self.board[r][i][1] == "K":
                        self.king_check = True
                        made_check = True
                        if i + 1 < 8:
                            self.check_through_king.append((r, i + 1))
                        break
                    pinning = True
                    old_enemy_r = r
                    old_enemy_c = i
                else:
                    if self.board[r][i][1] == "K":
                        self.pinned.append((old_enemy_r, old_enemy_c))
                        self.allowed_pinned.append(Move((old_enemy_r, old_enemy_c), (r, c), self.board))
                        for elem in check_road:
                            self.allowed_pinned.append(Move((old_enemy_r, old_enemy_c), elem, self.board))
                    break
            elif not pinning:
                if self.whiteToMove:
                    self.whiteProtects.append((r, i))
                else:
                    self.blackProtects.append((r, i))
                break

        if made_check:
            for elem in check_road:
                self.check_path_to_king.append(elem)
            self.check_path_to_king.append((r, c))

            self.figures_checking_king = self.figures_checking_king + 1

        pinning = False
        old_enemy_r = 0
        old_enemy_c = 0
        check_road = []  # putic do kralja
        made_check = False  # da li sam bas ja napravio sah
        for i in range(c - 1, -1, -1):
            if self.board[r][i] == "--" and not pinning:
                moves.append(Move((r, c), (r, i), self.board))
                check_road.append((r, i))
            elif self.board[r][i][0] == enemy:
                if not pinning:
                    moves.append(Move((r, c), (r, i), self.board))
                    if self.board[r][i][1] == "K":
                        self.king_check = True
                        made_check = True
                        if i - 1 > 0:
                            self.check_through_king.append((r, i - 1))
                        break
                    pinning = True
                    old_enemy_r = r
                    old_enemy_c = i
                else:
                    if self.board[r][i][1] == "K":
                        self.pinned.append((old_enemy_r, old_enemy_c))
                        self.allowed_pinned.append(Move((old_enemy_r, old_enemy_c), (r, c), self.board))
                        for elem in check_road:
                            self.allowed_pinned.append(Move((old_enemy_r, old_enemy_c), elem, self.board))
                    break
            elif not pinning:
                if self.whiteToMove:
                    self.whiteProtects.append((r, i))
                else:
                    self.blackProtects.append((r, i))
                break

        if made_check:
            for elem in check_road:
                self.check_path_to_king.append(elem)
            self.check_path_to_king.append((r, c))

            self.figures_checking_king = self.figures_checking_king + 1

    def getKnightMoves(self, r, c, moves):
        friend = "w"
        if not self.whiteToMove:
            friend = "b"

        r_offsets = [r + 1, r + 1, r - 1, r - 1, r + 2, r + 2, r - 2, r - 2]
        c_offsets = [c + 2, c - 2, c + 2, c - 2, c + 1, c - 1, c + 1, c - 1]
        i = 0
        while i < 8:
            if 8 > r_offsets[i] >= 0 and 8 > c_offsets[i] >= 0 and \
                    self.board[r_offsets[i]][c_offsets[i]][0] != friend:
                moves.append(Move((r, c), (r_offsets[i], c_offsets[i]), self.board))
                if self.board[r_offsets[i]][c_offsets[i]][1] == "K":
                    self.check_path_to_king.append((r, c))  # ako je konj napravio sah smem da pojedem piuna
                    self.figures_checking_king = self.figures_checking_king + 1
                    self.king_check = True
            elif 8 > r_offsets[i] >= 0 and 8 > c_offsets[i] >= 0:
                if self.whiteToMove:
                    self.whiteProtects.append((r_offsets[i], c_offsets[i]))
                else:
                    self.blackProtects.append((r_offsets[i], c_offsets[i]))
            i += 1

    def getKingMoves(self, r, c, moves):
        self.GetKingRookMoves(r, c, moves)
        self.getKingBishopMoves(r, c, moves)

    def GetKingRookMoves(self, r, c, moves):
        enemy = "w"
        if self.whiteToMove:
            enemy = "b"
            # provera rokade
            if not self.whiteKingMoved:
                if not self.whiteRooksMoved[0] and self.board[7][1] == "--" and self.board[7][2] == "--" and \
                        self.board[7][3] == "--":
                    self.rokadaPossible[2] = True
                if not self.whiteRooksMoved[1] and self.board[7][5] == "--" and self.board[7][6] == "--":
                    self.rokadaPossible[3] = True
        elif not self.whiteToMove:
            enemy = "w"
            # provera rokade
            if not self.blackKingMoved:
                if not self.blackRooksMoved[0] and self.board[0][1] == "--" and self.board[0][2] == "--" and \
                        self.board[0][3] == "--":
                    self.rokadaPossible[0] = True
                if not self.blackRooksMoved[1] and self.board[0][5] == "--" and self.board[0][6] == "--":
                    self.rokadaPossible[1] = True

        for i in range(r + 1, 8):
            if self.board[i][c] == "--":
                moves.append(Move((r, c), (i, c), self.board))
            elif self.board[i][c][0] == enemy:
                moves.append(Move((r, c), (i, c), self.board))
            else:
                if self.whiteToMove:
                    self.whiteProtects.append((i, c))
                else:
                    self.blackProtects.append((i, c))
            break

        for i in range(r - 1, -1, -1):
            if self.board[i][c] == "--":
                moves.append(Move((r, c), (i, c), self.board))
            elif self.board[i][c][0] == enemy:
                moves.append(Move((r, c), (i, c), self.board))
            else:
                if self.whiteToMove:
                    self.whiteProtects.append((i, c))
                else:
                    self.blackProtects.append((i, c))
            break

        for i in range(c + 1, 8):
            if self.board[r][i] == "--":
                moves.append(Move((r, c), (r, i), self.board))
            elif self.board[r][i][0] == enemy:
                moves.append(Move((r, c), (r, i), self.board))
            else:
                if self.whiteToMove:
                    self.whiteProtects.append((r, i))
                else:
                    self.blackProtects.append((r, i))
            break

        for i in range(c - 1, -1, -1):
            if self.board[r][i] == "--":
                moves.append(Move((r, c), (r, i), self.board))
            elif self.board[r][i][0] == enemy:
                moves.append(Move((r, c), (r, i), self.board))
            else:
                if self.whiteToMove:
                    self.whiteProtects.append((r, i))
                else:
                    self.blackProtects.append((r, i))
            break

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
            else:
                if self.whiteToMove:
                    self.whiteProtects.append((i, new_c))
                else:
                    self.blackProtects.append((i, new_c))
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
            else:
                if self.whiteToMove:
                    self.whiteProtects.append((i, new_c))
                else:
                    self.blackProtects.append((i, new_c))
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
            else:
                if self.whiteToMove:
                    self.whiteProtects.append((new_r, i))
                else:
                    self.blackProtects.append((new_r, i))
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
            else:
                if self.whiteToMove:
                    self.whiteProtects.append((new_r, i))
                else:
                    self.blackProtects.append((new_r, i))
            break

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getBishopMoves(self, r, c, moves):
        enemy = "w"
        if self.whiteToMove:
            enemy = "b"

        new_c = c
        pinning = False
        old_enemy_r = 0
        old_enemy_c = 0
        check_road = []  # putic do kralja
        made_check = False  # da li sam bas ja napravio sah
        for i in range(r + 1, 8):
            new_c = new_c + 1
            if new_c >= 8:
                break
            if self.board[i][new_c] == "--" and not pinning:
                moves.append(Move((r, c), (i, new_c), self.board))
                check_road.append((i, new_c))
            elif self.board[i][new_c][0] == enemy:
                if not pinning:
                    moves.append(Move((r, c), (i, new_c), self.board))
                    if self.board[i][new_c][1] == "K":
                        self.king_check = True
                        made_check = True
                        if i + 1 < 8 and new_c + 1 < 8:
                            self.check_through_king.append((i + 1, new_c + 1))
                        break
                    old_enemy_c = new_c
                    old_enemy_r = i
                    pinning = True
                else:
                    if self.board[i][new_c][1] == "K":
                        self.pinned.append((old_enemy_r, old_enemy_c))
                        self.allowed_pinned.append(Move((old_enemy_r, old_enemy_c), (r, c), self.board))
                        for elem in check_road:
                            self.allowed_pinned.append(Move((old_enemy_r, old_enemy_c), elem, self.board))
                    break
            elif not pinning:
                if self.whiteToMove:
                    self.whiteProtects.append((i, new_c))
                else:
                    self.blackProtects.append((i, new_c))
                break
        if made_check:
            for elem in check_road:
                self.check_path_to_king.append(elem)
            self.check_path_to_king.append((r, c))
            self.figures_checking_king = self.figures_checking_king + 1

        new_c = c
        pinning = False
        old_enemy_r = 0
        old_enemy_c = 0
        check_road = []  # putic do kralja
        made_check = False  # da li sam bas ja napravio sah
        for i in range(r - 1, -1, -1):
            new_c = new_c - 1
            if new_c < 0:
                break
            if self.board[i][new_c] == "--" and not pinning:
                moves.append(Move((r, c), (i, new_c), self.board))
                check_road.append((i, new_c))
            elif self.board[i][new_c][0] == enemy:
                if not pinning:
                    moves.append(Move((r, c), (i, new_c), self.board))
                    if self.board[i][new_c][1] == "K":
                        self.king_check = True
                        made_check = True
                        if i - 1 >= 0 and new_c - 1 >= 0:
                            self.check_through_king.append((i - 1, new_c - 1))
                        break
                    old_enemy_c = new_c
                    old_enemy_r = i
                    pinning = True
                else:
                    if self.board[i][new_c][1] == "K":
                        self.pinned.append((old_enemy_r, old_enemy_c))
                        self.allowed_pinned.append(Move((old_enemy_r, old_enemy_c), (r, c), self.board))
                        for elem in check_road:
                            self.allowed_pinned.append(Move((old_enemy_r, old_enemy_c), elem, self.board))
                    break
            elif not pinning:
                if self.whiteToMove:
                    self.whiteProtects.append((i, new_c))
                else:
                    self.blackProtects.append((i, new_c))
                break
        if made_check:
            for elem in check_road:
                self.check_path_to_king.append(elem)
            self.check_path_to_king.append((r, c))
            self.figures_checking_king = self.figures_checking_king + 1

        new_r = r
        pinning = False
        old_enemy_r = 0
        old_enemy_c = 0
        check_road = []  # putic do kralja
        made_check = False  # da li sam bas ja napravio sah
        for i in range(c + 1, 8):
            new_r = new_r - 1
            if new_r < 0:
                break
            if self.board[new_r][i] == "--" and not pinning:
                moves.append(Move((r, c), (new_r, i), self.board))
                check_road.append((new_r, i))
            elif self.board[new_r][i][0] == enemy:
                if not pinning:
                    moves.append(Move((r, c), (new_r, i), self.board))
                    if self.board[new_r][i][1] == "K":
                        self.king_check = True
                        made_check = True
                        if i + 1 < 8 and new_r - 1 >= 0:
                            self.check_through_king.append((new_r - 1, i + 1))
                        break
                    old_enemy_c = i
                    old_enemy_r = new_r
                    pinning = True
                else:
                    if self.board[new_r][i][1] == "K":
                        self.pinned.append((old_enemy_r, old_enemy_c))
                        self.allowed_pinned.append(Move((old_enemy_r, old_enemy_c), (r, c), self.board))
                        for elem in check_road:
                            self.allowed_pinned.append(Move((old_enemy_r, old_enemy_c), elem, self.board))
                    break
            elif not pinning:
                if self.whiteToMove:
                    self.whiteProtects.append((new_r, i))
                else:
                    self.blackProtects.append((new_r, i))
                break
        if made_check:
            for elem in check_road:
                self.check_path_to_king.append(elem)
            self.check_path_to_king.append((r, c))
            self.figures_checking_king = self.figures_checking_king + 1

        new_r = r
        pinning = False
        old_enemy_r = 0
        old_enemy_c = 0
        check_road = []  # putic do kralja
        made_check = False  # da li sam bas ja napravio sah
        for i in range(c - 1, -1, -1):
            new_r = new_r + 1
            if new_r >= 8:
                break
            if self.board[new_r][i] == "--" and not pinning:
                moves.append(Move((r, c), (new_r, i), self.board))
                check_road.append((new_r, i))
            elif self.board[new_r][i][0] == enemy:
                if not pinning:
                    moves.append(Move((r, c), (new_r, i), self.board))
                    if self.board[new_r][i][1] == "K":
                        self.king_check = True
                        made_check = True
                        if i - 1 >= 0 and new_r + 1 < 8:
                            self.check_through_king.append((new_r + 1, i - 1))
                        break
                    old_enemy_c = i
                    old_enemy_r = new_r
                    pinning = True
                else:
                    if self.board[new_r][i][1] == "K":
                        self.pinned.append((old_enemy_r, old_enemy_c))
                        self.allowed_pinned.append(Move((old_enemy_r, old_enemy_c), (r, c), self.board))
                        for elem in check_road:
                            self.allowed_pinned.append(Move((old_enemy_r, old_enemy_c), elem, self.board))
                    break
            elif not pinning:
                if self.whiteToMove:
                    self.whiteProtects.append((new_r, i))
                else:
                    self.blackProtects.append((new_r, i))
                break
        if made_check:
            for elem in check_road:
                self.check_path_to_king.append(elem)
            self.check_path_to_king.append((r, c))
            self.figures_checking_king = self.figures_checking_king + 1


class Move:
    rank_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in rank_to_rows.items()}
    files_to_cols = {"h": 7, "g": 6, "f": 5, "e": 4, "d": 3, "c": 2, "b": 1, "a": 0}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_square, end_square, board, rokada=False):  # konstruktor klase
        self.start_row = start_square[0]
        self.start_column = start_square[1]
        self.end_row = end_square[0]
        self.end_column = end_square[1]
        self.piece_moved = board[self.start_row][self.start_column]
        self.piece_captured = board[self.end_row][self.end_column]
        self.rokada = rokada

    def __eq__(self, other):
        if isinstance(other, Move):
            if self.getChessNotation() == other.getChessNotation():
                other.rokada = self.rokada
                return True
        return False

    def getChessNotation(self):
        return self.getRankFile(self.start_row, self.start_column) + self.getRankFile(self.end_row, self.end_column)

    def getRankFile(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]
