from menu import MenuManager
from pieces import ChessPiece, Pawn
import copy


class Board:
    def __init__(self):
        self.board = [[None] * 8 for _ in range(8)]
        self.white_below = True

        for i in range(8):
            for j in range(8):
                color = 'B' if i < 4 else 'W'

                if i == 0 or i == 7:
                    pieces_on_row = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
                elif i == 1 or i == 6:
                    pieces_on_row = ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P']
                else:
                    pieces_on_row = [None] * 8

                self.board[i][j] = (
                    Pawn(pieces_on_row[j], color, self) if pieces_on_row[j] == "P" else
                    ChessPiece(pieces_on_row[j], color, self) if pieces_on_row[j] else None
                )

    def __str__(self):
        res = ''
        for i in range(8):
            res += ''.join(str(piece) if piece else '.' for piece in self.board[i]) + "\n"
        return res

    def is_path_clear(self, start_pos, end_pos):
        start_x, start_y = start_pos
        end_x, end_y = end_pos

        diff_x = end_x - start_x
        diff_y = end_y - start_y

        step_x = (diff_x // abs(diff_x)) if diff_x != 0 else 0
        step_y = (diff_y // abs(diff_y)) if diff_y != 0 else 0

        x, y = start_x + step_x, start_y + step_y
        while (x, y) != (end_x, end_y):
            if self.board[y][x] is not None:
                return False
            x += step_x
            y += step_y

        return True

    def can_castling(self, king_x, king_y, chess_board, direction, num_of_steps):
        board = chess_board.board
        king = board[king_y][king_x]

        if king.already_moved:
            return False

        try: # когда в validate_moves -1/+1 и 4 - индекс выйдет один раз за пределы доски, так что просто возвращаем False
            rook = board[king_y][king_x + direction * num_of_steps]
            if not rook or rook.name != 'R' or rook.already_moved:
                return False

            way_is_clear = self.is_path_clear((king_x, king_y),
                                              (king_x + direction * num_of_steps, king_y))
            if not way_is_clear:
                return False

            if king.is_king_in_check(king.color, [king_x, king_y]):
                return False

            king_moves_x = [
                king_x + direction,
                king_x + direction * 2
            ]

            for x in king_moves_x:
                board[king_y][x] = king
                if board[king_y][x].is_king_in_check(king.color, [x, king_y]):
                    board[king_y][x] = None
                    return False
                board[king_y][x] = None

            return True

        except IndexError:
            return False


    def move_piece(self, start_pos, end_pos, chess_board, game_logic, menu_manager=None):
        start_x, start_y = start_pos
        end_x, end_y = end_pos
        board = chess_board.board
        beating_suffix = ''

        moving_piece = board[start_y][start_x]
        if not moving_piece:
            raise ValueError("На начальной позиции нет фигуры!")

        if moving_piece.name in ['R', 'B', 'Q']:
            if not self.is_path_clear(start_pos, end_pos):
                raise ValueError("На пути перемещения есть фигуры!")

        record_prefix = moving_piece.name

        if moving_piece.name == 'K':
            if abs(end_x - start_x) == 2:
                direction = (end_x - start_x) // 2

                if (chess_board.white_below and direction == 1) or (chess_board.white_below == False and direction == -1):
                    moving_piece.make_castling(start_x, start_y, chess_board, direction, 3)
                    record_prefix = '0-0'
                else:
                    moving_piece.make_castling(start_x, start_y, chess_board, direction, 4)
                    record_prefix = '0-0-0'

        if isinstance(moving_piece, Pawn):
            white_below = chess_board.white_below
            direction = 1 \
                if ((moving_piece.color == 'W' and white_below) or
                    (moving_piece.color == 'B' and not white_below)) \
                else -1
            if end_x != start_x and board[end_y][end_x] is None:
                en_passant_target_y = end_y + direction
                if 0 <= en_passant_target_y < 8 and 0 <= end_x < 8:
                    captured_piece = board[en_passant_target_y][end_x]

                    if isinstance(captured_piece, Pawn) and captured_piece.color != moving_piece.color and \
                            captured_piece.possibility_of_en_passant:
                        print(f"End positions: end_x={end_x}, end_y={end_y}, direction={direction}")
                        print(f"En passant target: en_passant_target_y={en_passant_target_y}")
                        game_logic.add_points(moving_piece, captured_piece)
                        board[en_passant_target_y][end_x] = None
                        record_prefix = 'EP'
                        beating_suffix = f'{chr(97 + start_y)}x'

        for row in board:
            for piece in row:
                if isinstance(piece, Pawn):
                    piece.possibility_of_en_passant = False

        if isinstance(moving_piece, Pawn) and abs(end_y - start_y) == 2:
            moving_piece.possibility_of_en_passant = True

        target_piece = board[end_y][end_x]
        if target_piece and target_piece.color != moving_piece.color:
            game_logic.add_points(moving_piece, target_piece)
            beating_suffix = f'{chr(97 + start_y)}x' if moving_piece.name == 'P' else 'x'

        board[end_y][end_x] = moving_piece
        board[start_y][start_x] = None
        if isinstance(moving_piece, Pawn):
            if (moving_piece.color == 'W' and end_y == 0) or (moving_piece.color == 'B' and end_y == 7):
                if moving_piece.color == game_logic.player_color:
                    chosen_piece_name = menu_manager.draw_promotion_menu(moving_piece.color)
                    self.promote_pawn(end_x, end_y, chosen_piece_name)
                else:
                    self.promote_pawn(end_x, end_y, chosen_piece_name='Q')

        moving_piece.already_moved = True

        game_logic.record_move(end_pos, record_prefix, beating_suffix) if beating_suffix \
            else game_logic.record_move(end_pos, record_prefix)

    def promote_pawn(self, x, y, chosen_piece_name=None):
        piece = self.board[y][x]
        if isinstance(self.board[y][x], Pawn):
            new_piece_name = chosen_piece_name if chosen_piece_name else 'Q'
            self.board[y][x] = ChessPiece(new_piece_name, piece.color, self)

# AI
    def copy(self):
        new_board = Board()
        new_board.board = copy.deepcopy(self.board)
        new_board.white_below = self.white_below
        return new_board

    def check_game_state(self, game_logic):
        current_turn = game_logic.current_turn
        king_in_check = False

        for row in self.board:
            for piece in row:
                if piece and piece.name == 'K' and piece.color == current_turn:
                    king_in_check = piece.is_king_in_check(current_turn)

        can_move = False
        for y in range(8):
            for x in range(8):
                piece = self.board[y][x]
                if piece and piece.color == current_turn:
                    if piece.validate_moves(x, y):
                        can_move = True
                        break
            if can_move:
                break

        if not can_move:
            if king_in_check:
                return "checkmate"
            return "stalemate"

        return "continue"

    def get_valid_moves(self, current_turn):
        valid_moves = []

        for y in range(8):
            for x in range(8):
                piece = self.board[y][x]
                if piece and piece.color == current_turn:
                    moves = piece.validate_moves(x, y)
                    for move in moves:
                        valid_moves.append(((x, y), tuple(move)))

        return valid_moves

    def to_fen(self, game_logic):
        fen_matrix = ""
        for row in self.board:
            empty_count = 0
            for piece in row:
                if piece is None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        fen_matrix += str(empty_count)
                        empty_count = 0
                    representation = piece.name.upper() if piece.color == 'W' else piece.name.lower()
                    fen_matrix += representation
            if empty_count > 0:
                fen_matrix += str(empty_count)
            fen_matrix += "/"

        fen_matrix = fen_matrix.rstrip("/")

        fen_color = game_logic.current_turn.lower()

        castling_rights = []
        if self.white_below:
            if self.board[7][4] and self.board[7][4].name == 'K' and not self.board[7][4].already_moved:
                if self.board[7][7] and self.board[7][7].name == 'R' and not self.board[7][7].already_moved:
                    castling_rights.append("K")
                if self.board[7][0] and self.board[7][0].name == 'R' and not self.board[7][0].already_moved:
                    castling_rights.append("Q")
            if self.board[0][4] and self.board[0][4].name == 'K' and not self.board[0][4].already_moved:
                if self.board[0][7] and self.board[0][7].name == 'R' and not self.board[0][7].already_moved:
                    castling_rights.append("k")
                if self.board[0][0] and self.board[0][0].name == 'R' and not self.board[0][0].already_moved:
                    castling_rights.append("q")
        else:
            if self.board[0][3] and self.board[0][3].name == 'K' and not self.board[0][3].already_moved:
                if self.board[0][7] and self.board[0][7].name == 'R' and not self.board[0][7].already_moved:
                    castling_rights.append("Q")
                if self.board[0][0] and self.board[0][0].name == 'R' and not self.board[0][0].already_moved:
                    castling_rights.append("K")
            if self.board[7][3] and self.board[7][3].name == 'K' and not self.board[7][3].already_moved:
                if self.board[7][7] and self.board[7][7].name == 'R' and not self.board[7][7].already_moved:
                    castling_rights.append("q")
                if self.board[7][0] and self.board[7][0].name == 'R' and not self.board[7][0].already_moved:
                    castling_rights.append("k")
        fen_castling = "".join(castling_rights) if castling_rights else "-"

        fen_en_passant = "-"
        for y, row in enumerate(self.board):
            for x, piece in enumerate(row):
                if isinstance(piece, Pawn) and piece.possibility_of_en_passant:
                    fen_en_passant = f"{chr(97 + x)}{8 - y - 1}"
                    break

        fen_halfmove = game_logic.half_move_count
        fen_fullmove = len(game_logic.move_history)

        fen_string = f"{fen_matrix} {fen_color} {fen_castling} {fen_en_passant} {fen_halfmove} {fen_fullmove}"
        return fen_string
