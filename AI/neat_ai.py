import neat
import numpy as np
import chess
import chess.engine


class NeatChessAI:
    def __init__(self, config_path, color):
        self.color = color
        self.config = neat.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            config_path
        )
        self.population = neat.Population(self.config)
        self.engine_path = "D:/Python/Chess/AI/stockfish/stockfish-windows-x86-64-avx2.exe"
        self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)

    def board_to_input(self, chess_board, current_turn):
        inputs = []
        for row in chess_board.board:
            for piece in row:
                if piece is None:
                    inputs.append(0)
                else:
                    value = 1 if piece.color == self.color else -1
                    inputs.append(value)

        additional_input = 1 if chess_board.white_below else -1
        inputs.append(additional_input)

        valid_moves = chess_board.get_valid_moves(current_turn)
        inputs += [1 if (start_pos, end_pos) in valid_moves else 0 for start_pos in range(64) for end_pos in range(64)]

        return inputs

    def evaluate_genome(self, genome, config, chess_board, current_turn):
        inputs = np.array(self.board_to_input(chess_board, current_turn))
        net = neat.nn.FeedForwardNetwork.create(genome, config)

        valid_moves = chess_board.get_valid_moves(current_turn)
        outputs = net.activate(inputs)

        valid_outputs = [-float('inf')] * len(outputs)
        for i, (start_pos, end_pos) in enumerate(valid_moves):
            start_index = start_pos[1] * 8 + start_pos[0]
            end_index = end_pos[1] * 8 + end_pos[0]
            if 0 <= start_index < 64 <= end_index < 128:
                valid_outputs[i] = outputs[i]

        best_move_index = np.argmax(valid_outputs)
        start_pos, end_pos = valid_moves[best_move_index]

        return start_pos, end_pos

    def evaluate_fitness(self, board, result, turn_color, game_logic):
        central_positions = [(3, 3), (3, 4), (4, 3), (4, 4)]
        control_center_bonus = 0

        for y, row in enumerate(board.board):
            for x, piece in enumerate(row):
                if piece and piece.color == turn_color and (x, y) in central_positions:
                    control_center_bonus += 1

        ai_color = self.color
        player_color = 'W' if ai_color == 'B' else 'B'
        ai_points = game_logic.scores[ai_color]
        player_points = game_logic.scores[player_color]

        points_difference_bonus = max(0, ai_points - player_points)

        if result == "win":
            fitness = 100
        elif result == "loss":
            fitness = 0
        else:
            fitness = 50

        return fitness + control_center_bonus + points_difference_bonus

    def make_move(self, chess_board, game_logic):
        for genome_id, genome in self.population.population.items():
            try:
                start_pos, end_pos = self.evaluate_genome(genome, self.config, chess_board, game_logic.current_turn)

                valid_moves = chess_board.get_valid_moves(game_logic.current_turn)
                if (start_pos, end_pos) in valid_moves:
                    chess_board.move_piece(start_pos, end_pos, chess_board, game_logic)
                    game_logic.switch_turn()
                    return
            except (ValueError, IndexError) as e:
                print(f"Ошибка выполнения хода {start_pos}->{end_pos}: {e}")

        for genome_id, genome in self.population.population.items():
            genome.fitness = genome.fitness - 1 if genome.fitness is not None else -1
        print("Не удалось сделать допустимый ход!")

    def simulate_game(self, chess_board, game_logic, net):
        temp_board = chess_board.copy()
        temp_game_logic = game_logic.copy()
        result = None

        for _ in range(100):
            inputs = np.array(self.board_to_input(temp_board, temp_game_logic.current_turn))
            outputs = net.activate(inputs)

            valid_moves = temp_board.get_valid_moves(temp_game_logic.current_turn)

            if not valid_moves:
                result = "draw"
                return result, temp_game_logic

            valid_start_indices, valid_end_indices = set(), set()
            for start_pos, end_pos in valid_moves:
                valid_start_indices.add(start_pos[1] * 8 + start_pos[0])
                valid_end_indices.add(end_pos[1] * 8 + end_pos[0])

            # AI выбор
            valid_choice = False
            try_count = 0  # Ограничиваем количество ошибок
            while not valid_choice:
                start_index = np.argmax(outputs[:64])
                end_index = np.argmax(outputs[64:])

                if try_count > len(valid_moves):  # если больше попыток чем ходов
                    print("Ошибка: AI не может выбрать валидный ход")
                    return "draw", temp_game_logic

                if start_index in valid_start_indices and end_index in valid_end_indices:
                    start_pos, end_pos = (start_index % 8, start_index // 8), (end_index % 8, end_index // 8)
                    valid_choice = True  # Если найдено, завершаем цикл
                else:
                    # Обнуляем выходные данные и обновляем попытку
                    outputs[start_index] = float('-inf')
                    outputs[64 + end_index] = float('-inf')
                    try_count += 1

            # Выполняем ход
            try:
                temp_board.move_piece(start_pos, end_pos, temp_board, temp_game_logic)
            except ValueError as e:
                print(f"Ошибка выполнения хода {start_pos}->{end_pos}: {e}")
                break

            result_state = temp_board.check_game_state(temp_game_logic)
            if result_state == "checkmate":
                result = "win" if temp_game_logic.current_turn != self.color else "loss"
                break
            elif result_state == "stalemate":
                result = "draw"
                break

            temp_game_logic.switch_turn()

        return result, temp_game_logic

    def analyze_position_with_stockfish(self, board, depth=6):
        result = self.engine.analyse(board, chess.engine.Limit(depth=depth))
        return result

    def convert_board_to_chess(self, game_board):
        fen_matrix = ""
        for row in game_board.board:
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

        fen_matrix = fen_matrix.strip("/")
        fen_color = "w" if game_board.white_below else "b"
        fen_castling = "KQkq"  # Упростим, добавив все рокировки (оптимально — интеграция текущих состояний)
        fen_en_passant = "-"  # Сделать "-" при отсутствии.
        fen_halfmove = "0"
        fen_fullmove = "1"

        fen_string = f"{fen_matrix} {fen_color} {fen_castling} {fen_en_passant} {fen_halfmove} {fen_fullmove}"
        return chess.Board(fen_string)
