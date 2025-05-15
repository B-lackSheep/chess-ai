class ChessPiece:
    attack_dict = {
        'R': {'directions': [[0, 1], [1, 0], [0, -1], [-1, 0]], 'max_steps': 7, 'points': 5},
        'B': {'directions': [[1, 1], [-1, -1], [1, -1], [-1, 1]], 'max_steps': 7, 'points': 3},
        'Q': {'directions': [[1, 1], [-1, -1], [1, -1], [-1, 1], [0, 1], [1, 0], [0, -1], [-1, 0]],
              'max_steps': 7, 'points': 9},
        'N': {'directions': [[1, 2], [2, 1], [-1, -2], [-2, -1], [-1, 2], [-2, 1], [1, -2], [2, -1]],
              'max_steps': 1, 'points': 3},
        'K': {'directions': [[1, 1], [-1, -1], [1, -1], [-1, 1], [0, 1], [1, 0], [0, -1], [-1, 0]],
              'max_steps': 1}
    }


    def __init__(self, name, color, board):
        self.color = color
        self.already_moved = False
        self.name = name
        self.board = board

    def __str__(self):
        return self.name + self.color

    def get_moves(self, x, y):
        attack_dict = ChessPiece.attack_dict[self.name]
        moves = []
        board = self.board.board
        attack = attack_dict['directions']
        max_steps = attack_dict['max_steps']

        for direction in attack:
            pos = [x, y]
            for _ in range(max_steps):
                pos[0] += direction[0]
                pos[1] += direction[1]

                if not (0 <= pos[0] < 8 and 0 <= pos[1] < 8):
                    break

                under_attack = board[pos[1]][pos[0]]
                if under_attack:
                    if under_attack.name == 'K' and under_attack.color != self.color:
                        moves.append(pos[:])
                    elif under_attack.color != self.color:
                        moves.append(pos[:])
                    break

                moves.append(pos[:])

        return moves


    def validate_moves(self, x, y):
        board = self.board.board
        piece = board[y][x]

        if not piece:
            return []

        moves = piece.get_moves(x, y)
        valid_moves = []

        for move in moves:
            remember = board[move[1]][move[0]]
            board[y][x] = None
            board[move[1]][move[0]] = piece

            if not self.is_king_in_check(piece.color):
                valid_moves.append(move)

            board[move[1]][move[0]] = remember
            board[y][x] = piece

        if piece.name == 'K':
            for direction in [-1, 1]:
                for num_of_steps in [3, 4]:
                    if self.board.can_castling(x, y, self.board, direction, num_of_steps):
                        valid_moves.append([x + direction * 2, y])

        return valid_moves

    def make_castling(self, king_x, king_y, chess_board, direction, num_of_steps):
        board = chess_board.board
        king = board[king_y][king_x]
        rook = board[king_y][king_x + direction * num_of_steps]

        king_steps = 2
        king_target_x = king_x + direction * king_steps
        rook_target_x = king_x + direction

        board[king_y][rook_target_x] = rook
        board[king_y][king_target_x] = king
        board[king_y][king_x] = None
        board[king_y][king_x + direction * num_of_steps] = None


    def is_king_in_check(self, color, king_position=None):
        board = self.board.board

        if not king_position:
            king_position = None
            for y in range(8):
                for x in range(8):
                    piece = board[y][x]
                    if piece and piece.name == 'K' and piece.color == color:
                        king_position = [x, y]
                        break
                if king_position:
                    break

        for y in range(8):
            for x in range(8):
                attacker = board[y][x]
                if attacker and attacker.color != color:
                    if king_position in attacker.get_moves(x, y):
                        return True

        return False


    def checkmate_stalemate(self, color):
        board = self.board.board
        king_in_check = self.is_king_in_check(color)

        for y in range(8):
            for x in range(8):
                if board[y][x] and board[y][x].color == color:
                    if self.validate_moves(x, y):
                        return None
        if king_in_check:
            return 1
        return 0


class Pawn(ChessPiece):
    def __init__(self, name, color, board):
        super().__init__(name, color, board)
        self.possibility_of_en_passant = False

    def can_en_passant(self, board, current_row, last_move):
        column_char = last_move[0]
        row_char = last_move[1]

        column = ord(column_char) - ord('a')
        row = 8 - int(row_char)

        attacked_piece = board[row][column]

        if current_row == row and attacked_piece.name == 'P' and attacked_piece.color != self.color:
            return True

        return False

    def get_moves(self, x, y):
        moves = []
        board = self.board.board

        white_below = self.board.white_below
        direction = -1 \
            if ((self.color == 'W' and white_below) or
                (self.color == 'B' and not white_below)) \
            else 1

        move_forward = y + direction
        if 0 <= move_forward < 8 and board[move_forward][x] is None:
            moves.append([x, move_forward])
            if not self.already_moved and board[move_forward + direction][x] is None:
                moves.append([x, move_forward + direction])

        for diff_x in [-1, 1]:
            attacked_x = x + diff_x
            if 0 <= attacked_x < 8 and 0 <= move_forward < 8:
                enemy_piece = board[move_forward][attacked_x]
                if enemy_piece and enemy_piece.color != self.color:
                    moves.append([attacked_x, move_forward])

                behind_piece = board[y][attacked_x]
                if behind_piece and isinstance(behind_piece, Pawn) and behind_piece.color != self.color and \
                        behind_piece.possibility_of_en_passant:
                    moves.append([attacked_x, move_forward])

        return moves
