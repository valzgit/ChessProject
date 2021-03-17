import random as r


class SagaBot:
    def __init__(self, gameState, depth=1):
        self.gameState = gameState
        self.depth = depth

    def calculateMoves(self, valid_moves):
        i = 0
        eating_moves = []
        checking_moves = []
        while i < len(valid_moves):
            move = valid_moves.__getitem__(i)
            enemy = self.gameState.board[move.end_row][move.end_column]
            me = self.gameState.board[move.start_row][move.start_column]
            if enemy != "--":
                if enemy[1] == "K":
                    checking_moves.append(move)
                elif self.gameState.values[enemy[1]] >= self.gameState.values[me[1]]:
                    eating_moves.append(move)
            i += 1
        if len(eating_moves) != 0:
            return eating_moves.__getitem__(r.randrange(0, len(eating_moves), 1))
        elif len(checking_moves) != 0:
            return checking_moves.__getitem__(r.randrange(0, len(checking_moves), 1))
        else:
            return valid_moves.__getitem__(r.randrange(0, len(valid_moves), 1))
