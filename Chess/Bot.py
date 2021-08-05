import random as r
import ChessEngine as ce


class SagaBot:
    def __init__(self, gameState, depth=1):
        self.gameState = gameState
        self.depth = depth
        self.move_number = 0
        self.valid_moves = []
        self.valid_enemy_moves = []
        self.white_protect_list = []
        self.black_protect_list = []
        self.whiteToMove = False

    def calculateMoves(self, valid_moves, valid_enemy_moves, white_protect_list, black_protect_list, whiteToMove):
        i = 0
        self.move_number += 1
        self.valid_moves = valid_moves
        self.valid_enemy_moves = valid_enemy_moves
        self.white_protect_list = white_protect_list
        self.black_protect_list = black_protect_list
        self.whiteToMove = whiteToMove
        safe_eating_moves = []
        eating_moves = []
        checking_moves = []
        maks = -1000
        best_move = []
        safe_moving_moves = []
        in_danger_list = []
        # while i < len(valid_enemy_moves):
        #     move = valid_enemy_moves.__getitem__(i)
        #     print(str(move.start_row*10+move.start_column) + " to " + str(move.end_row*10+move.end_column))
        #     i += 1
        # i = 0
        while i < len(valid_moves):
            move = valid_moves.__getitem__(i)
            enemy = self.gameState.board[move.end_row][move.end_column]
            me = self.gameState.board[move.start_row][move.start_column]
            if enemy != "--":  # ako postoji neprijatelj koji nije prazno polje
                if enemy[1] == "K":  # potez koji uradi sah
                    checking_moves.append(move)
                else:  # potez koji jede
                    eating_moves.append(move)

                selected_valid_moves = []
                selected_enemy_valid_moves = []

                self.generateMeList(valid_moves, i, move, selected_valid_moves,
                                    True)  # generisem listu poteza koji idu na istu destinaciju kao i ovaj potez`
                self.generateMeList(valid_enemy_moves, i, move, selected_enemy_valid_moves,
                                    False)  # isto i za protivnicke poteze

                if self.whiteToMove:
                    self.expandMeList(white_protect_list, selected_valid_moves, i, True, move)
                    self.expandMeList(black_protect_list, selected_enemy_valid_moves, i, False, move)
                else:
                    self.expandMeList(black_protect_list, selected_valid_moves, i, True, move)
                    self.expandMeList(white_protect_list, selected_enemy_valid_moves, i, False, move)

                selected_valid_moves.sort(key=self.sortByVal)
                selected_enemy_valid_moves.sort(key=self.sortByVal)

                dangerousList = []
                addValue = 0
                if (move.start_row,
                    move.start_column) not in in_danger_list:  # ukoliko vec nisam zabelezio da je figura u opasnosti
                    self.dangerousPosition(valid_enemy_moves, i, ce.Move((move.start_row, move.start_column),
                                                                         (move.start_row, move.start_column),
                                                                         self.gameState.board), dangerousList, False)
                    if len(dangerousList) > 0:
                        in_danger_list.append((move.start_row, move.start_column))
                        addValue = self.gameState.values[me[1]]
                else:
                    addValue = self.gameState.values[me[1]]
                # print(addValue)
                val = self.eatableByEnemy(selected_valid_moves, selected_enemy_valid_moves,
                                          self.gameState.values[me[1]]) + \
                      self.gameState.values[enemy[
                          1]] + addValue

                # if addValue > 0:
                # print("Val je: " + str(val) + " a addValue je: " + str(addValue) + " za potez " + str(
                #     move.start_row) + str(move.start_column) + " na " + str(move.end_row) + str(move.end_column))
                # # brojac = 0
                # print("Protivnickih poteza ima:" + str(len(valid_enemy_moves)))
                # print("Izabranih protivnickih poteza ima:" + str(len(selected_enemy_valid_moves)))
                # while brojac < len(selected_enemy_valid_moves):
                #     print(selected_enemy_valid_moves.__getitem__(brojac))
                #     brojac += 1

                if val >= 0:
                    safe_eating_moves.append(move)
                    if val > maks:
                        best_move = []
                        maks = val
                        best_move.append(move)
                    elif val == maks:
                        best_move.append(move)
            else:
                selected_valid_moves = []
                selected_enemy_valid_moves = []

                self.generateMeList(valid_moves, i, move, selected_valid_moves, True)
                self.generateMeList(valid_enemy_moves, i, move, selected_enemy_valid_moves, False)

                # print("Velicine pre sortiranja: " + str(len(selected_valid_moves))+" " + str(len(selected_enemy_valid_moves)))
                selected_valid_moves.sort(key=self.sortByVal)
                selected_enemy_valid_moves.sort(key=self.sortByVal)
                # print("Velicine posle sortiranja: " + str(len(selected_valid_moves)) + " " + str(
                #     len(selected_enemy_valid_moves)))

                dangerousList = []
                addValue = 0
                if (move.start_row,
                    move.start_column) not in in_danger_list:  # ukoliko vec nisam zabelezio da je figura u opasnosti
                    self.dangerousPosition(valid_enemy_moves, i,
                                           ce.Move((move.start_row, move.start_column),
                                                   (move.start_row, move.start_column),
                                                   self.gameState.board), dangerousList, False)
                    if len(dangerousList) > 0:
                        in_danger_list.append((move.start_row, move.start_column))
                        addValue = self.gameState.values[me[1]]
                else:
                    addValue = self.gameState.values[me[1]]
                # print(addValue)
                val = self.eatableByEnemy(selected_valid_moves, selected_enemy_valid_moves,
                                          self.gameState.values[me[1]]) + addValue
                # if addValue > 0:
                #     print("Val je: " + str(val) + " a addValue je: " + str(addValue) + " za potez " + str(
                #         move.start_row) + str(move.start_column) + " na " + str(move.end_row) + str(move.end_column))
                #     # brojac = 0
                #     print("Protivnickih poteza ima:" + str(len(valid_enemy_moves)))
                #     print("Izabranih protivnickih poteza ima:" + str(len(selected_enemy_valid_moves)))
                #     # while brojac < len(selected_enemy_valid_moves):
                #     #     print(selected_enemy_valid_moves.__getitem__(brojac))
                #     #     brojac+=1

                if val >= 0:
                    safe_moving_moves.append(move)
                    if val > maks:
                        best_move = []
                        maks = val
                        best_move.append(move)
                    elif val == maks:
                        best_move.append(move)

            i += 1

        if len(best_move) != 0:
            print("best move")
            move = best_move.__getitem__(r.randrange(0, len(best_move), 1))

            counter = 0
            if val > 0:
                while counter < len(best_move):
                    alternative = best_move.__getitem__(counter)
                    if move.start_row == alternative.start_row and move.start_column == alternative.start_column:
                        if move.end_row == alternative.end_row and move.end_column == alternative.end_column:
                            counter += 1
                            continue
                        else:
                            if whiteToMove and move.end_row > alternative.end_row:
                                move = alternative
                            elif not whiteToMove and move.end_row < alternative.end_row:
                                move = alternative
                    counter += 1
            else:  # ovaj deo ispod je apsolutno stimovanje igranja i nema veliku logicku vrednost
                if move.piece_moved[1] != "P":
                    while counter < len(best_move):
                        alternative = best_move.__getitem__(counter)
                        if whiteToMove and move.end_row > alternative.end_row and alternative.start_row > 3:
                            return alternative
                        elif not whiteToMove and move.end_row < alternative.end_row and alternative.start_row < 4:
                            return alternative
                        counter += 1

            return move
        if len(safe_eating_moves) != 0:
            print("safe eating move")
            return safe_eating_moves.__getitem__(r.randrange(0, len(safe_eating_moves), 1))
        if len(safe_moving_moves) != 0:
            print("safe moving move")
            return safe_moving_moves.__getitem__(r.randrange(0, len(safe_moving_moves), 1))
        if len(checking_moves) != 0:
            return checking_moves.__getitem__(r.randrange(0, len(checking_moves), 1))
        # if len(eating_moves) != 0:
        #     return eating_moves.__getitem__(r.randrange(0, len(eating_moves), 1))
        return valid_moves.__getitem__(r.randrange(0, len(valid_moves), 1))

    def eatableByEnemy(self, selected_valid_moves, selected_enemy_valid_moves,
                       ex_value):  # gledam koliko dugo traje razmena jedenjem i da li ja izlazim kao pobednik iz toga
        calculate_expense = 0

        if len(selected_enemy_valid_moves) != 0:  # trazim figuru najmanje vrednosti sa kojom moze protivnik da me pojede
            calculate_expense = ex_value
            move = selected_enemy_valid_moves.__getitem__(0)
            me = self.gameState.board[move.start_row][move.start_column]
            selected_enemy_valid_moves.__delitem__(0)
            if self.gameState.values[me[
                1]] <= calculate_expense or len(
                selected_valid_moves) == 0:  # racunam da ce taj potez da odigra protivnik, i onda ako vredi simuliram svoj naredni potez, ako ne vredi zavrsavam
                calculate_expense = self.eatableByGood(selected_valid_moves, selected_enemy_valid_moves,
                                                       self.gameState.values[me[1]]) - calculate_expense
            else:
                calculate_expense = 0

        return calculate_expense

    def eatableByGood(self, selected_valid_moves, selected_enemy_valid_moves, ex_value):
        calculate_expense = 0

        if len(selected_valid_moves) != 0:
            calculate_expense = ex_value
            move = selected_valid_moves.__getitem__(0)
            me = self.gameState.board[move.start_row][move.start_column]
            selected_valid_moves.__delitem__(0)
            if self.gameState.values[me[1]] <= calculate_expense or len(selected_enemy_valid_moves) == 0:
                calculate_expense = self.eatableByEnemy(selected_valid_moves, selected_enemy_valid_moves,
                                                        self.gameState.values[me[1]]) + calculate_expense
            else:
                calculate_expense = 0

        return calculate_expense

    def expandMeList(self, possible_moves, selected_valid_moves, i, skip_iteration, move):
        j = 0
        while j < len(possible_moves):
            if j != i or (not skip_iteration and j == i):
                while_move = possible_moves.__getitem__(j)
                if move.end_row == while_move.end_row and move.end_column == while_move.end_column:
                    selected_valid_moves.append(while_move)
            j += 1

    def generateMeList(self, moves, i, move, selected_moves, skip_iteration):
        j = 0
        blocked_positions = []  # branim da se pijun dva puta gleda (posto moze na 2 pozicije da ode prvi potez)
        # if skip_iteration:
        #     print("Velicina validnih poteza je " + str(len(moves)) + "za potez " + str(move.start_row*10+move.start_column) + " to " + str(move.end_row*10 + move.end_column))
        # else:
        #     print("Velicina validnih poteza protivnika je " + str(len(moves)) + "za potez " + str(move.start_row*10+move.start_column) + " to " + str(move.end_row*10 + move.end_column))

        while j < len(moves):
            if (j != i and skip_iteration) or not skip_iteration:
                while_move = moves.__getitem__(j)

                if (while_move.start_row, while_move.start_column) in blocked_positions:
                    j += 1
                    continue

                me = self.gameState.board[while_move.start_row][while_move.start_column]
                if me[1] != "P":  # svako ko nije piun sme da jede tamo gde se krece
                    if (move.end_row == while_move.end_row) and (move.end_column == while_move.end_column):
                        selected_moves.append(while_move)
                        # print(str(while_move.start_row) + " " + str(while_move.start_column) + " to " + str(
                        #     while_move.end_row) + " " + str(while_move.end_column))
                else:  # samo piun jede dijagonalno a krece se pravo
                    blocked_positions.append((while_move.start_row, while_move.start_column))
                    if me[0] == "w":
                        if (while_move.start_row - 1 >= 0) and (while_move.start_row - 1 == move.end_row):
                            if (while_move.start_column - 1 >= 0) and (while_move.start_column - 1 == move.end_column):
                                selected_moves.append(
                                    ce.Move((while_move.start_row, while_move.start_column),
                                            (while_move.start_row - 1, while_move.start_column - 1),
                                            self.gameState.board))
                                # print("1. " + str(while_move.start_row) + " " + str(
                                #     while_move.start_column) + " to " + str(
                                #     while_move.start_row - 1) + " " + str(while_move.start_column - 1))
                            if (while_move.start_column + 1 <= 7) and (while_move.start_column + 1 == move.end_column):
                                selected_moves.append(
                                    ce.Move((while_move.start_row, while_move.start_column),
                                            (while_move.start_row - 1, while_move.start_column + 1),
                                            self.gameState.board))
                                # print("2. " + str(while_move.start_row) + " " + str(
                                #     while_move.start_column) + " to " + str(
                                #     while_move.start_row - 1) + " " + str(while_move.start_column + 1))
                    else:
                        if (while_move.start_row + 1 <= 7) and (while_move.start_row + 1 == move.end_row):
                            if (while_move.start_column - 1 >= 0) and (while_move.start_column - 1 == move.end_column):
                                selected_moves.append(
                                    ce.Move((while_move.start_row, while_move.start_column),
                                            (while_move.start_row + 1, while_move.start_column - 1),
                                            self.gameState.board))
                                # print("3. " + str(while_move.start_row) + " " + str(
                                #     while_move.start_column) + " to " + str(
                                #     while_move.start_row + 1) + " " + str(while_move.start_column - 1))
                            if (while_move.start_column + 1 <= 7) and (while_move.start_column + 1 == move.end_column):
                                selected_moves.append(
                                    ce.Move((while_move.start_row, while_move.start_column),
                                            (while_move.start_row + 1, while_move.start_column + 1),
                                            self.gameState.board))
                                # print("4. " + str(while_move.start_row) + " " + str(
                                #     while_move.start_column) + " to " + str(
                                #     while_move.start_row + 1) + " " + str(while_move.start_column + 1))
            j += 1
        # print("-------------------------------------------")

    def dangerousPosition(self, valid_moves, i, move, selected_valid_moves, skip_iteration):
        j = 0
        blocked_positions = []  # branim da se pijun dva puta gleda (posto moze na 2 pozicije da ode prvi potez)
        while j < len(valid_moves):
            if (j != i and skip_iteration) or not skip_iteration:
                while_move = valid_moves.__getitem__(j)
                if (while_move.start_row, while_move.start_column) in blocked_positions:
                    j += 1
                    continue
                me = self.gameState.board[while_move.start_row][while_move.start_column]
                if me[1] != "P":  # svako ko nije piun sme da jede tamo gde se krece
                    if move.end_row == while_move.end_row and move.end_column == while_move.end_column:
                        selected_valid_moves.append(while_move)
                        return
                else:  # samo piun jede dijagonalno a krece se pravo
                    blocked_positions.append((while_move.start_row, while_move.start_column))
                    if me[0] == "w":
                        if while_move.start_row - 1 >= 0 and while_move.start_row - 1 == move.end_row:
                            if while_move.start_column - 1 >= 0 and while_move.start_column - 1 == move.end_column:
                                selected_valid_moves.append(
                                    ce.Move((while_move.start_row, while_move.start_column),
                                            (while_move.start_row - 1, while_move.start_column - 1),
                                            self.gameState.board))
                                return
                            if while_move.start_column + 1 <= 7 and while_move.start_column + 1 == move.end_column:
                                selected_valid_moves.append(
                                    ce.Move((while_move.start_row, while_move.start_column),
                                            (while_move.start_row - 1, while_move.start_column + 1),
                                            self.gameState.board))
                                return
                    else:
                        if while_move.start_row + 1 <= 7 and while_move.start_row + 1 == move.end_row:
                            if while_move.start_column - 1 >= 0 and while_move.start_column - 1 == move.end_column:
                                selected_valid_moves.append(
                                    ce.Move((while_move.start_row, while_move.start_column),
                                            (while_move.start_row + 1, while_move.start_column - 1),
                                            self.gameState.board))
                                return
                            if while_move.start_column + 1 <= 7 and while_move.start_column + 1 == move.end_column:
                                selected_valid_moves.append(
                                    ce.Move((while_move.start_row, while_move.start_column),
                                            (while_move.start_row + 1, while_move.start_column + 1),
                                            self.gameState.board))
            j += 1

    def sortByVal(self, move):
        return self.gameState.values[self.gameState.board[move.start_row][move.start_column][1]]
