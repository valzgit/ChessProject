import pygame as p
import random as r
from Chess import ChessEngine

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}


def loadImages():
    pieces = ["wP", "wR", "wK", "wB", "wN", "wQ", "bP", "bR", "bK", "bB", "bN", "bQ"]
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
                if not gs.whiteToMove:
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
            valid_moves, valid_enemy_moves = gs.getValidMoves()

            # u ovom delu se obradjuje pat , sah mat i pitanje korisnika da li zeli da igra novu igru
            if len(valid_moves) == 0 and gs.king_check:
                print("SAH MAT")
                SAH_MAT = True
            elif len(valid_moves) == 0:
                SAH_MAT = True
                print("PAT")
            if gs.notEaten >= 50:
                SAH_MAT = True
                print("REMI (50 poteza bez pomeranja piuna ili jedenja figura)")

            move_made = False
            king_position = gs.getKingPosition()

        drawGameState(screen, gs, possible_moves, king_position)
        clock.tick(MAX_FPS)
        p.display.flip()

        # BOT PLAYING HERE
        if not gs.whiteToMove and not SAH_MAT:
            move = valid_moves.__getitem__(r.randrange(0, len(valid_moves), 1))
            gs.makeMove(move)
            move_made = True
        # elif gs.whiteToMove and not SAH_MAT:  # ovde je suprotno pise whitetomove al igra crni
        #     move = valid_moves.__getitem__(r.randrange(0, len(valid_moves), 1))
        #     gs.makeMove(move)
        #     move_made = True


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
