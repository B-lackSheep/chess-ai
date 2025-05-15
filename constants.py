import pygame


pygame.init()

FONT_PATH = "Assets/Fonts/Typography Times Bold.ttf"

FONT_TITLE = pygame.font.Font(FONT_PATH, 28)
FONT_TEXT = pygame.font.Font(FONT_PATH, 18)
FONT_LABELS = pygame.font.Font(FONT_PATH, 16)

COLOR_TEXT = (0, 0, 0)
COLOR_TEXT_OUTSIDE_BUTTON = (240, 217, 181)
COLOR_MENU_BG = (46, 42, 36)
COLOR_MENU_BORDER = (240, 217, 181)
COLOR_BUTTON = (240, 217, 181) # Ну или COLOR_MENU_BORDER
COLOR_BUTTON_BORDER = (0, 0, 0)
COLOR_AVATAR_BG = (240, 217, 181) # Ну или COLOR_MENU_BORDER

MENU_SIZE = (320, 320)
ICON_SIZE = (80, 80)
BUTTON_HEIGHT = 50
BUTTON_SMALL_HEIGHT = 40

WINDOW_SIZE = (1280, 640)
WINDOW_TITLE = "Chess"

CELL_SIZE = 80

COLOR_LIGHT_CELLS = (240, 217, 181) # Ну или COLOR_MENU_BORDER
COLOR_DARK_CELLS = (181, 136, 99) # Ну или COLOR_MENU_BG

PIECE_SIZE = 70


COLOR_MOVE_HIGHLIGHT = (200, 200, 200)
MOVE_HIGHLIGHT_RADIUS = 10

PLAYER_DATA = {
    "player": {
        "name": "Player",
        "avatar": "Assets/Avatars/Player.png",
        "elo": 555
    },
    "opponent": {
        "name": "Opponent 1",
        "avatar": "Assets/Avatars/Bot1.png",
        "elo": 250
    }
}
