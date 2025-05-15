import pygame
from pygame import *
from board import Board
from game_logic import GameLogic
from menu import MenuManager
from AI.neat_ai import NeatChessAI
from constants import (WINDOW_SIZE, WINDOW_TITLE,
                       CELL_SIZE, COLOR_LIGHT_CELLS, COLOR_DARK_CELLS, COLOR_TEXT,
                       PIECE_SIZE, FONT_LABELS, COLOR_MOVE_HIGHLIGHT, MOVE_HIGHLIGHT_RADIUS, FONT_TEXT, COLOR_MENU_BG,
                       COLOR_MENU_BORDER, PLAYER_DATA, COLOR_TEXT_OUTSIDE_BUTTON)


def init_window():
    pygame.init()
    wind = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()
    return wind, clock


def create_rect_list():
    rect_list = []
    for i in range(8):
        for n in range(4):
            rect_list.append(pygame.Rect((n * 160 + (i % 2) * 80, i * 80, 80, 80))) # Заменять магические числа?

    return rect_list


def draw_panel(wind, player_data, scores, side, move_history=None):
    panel_width = 320
    panel_height = 640
    avatar_size = 100

    panel_x = 0 if side == "left" else (WINDOW_SIZE[0] - panel_width)

    pygame.draw.rect(wind, COLOR_MENU_BG, (panel_x, 0, panel_width, panel_height))
    pygame.draw.rect(wind, COLOR_MENU_BORDER, (panel_x, 0, panel_width, panel_height), 2)

    avatar_x = panel_x + (panel_width - avatar_size) // 2
    avatar_y = 40

    avatar = pygame.image.load(player_data["avatar"])
    avatar = pygame.transform.scale(avatar, (avatar_size, avatar_size))
    wind.blit(avatar, (avatar_x, avatar_y))

    name_text = FONT_TEXT.render(player_data["name"], True, COLOR_TEXT_OUTSIDE_BUTTON)
    name_x = panel_x + (panel_width - name_text.get_width()) // 2
    name_y = avatar_y + avatar_size + 20
    wind.blit(name_text, (name_x, name_y))

    elo_text = FONT_TEXT.render(f"Elo: {player_data['elo']}", True, COLOR_TEXT_OUTSIDE_BUTTON)
    elo_x = panel_x + (panel_width - elo_text.get_width()) // 2
    elo_y = name_y + name_text.get_height() + 10
    wind.blit(elo_text, (elo_x, elo_y))

    score_text = FONT_TEXT.render(f"Points: {scores}", True, COLOR_TEXT_OUTSIDE_BUTTON)
    score_x = panel_x + (panel_width - score_text.get_width()) // 2
    score_y = elo_y + elo_text.get_height() + 10
    wind.blit(score_text, (score_x, score_y))

    if move_history:
        moves_title = FONT_TEXT.render("History of moves", True, COLOR_TEXT_OUTSIDE_BUTTON)
        moves_x = panel_x + (panel_width - moves_title.get_width()) // 2
        moves_y = score_y + 50
        wind.blit(moves_title, (moves_x, moves_y))

        text_y = moves_y + moves_title.get_height() + 10
        for idx, move_pair in enumerate(move_history, start=1):
            move_text = f"{idx}. {' '.join(move_pair)}"
            move_text_surface = FONT_TEXT.render(move_text, True, COLOR_TEXT_OUTSIDE_BUTTON)
            wind.blit(move_text_surface, (panel_x + 10, text_y))
            text_y += move_text_surface.get_height() + 5


def draw_board(board, wind):
    pygame.draw.rect(wind, COLOR_DARK_CELLS, (320, 0, WINDOW_SIZE[0] - 640, WINDOW_SIZE[1]))

    for row in range(8):
        for col in range(8):
            x = col * CELL_SIZE + 320
            y = row * CELL_SIZE
            cell_color = COLOR_LIGHT_CELLS if (row + col) % 2 == 0 else COLOR_DARK_CELLS
            pygame.draw.rect(wind, cell_color, (x, y, CELL_SIZE, CELL_SIZE))

    labels_x = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    labels_y = ['8', '7', '6', '5', '4', '3', '2', '1']

    if not board.white_below:
        labels_x = labels_x[::-1]
        labels_y = labels_y[::-1]

    for idx, label in enumerate(labels_x):
        text = FONT_LABELS.render(label, True, COLOR_TEXT)
        x_pos = 320 + idx * CELL_SIZE + (CELL_SIZE - text.get_width()) * 0.95
        y_pos = 640 - text.get_height() - 5
        wind.blit(text, (x_pos, y_pos))

    for idx, label in enumerate(labels_y):
        text = FONT_LABELS.render(label, True, COLOR_TEXT)
        x_pos = 340 - text.get_width() - 5
        y_pos = idx * CELL_SIZE + (CELL_SIZE - text.get_height()) // 2
        wind.blit(text, (x_pos, y_pos))

    for row in range(8):
        for col in range(8):
            piece = board.board[row][col]
            if piece:
                image_path = f"Assets/Pieces/{piece}.png"
                try:
                    piece_image = pygame.image.load(image_path)
                    piece_image = pygame.transform.scale(piece_image, (PIECE_SIZE, PIECE_SIZE))
                    x = col * CELL_SIZE + 320 + (CELL_SIZE - PIECE_SIZE) * 0.2
                    y = row * CELL_SIZE + (CELL_SIZE - PIECE_SIZE) // 2
                    wind.blit(piece_image, (x, y))
                except pygame.error:
                    print(f"Ошибка при загрузке изображения: {image_path}")

    pygame.display.update()



def draw_circles(moves, wind):
    for circle in moves:
        pygame.draw.circle(wind, COLOR_MOVE_HIGHLIGHT,
                           (circle[0]*CELL_SIZE+CELL_SIZE//2 + 320, circle[1]*CELL_SIZE+CELL_SIZE//2),
                           MOVE_HIGHLIGHT_RADIUS)
    display.update()


def main():
    wind, clock = init_window()
    chess_board = Board()
    game_logic = GameLogic()
    menu_manager = MenuManager(wind)
    ai_player = NeatChessAI('AI/config.txt', color='B')

    moves = []
    selected_piece = None
    start_pos = []

    game_running = True
    while game_running:
        if game_logic.current_turn == 'B':  # Ход AI
            print(game_logic.current_turn)
            ai_player.make_move(chess_board, game_logic)

        game_state = chess_board.check_game_state(game_logic)

        if game_state in ["checkmate", "stalemate"]:
            result = "checkmate" if game_state == "checkmate" else "stalemate"
            restart = menu_manager.handle_end_game_menu(result, game_logic.current_turn, game_logic.player_color,
                                                        game_logic.scores)
            if restart:
                chess_board = Board()
                game_logic = GameLogic()
            else:
                game_running = False
        else:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    game_running = False
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    clicked_x = mouse_x // CELL_SIZE
                    clicked_y = mouse_y // CELL_SIZE

                    if clicked_x in range(4, 12):
                        clicked_x -= 4
                        if moves and [clicked_x, clicked_y] in moves: # ход
                            chess_board.move_piece(start_pos, (clicked_x, clicked_y), chess_board, game_logic)
                            game_logic.switch_turn()
                            game_state = selected_piece.checkmate_stalemate(game_logic.current_turn)

                            if game_state == 1 or game_state == 0:
                                result = "checkmate" if game_state == 1 else "stalemate"
                                restart = (menu_manager.handle_end_game_menu
                                           (result, game_logic.current_turn, game_logic.player_color, game_logic.scores))
                                if restart:
                                    chess_board = Board()
                                    game_logic = GameLogic()
                                    moves = []
                                    selected_piece = None
                                    start_pos = []
                                else:
                                    game_running = False

                            moves = []
                            selected_piece = None
                            start_pos = []
                        else:
                            selected_piece = chess_board.board[clicked_y][clicked_x]
                            if (selected_piece
                                    and game_logic.is_turn_correct(selected_piece)
                                    and selected_piece.name in ['R', 'N', 'B', 'Q', 'K', 'P']):
                                # Если кликнули на фигуру, но не на возможный код, также может лишняя проверка на name...
                                moves = selected_piece.validate_moves(clicked_x, clicked_y)
                                start_pos = (clicked_x, clicked_y)

                            else:
                                moves = []
                                selected_piece = None
                                start_pos = []
                    else:
                        continue

        draw_panel(wind, PLAYER_DATA["player"], game_logic.scores['W'], "left")
        draw_panel(wind, PLAYER_DATA["opponent"], game_logic.scores['B'], "right", game_logic.move_history)
        draw_board(chess_board, wind)
        if moves:
            draw_circles(moves, wind)

        clock.tick(60)