# gamestate.py
from enum import Enum

class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    AI_THINKING = "ai_thinking"
    GAME_OVER = "game_over"
    WIN = "win"
    PAUSED = "paused"