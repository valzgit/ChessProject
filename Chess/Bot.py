import random as r


class SagaBot:
    def __init__(self, gameState, depth=1):
        self.gameState = gameState
        self.depth = depth
        self.move_number = 0
        self.valid_moves = []
        self.valid_enemy_moves = []

    def calculateMoves(self, valid_moves, valid_enemy_moves):
        i = 0
        self.move_number += 1
        self.valid_moves = valid_moves
        self.valid_enemy_moves = valid_enemy_moves
        safe_eating_moves = []
        eating_moves = []
        checking_moves = []
        maks = -1000
        best_move = []
        safe_moving_moves = []

        while i < len(valid_moves):
            move = valid_moves.__getitem__(i)
            enemy = self.gameState.board[move.end_row][move.end_column]
            me = self.gameState.board[move.start_row][move.start_column]
            if enemy != "--":
                if enemy[1] == "K":
                    checking_moves.append(move)
                else:
                    eating_moves.append(move)
                    j = 0
                    selected_valid_moves = []
                    selected_enemy_valid_moves = []
                    while j < len(valid_moves):
                        if j != i:
                            while_move = valid_moves.__getitem__(j)
                            if move.end_row == while_move.end_row and move.end_column == while_move.end_column:
                                selected_valid_moves.append(while_move)
                        j += 1
                    j = 0
                    while j < len(valid_enemy_moves):
                        while_move = valid_enemy_moves.__getitem__(j)
                        if move.end_row == while_move.end_row and move.end_column == while_move.end_column:
                            selected_enemy_valid_moves.append(while_move)
                        j += 1

                    val = self.eatableByEnemy(selected_valid_moves, selected_enemy_valid_moves,
                                              self.gameState.values[me[1]]) + \
                          self.gameState.values[enemy[1]]
                    if val >= 0:
                        safe_eating_moves.append(move)
                        if val > maks:
                            best_move = []
                            maks = val
                            best_move.append(move)
                        elif val == maks:
                            best_move.append(move)
            else:
                j = 0
                selected_valid_moves = []
                selected_enemy_valid_moves = []
                while j < len(valid_moves):
                    if j != i:
                        while_move = valid_moves.__getitem__(j)
                        if move.end_row == while_move.end_row and move.end_column == while_move.end_column:
                            selected_valid_moves.append(while_move)
                    j += 1
                j = 0
                while j < len(valid_enemy_moves):
                    while_move = valid_enemy_moves.__getitem__(j)
                    if move.end_row == while_move.end_row and move.end_column == while_move.end_column:
                        print(str(while_move.start_row) + " " + str(while_move.start_column) + " to " + str(while_move.end_row) + " " + str(while_move.end_column))
                        selected_enemy_valid_moves.append(while_move)
                    j += 1

                val = self.eatableByEnemy(selected_valid_moves, selected_enemy_valid_moves,
                                          self.gameState.values[me[1]])
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
            return best_move.__getitem__(r.randrange(0, len(best_move), 1))
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

    def eatableByEnemy(self, selected_valid_moves, selected_enemy_valid_moves, ex_value):
        calculate_expense = 0
        i = 0
        min_pos = -1
        min_val = 1000
        # print(len(selected_enemy_valid_moves))
        while i < len(selected_enemy_valid_moves):
            move = selected_enemy_valid_moves.__getitem__(i)
            me = self.gameState.board[move.start_row][move.start_column]
            if self.gameState.values[me[1]] < min_val:
                min_val = self.gameState.values[me[1]]
                min_pos = i
                calculate_expense = ex_value
            i += 1

        if min_pos != -1:
            move = selected_enemy_valid_moves.__getitem__(min_pos)
            me = self.gameState.board[move.start_row][move.start_column]
            selected_enemy_valid_moves.__delitem__(min_pos)
            calculate_expense = self.eatableByGood(selected_valid_moves, selected_enemy_valid_moves,
                                                    self.gameState.values[me[1]]) - calculate_expense
        return calculate_expense

    def eatableByGood(self, selected_valid_moves, selected_enemy_valid_moves, ex_value):
        calculate_expense = 0
        i = 0
        min_pos = -1
        min_val = 1000
        while i < len(selected_valid_moves):
            move = selected_valid_moves.__getitem__(i)
            me = self.gameState.board[move.start_row][move.start_column]
            if self.gameState.values[me[1]] < min_val:
                min_val = self.gameState.values[me[1]]
                min_pos = i
                calculate_expense = ex_value
            i += 1

        if min_pos != -1:
            move = selected_valid_moves.__getitem__(min_pos)
            me = self.gameState.board[move.start_row][move.start_column]
            selected_valid_moves.__delitem__(min_pos)
            calculate_expense = self.eatableByGood(selected_valid_moves, selected_enemy_valid_moves,
                                                    self.gameState.values[me[1]]) + calculate_expense
        return calculate_expense
