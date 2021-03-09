import pygame as p
import random as r
from Chess import ChessEngine

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}


def loadImages():
    pieces = ["wP", "wR",  "wK", "wB", "wN", "wQ", "bP", "bR", "bK", "bB", "bN", "bQ"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def main():
    SAH_MAT = False
    possible_moves = []
    king_position = ()
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    valid_moves, valid_enemy_moves = gs.getValidMoves()
    move_made = False
    loadImages()  # only once
    running = True
    square_selected = ()
    playerClicks = []
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN and not SAH_MAT:
                location = p.mouse.get_pos()
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                playing = "w"
                if gs.whiteToMove:
                    playing = "w"
                else:
                    playing = "b"
                if square_selected == (row, col):  # da li je 2 puta kliknuo na isto polje
                    square_selected = ()
                    playerClicks = []
                    possible_moves = []
                elif len(square_selected) != 0 and gs.board[row][col][0] == playing:
                    square_selected = (row, col)
                    playerClicks = [square_selected]
                    possible_moves = []
                else:
                    square_selected = (row, col)
                    playerClicks.append(square_selected)
                if len(playerClicks) == 1:
                    turn = gs.board[row][col][0]
                    if (turn == "w" and gs.whiteToMove) or (turn == "b" and not gs.whiteToMove):
                        i = 0
                        while i < len(valid_moves):
                            if (valid_moves.__getitem__(i).start_row, valid_moves.__getitem__(i).start_column) == (
                                    row, col):
                                possible_moves.append(valid_moves.__getitem__(i))
                            i = i + 1
                if len(playerClicks) == 2:
                    possible_moves = []
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    if move in valid_moves:
                        print(move.getChessNotation())
                        gs.makeMove(move)
                        move_made = True
                    playerClicks = []
                    square_selected = ()
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo kada stisnem z
                    gs.undoMove()
                    king_position = ()
                    playerClicks = []
                    square_selected = ()
                    move_made = True

        if move_made:
            gs.pinned = []
            valid_moves, valid_enemy_moves = gs.getValidMoves()
            i = 0
            King = gs.white_king
            next_to_king = []
            if gs.whiteToMove:
                King = gs.black_king
            if King[0] > 0 and King[1] > 0:
                next_to_king.append((King[0] - 1, King[1] - 1))
            if King[0] < 7 and King[1] < 7:
                next_to_king.append((King[0] + 1, King[1] + 1))
            if King[0] > 0 and King[1] < 7:
                next_to_king.append((King[0] - 1, King[1] + 1))
            if King[0] < 7 and King[1] > 0:
                next_to_king.append((King[0] + 1, King[1] - 1))
            if King[0] > 0:
                next_to_king.append((King[0] - 1, King[1]))
            if King[0] < 7:
                next_to_king.append((King[0] + 1, King[1]))
            if King[1] > 0:
                next_to_king.append((King[0], King[1] - 1))
            if King[1] < 7:
                next_to_king.append((King[0], King[1] + 1))
            king_play_indexes = []
            while i < len(valid_moves):
                move = valid_moves.__getitem__(i)
                row = move.start_row
                col = move.start_column
                if move not in gs.allowed_pinned:  # mozda postoji sansa ako 2 puta imam figuru u ovoj listi da moram da izbacim svako njeno pojaljivanje iz iste
                    if (row, col) in gs.pinned:
                        valid_moves.__delitem__(i)
                        continue
                if (row, col) == King:
                    king_play_indexes.append(i)
                i = i + 1
            i = 0
            while i < len(valid_enemy_moves):
                move = valid_enemy_moves.__getitem__(i)
                row = move.start_row
                col = move.start_column
                if gs.board[row][col][1] != "P" and (
                        move.end_row, move.end_column) in next_to_king:  # moram piune da izbacim odavde
                    index = 0
                    while index < len(king_play_indexes):
                        where = king_play_indexes.__getitem__(index)
                        king_move = valid_moves.__getitem__(where)
                        if (king_move.end_row, king_move.end_column) == (move.end_row, move.end_column):
                            valid_moves.__delitem__(where)
                            king_play_indexes.__delitem__(index)
                            pom_brojac = index
                            while pom_brojac < len(king_play_indexes):
                                king_play_indexes[pom_brojac] = king_play_indexes[pom_brojac] - 1
                                pom_brojac = pom_brojac + 1
                            continue
                        index = index + 1
                i = i + 1
            new_valid_moves = []
            print(gs.check_path_to_king)
            if len(gs.check_path_to_king) > 0:
                index = 0
                while index < len(valid_moves):
                    move = valid_moves.__getitem__(index)
                    row = move.end_row
                    col = move.end_column
                    if (move.start_row,move.start_column) == gs.white_king or (move.start_row,move.start_column) == gs.black_king:
                        new_valid_moves.append(move)
                    elif (row, col) in gs.check_path_to_king:
                        new_valid_moves.append(move)
                    index = index + 1
                valid_moves = new_valid_moves
            if len(valid_moves) == 0:
                print("SAH MAT")
                SAH_MAT = True

            gs.check_path_to_king = []
            move_made = False
            king_position = ()
            if gs.whiteToMove and gs.king_check:
                king_position = gs.black_king
            elif not gs.whiteToMove and gs.king_check:
                king_position = gs.white_king
            gs.king_check = False

        drawGameState(screen, gs, possible_moves, king_position)
        clock.tick(MAX_FPS)
        p.display.flip()

        #BOT PLAYING HERE
        if not gs.whiteToMove and not SAH_MAT:
            move = valid_moves.__getitem__(r.randrange(0, len(valid_moves), 1))
            gs.makeMove(move)
            move_made = True


def drawBoard(screen):
    colors = [p.Color(241, 217, 192), p.Color(169, 122, 101)]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPossibleMoves(screen, possiblemoves):
    color = p.Color("green")
    for i in possiblemoves:
        p.draw.circle(screen, color, (i.end_column * SQ_SIZE + SQ_SIZE // 2, i.end_row * SQ_SIZE + SQ_SIZE // 2),
                      SQ_SIZE // 8)


def drawCheck(screen, king_position, board):
    color = p.Color("red")
    if len(king_position) == 2:
        p.draw.rect(screen, color, p.Rect(king_position[1] * SQ_SIZE, king_position[0] * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        screen.blit(IMAGES[board[king_position[0]][king_position[1]]],
                    p.Rect(king_position[1] * SQ_SIZE, king_position[0] * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawGameState(screen, gs, possible_moves, king_position):
    drawBoard(screen)  # nacrtaj kvadratice
    drawPieces(screen, gs.board)  # nacrtaj figure
    drawPossibleMoves(screen, possible_moves)  # nacrtaj polja
    drawCheck(screen, king_position, gs.board)


if __name__ == "__main__":
    main()
