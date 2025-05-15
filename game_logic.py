import copy


class GameLogic:
    def __init__(self):
        self.current_turn = 'W'
        self.scores = {'W': 0, 'B': 0}
        self.player_color = 'W'
        self.move_history = []
        self.last_move = None

    def switch_turn(self):
        self.current_turn = 'B' if self.current_turn == 'W' else 'W'
        print(self.scores)

    def is_turn_correct(self, piece):
        if piece is None:
            return False
        return piece.color == self.current_turn

    def add_points(self, moving_piece, enemy_piece):
        self.scores[moving_piece.color] += enemy_piece.attack_dict[enemy_piece.name]['points'] \
            if enemy_piece.name != 'P' \
            else 1

    def record_move(self, end_pos, move_prefix, beating_suffix=''):
        column = chr(97 + end_pos[0])
        row = str(8 - end_pos[1])

        if move_prefix == 'P':
            move_prefix = ''

        position_str = f"{move_prefix}{beating_suffix}{column}{row}"

        if self.current_turn == 'W':
            self.move_history.append([position_str])
        else:
            self.move_history[-1].append(position_str)

    def update_last_move(self, start_pos, end_pos):
        self.last_move = (start_pos, end_pos)

    def copy(self):
        new_game_logic = GameLogic()
        new_game_logic.current_turn = self.current_turn
        new_game_logic.scores = copy.deepcopy(self.scores)
        new_game_logic.player_color = self.player_color
        new_game_logic.move_history = copy.deepcopy(self.move_history)
        new_game_logic.last_move = copy.deepcopy(self.last_move)
        return new_game_logic
