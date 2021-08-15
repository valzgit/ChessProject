import pygame as p
import random as r
import serial
from Chess import ChessEngine
from Chess import Bot

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}


#arduinoData = serial.Serial('COM3', 9600)
#arduinoData.timeout = 1

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
    bot1 = Bot.SagaBot(gs)
    bot2 = Bot.SagaBot(gs)
    valid_moves, valid_enemy_moves, white_protect_list, black_protect_list = gs.getValidMoves()
    move_made = False
    loadImages()  # only once
    running = True
    square_selected = ()
    playerClicks = []
    gamemode = 1
    move_start_end_pos = []
    start_time = p.time.get_ticks()
    print(start_time)
    white_play_time = 0
    black_play_time = 0
    time_limit = 30 * 60 * 1000 # 30 minuta puta 60 sekundi puta 1000 milisekundi
    while running:
        if gs.num_of_played_moves == 0:
            start_time = p.time.get_ticks()
        if gs.whiteToMove and gs.num_of_played_moves > 0 and not SAH_MAT:
            play_time = p.time.get_ticks() - start_time
            white_play_time += play_time
            start_time = p.time.get_ticks()
            print(str(gs.num_of_played_moves) + " WHITE TIME IS " + str(play_time/1000) + " SECONDS AND LIMIT IS " + str(time_limit/1000))
            if white_play_time > time_limit:
                running = False
                print("BLACK WON (TIMES UP FOR WHITE)")
        if not gs.whiteToMove and gs.num_of_played_moves > 0 and not SAH_MAT:
            play_time = p.time.get_ticks() - start_time
            black_play_time += play_time
            start_time = p.time.get_ticks()
            print(str(gs.num_of_played_moves) + " BLACK TIME IS " + str(play_time/1000) + " SECONDS AND LIMIT IS " + str(time_limit/1000))
            if black_play_time > time_limit:
                running = False
                print("WHITE WON (TIMES UP FOR BLACK)")

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
                        move_start_end_pos = [(move.start_row, move.start_column), (move.end_row, move.end_column)]
                        gs.makeMove(move)
                        value = move.start_row * 1000 + move.start_column * 100 + move.end_row * 10 + move.end_column
                        #arduinoData.write(str(value).encode())
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
                elif e.key == p.K_ESCAPE:
                    running = False
                elif e.key == p.K_1:
                    gamemode = 1  # covek vs covek
                    print("MAN VS MAN")
                elif e.key == p.K_2:
                    gamemode = 2  # covek vs bot
                    print("MAN VS BOT")
                elif e.key == p.K_3:
                    gamemode = 3  # bot(random) vs bot (razvijeni)
                    print("BOT VS WEAKER BOT")
                elif e.key == p.K_4:
                    gamemode = 4  # bot (razvijeni) vs bot (razvijeni)
                    print("BOT VS BOT")
                elif e.key == p.K_7:
                    time_limit = 30 * 60 * 1000 # 30 minuta puta 60 sekundi puta 1000 milisekundi CLASSICAL
                    print("CLASSICAL (30 MIN)")
                elif e.key == p.K_8:
                    time_limit = 10 * 60 * 1000 # 10 minuta puta 60 sekundi puta 1000 milisekundi RAPID
                    print("RAPID (10 MIN)")
                elif e.key == p.K_9:
                    time_limit = 5 * 60 * 1000 # 5 minuta puta 60 sekundi puta 1000 milisekundi BLITZ
                    print("BLITZ (5 MIN)")
                elif e.key == p.K_0:
                    time_limit = 1 * 60 * 1000 # 1 minut puta 60 sekundi puta 1000 milisekundi BULLET
                    print("BULLET (1 MIN)")
                elif e.key == p.K_h:
                    move = bot1.calculateMoves(valid_moves, valid_enemy_moves, white_protect_list, black_protect_list,
                                               gs.whiteToMove)
                    value = 10000 + move.start_row * 1000 + move.start_column * 100 + move.end_row * 10 + move.end_column
                    #arduinoData.write(str(value).encode())
                    print("HELP FROM BOT")

        if move_made:
            valid_moves, valid_enemy_moves, white_protect_list, black_protect_list = gs.getValidMoves()

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

        drawGameState(screen, gs, possible_moves, king_position, move_start_end_pos)
        clock.tick(MAX_FPS)
        p.display.flip()

        # BOT PLAYING HERE
        if not gs.whiteToMove and not SAH_MAT:
            if gamemode >= 2:
                move = bot1.calculateMoves(valid_moves, valid_enemy_moves, white_protect_list, black_protect_list,
                                           gs.whiteToMove)
                move_start_end_pos = [(move.start_row, move.start_column), (move.end_row, move.end_column)]
                gs.makeMove(move)
                move_made = True
        elif gs.whiteToMove and not SAH_MAT:
            if gamemode == 3:  # random bot
                move = valid_moves.__getitem__(r.randrange(0, len(valid_moves), 1))
                move_start_end_pos = [(move.start_row, move.start_column), (move.end_row, move.end_column)]
                gs.makeMove(move)
                move_made = True
            elif gamemode == 4:
                move = bot2.calculateMoves(valid_moves, valid_enemy_moves, white_protect_list, black_protect_list,
                                           gs.whiteToMove)
                move_start_end_pos = [(move.start_row, move.start_column), (move.end_row, move.end_column)]
                gs.makeMove(move)
                move_made = True


def drawBoard(screen, move_start_end_pos):
    colors = [p.Color(241, 217, 192), p.Color(169, 122, 101)]
    move_color = p.Color(0, 100, 0)
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
            if len(move_start_end_pos) > 0 and (r, c) == move_start_end_pos[0]:
                p.draw.rect(screen, move_color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
                p.draw.rect(screen, color, p.Rect(c * SQ_SIZE + 2, r * SQ_SIZE + 2, SQ_SIZE - 4, SQ_SIZE - 4))
            elif len(move_start_end_pos) > 0 and (r, c) == move_start_end_pos[1]:
                p.draw.rect(screen, move_color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
                p.draw.rect(screen, color, p.Rect(c * SQ_SIZE + 2, r * SQ_SIZE + 2, SQ_SIZE - 4, SQ_SIZE - 4))


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


def drawGameState(screen, gs, possible_moves, king_position, move_start_end_pos):
    drawBoard(screen, move_start_end_pos)  # nacrtaj kvadratice
    drawPieces(screen, gs.board)  # nacrtaj figure
    drawPossibleMoves(screen, possible_moves)  # nacrtaj polja
    drawCheck(screen, king_position, gs.board)


if __name__ == "__main__":
    main()
