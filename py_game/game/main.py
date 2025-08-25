"""
This module is the main entry point for the game.
"""
from .game import Game


def main() -> None:
    """
    The main function for the game.
    """
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
