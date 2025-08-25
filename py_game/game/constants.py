"""
This module contains all the constants used in the game.
"""

import os

# --- Constants ---
SCREEN_WIDTH: int = 640
SCREEN_HEIGHT: int = 480
TITLE: str = "Box Breaker"
FPS: int = 60
PPM: float = 20.0  # Pixels per meter
MIN_BALL_SPEED: int = 13
MAX_BALL_SPEED: int = 20

# --- Colors ---
WHITE: tuple[int, int, int] = (255, 255, 255)
BLACK: tuple[int, int, int] = (0, 0, 0)

# --- Paths ---
BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR: str = os.path.join(BASE_DIR, "..", "res")
IMAGE_DIR: str = os.path.join(ASSET_DIR, "pixmaps")
SOUND_DIR: str = os.path.join(ASSET_DIR, "audio")
MAP_DIR: str = os.path.join(BASE_DIR, "..", "maps")
