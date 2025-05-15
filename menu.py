import pygame
from constants import (FONT_TITLE, FONT_TEXT,
                       COLOR_TEXT, COLOR_MENU_BG, COLOR_MENU_BORDER, COLOR_BUTTON, COLOR_BUTTON_BORDER,
                       MENU_SIZE, ICON_SIZE, BUTTON_HEIGHT, BUTTON_SMALL_HEIGHT, COLOR_TEXT_OUTSIDE_BUTTON)


class MenuManager:
    def __init__(self, window):
        self.window = window
        self.menu_size = MENU_SIZE
        self.icon_size = ICON_SIZE


    @staticmethod
    def scale_image(image_path, size):
        image = pygame.image.load(image_path)
        return pygame.transform.scale(image, size)


    def draw_wrapped_text(self, font, text, max_width, menu_x, text_y):
        words = text.split(' ')
        current_line = ""

        for word in words:
            # Проверяем, помещается ли строка с добавленным словом. Как-то слишком сложно?
            test_line = current_line + (' ' if current_line else '') + word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                rendered_line = font.render(current_line, True, COLOR_TEXT_OUTSIDE_BUTTON)
                line_x = menu_x + (self.menu_size[0] // 2 - rendered_line.get_width() // 2)
                self.window.blit(rendered_line, (line_x, text_y))
                text_y += rendered_line.get_height() + 5
                current_line = word

        if current_line:
            rendered_line = font.render(current_line, True, COLOR_TEXT_OUTSIDE_BUTTON)
            line_x = menu_x + (self.menu_size[0] // 2 - rendered_line.get_width() // 2)
            self.window.blit(rendered_line, (line_x, text_y))

        return text_y


    def draw_end_game_menu(self, result, loser_color, player_color, points):
        menu_width, menu_height = self.menu_size
        screen_width, screen_height = self.window.get_size()
        menu_x = (screen_width - menu_width) // 2
        menu_y = (screen_height - menu_height) // 2
        menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)

        pygame.draw.rect(self.window, COLOR_MENU_BG, menu_rect)
        pygame.draw.rect(self.window, COLOR_MENU_BORDER, menu_rect, 5)

        font_title = FONT_TITLE
        font_text = FONT_TEXT

        if result == "checkmate":
            diff = points['W'] - points['B']
            score_text = (
                f" White +{diff} points!" if diff > 0 else
                f" Black +{abs(diff)} points!" if diff < 0 else
                " Draw on points!"
            )

            result_text = "Win!" if player_color != loser_color else "Defeat!"

            full_summary = result_text + score_text # WRONG NAMES??
        elif result == "stalemate":
            full_summary = "Stalemate!"
        else:
            full_summary = "Игра окончена."

        restart_button_width = int(menu_width * 0.85)
        text_y = self.draw_wrapped_text(font_title, full_summary, restart_button_width, menu_x, menu_y + 20)

        text_y += int(menu_height * 0.12)

        player_avatar = self.scale_image('Assets/Avatars/Player.png', self.icon_size)
        bot_avatar = self.scale_image('Assets/Avatars/Bot1.png', self.icon_size)

        self.window.blit(player_avatar, (menu_x + 20, text_y))
        self.window.blit(bot_avatar, (menu_x + menu_width - 20 - self.icon_size[0], text_y))

        vs_text = font_text.render("vs", True, COLOR_TEXT_OUTSIDE_BUTTON)
        vs_x = menu_x + (menu_width // 2 - vs_text.get_width() // 2)
        vs_y = text_y + (self.icon_size[1] // 2 - vs_text.get_height() // 2)
        self.window.blit(vs_text, (vs_x, vs_y))

        restart_button_height = BUTTON_HEIGHT
        restart_button_x = menu_x + (menu_width - restart_button_width) // 2
        restart_button_y = text_y + self.icon_size[1] + 20
        restart_button = pygame.Rect(restart_button_x, restart_button_y, restart_button_width, restart_button_height)

        pygame.draw.rect(self.window, COLOR_BUTTON, restart_button, border_radius=15)
        pygame.draw.rect(self.window, COLOR_BUTTON_BORDER, restart_button, 2, border_radius=15)

        restart_text = font_title.render("Rematch", True, COLOR_TEXT)
        self.window.blit(restart_text, (restart_button.x + restart_button.width // 2 - restart_text.get_width() // 2,
                                        restart_button.y + 10))

        small_button_width = (menu_width - 60) // 2
        small_button_height = BUTTON_SMALL_HEIGHT
        bot_button_x = menu_x + 20
        exit_button_x = menu_x + menu_width - small_button_width - 20
        bot_exit_button_y = restart_button_y + restart_button_height + 20

        bot_button = pygame.Rect(bot_button_x, bot_exit_button_y, small_button_width, small_button_height)
        exit_button = pygame.Rect(exit_button_x, bot_exit_button_y, small_button_width, small_button_height)

        pygame.draw.rect(self.window, COLOR_BUTTON, bot_button, border_radius=10)
        pygame.draw.rect(self.window, COLOR_BUTTON, exit_button, border_radius=10)
        pygame.draw.rect(self.window, COLOR_BUTTON_BORDER, bot_button, 2, border_radius=10)
        pygame.draw.rect(self.window, COLOR_BUTTON_BORDER, exit_button, 2, border_radius=10)

        bot_text = font_text.render("New Bot", True, COLOR_TEXT)
        exit_text = font_text.render("Exit", True, COLOR_TEXT)

        self.window.blit(bot_text, (bot_button.x + bot_button.width // 2 - bot_text.get_width() // 2,
                                    bot_button.y + 10))
        self.window.blit(exit_text, (exit_button.x + exit_button.width // 2 - exit_text.get_width() // 2,
                                     exit_button.y + 10))

        pygame.display.update()

        return restart_button, bot_button, exit_button

    def handle_end_game_menu(self, result, current_turn, player_color, points):
        restart_button, bot_button, exit_button = self.draw_end_game_menu(result, current_turn, player_color, points)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if restart_button.collidepoint(mouse_x, mouse_y):
                        return True
                    elif exit_button.collidepoint(mouse_x, mouse_y):
                        pygame.quit()
                        return False

    def draw_promotion_menu(self, color):
        menu_width = 300
        menu_height = 200
        screen_width, screen_height = self.window.get_size()
        menu_x = (screen_width - menu_width) // 2
        menu_y = (screen_height - menu_height) // 2
        menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)

        pygame.draw.rect(self.window, COLOR_MENU_BG, menu_rect)
        pygame.draw.rect(self.window, COLOR_MENU_BORDER, menu_rect, 5)

        font_title = FONT_TITLE
        promotion_text = "Выберите фигуру для превращения:"
        text = font_title.render(promotion_text, True, COLOR_TEXT_OUTSIDE_BUTTON)
        self.window.blit(text, (menu_x + (menu_width - text.get_width()) // 2, menu_y + 20))

        button_width = 60
        button_height = 60
        piece_options = ['Q', 'R', 'B', 'N']
        buttons = []

        for i, piece_name in enumerate(piece_options):
            button_x = menu_x + 20 + (button_width + 20) * i
            button_y = menu_y + 80
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            pygame.draw.rect(self.window, COLOR_BUTTON, button_rect, border_radius=5)
            pygame.draw.rect(self.window, COLOR_BUTTON_BORDER, button_rect, 2, border_radius=5)

            text = FONT_TEXT.render(piece_name, True, COLOR_TEXT)
            self.window.blit(text, (button_x + (button_width - text.get_width()) // 2,
                                    button_y + (button_height - text.get_height()) // 2))
            buttons.append((button_rect, piece_name))

        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    for button_rect, piece_name in buttons:
                        if button_rect.collidepoint(mouse_x, mouse_y):
                            return piece_name
