"""
This module contains utility classes for the game.
"""

import pygame
import os
from typing import Dict, List, Tuple
from .constants import IMAGE_DIR, SOUND_DIR, MAP_DIR


class AssetManager:
    """A class to manage loading and storing game assets."""

    def __init__(self) -> None:
        """Initializes the AssetManager."""
        self.images: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.particle_images: Dict[str, List[pygame.Surface]] = {
            "red": [],
            "blue": [],
            "yellow": [],
            "green": [],
            "orange": [],
            "purple": [],
            "black": [],
            "silver": [],
        }
        self.load_assets()

    def load_assets(self) -> None:
        """Load all images and sounds."""
        for filename in os.listdir(IMAGE_DIR):
            if filename.endswith(".png"):
                name: str = os.path.splitext(filename)[0]
                try:
                    image: pygame.Surface = pygame.image.load(
                        os.path.join(IMAGE_DIR, filename)
                    ).convert_alpha()
                    self.images[name] = image
                    if name.startswith("p") and "_" in name:
                        parts: List[str] = name.split("_")
                        if (
                            len(parts) == 2
                            and parts[0].startswith("p")
                            and parts[0][1:].isdigit()
                        ):
                            color: str = parts[1]
                            if color in self.particle_images:
                                self.particle_images[color].append(image)
                    elif name.startswith("p") and name[1:].isdigit():
                        self.particle_images["red"].append(image)
                except pygame.error as e:
                    print(f"Failed to load image {filename}: {e}")
        try:
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.mixer.init()
            for filename in os.listdir(SOUND_DIR):
                if filename.endswith(".mp3"):
                    name = os.path.splitext(filename)[0]
                    sound: pygame.mixer.Sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, filename))
                    self.sounds[name] = sound
        except pygame.error as e:
            print(f"Failed to initialize mixer or load sound: {e}")


class MapLoader:
    """A class to load and manage game maps."""

    def __init__(self) -> None:
        """Initializes the MapLoader."""
        self.maps: List[List[List[int]]] = []
        self.max_level: int = 0
        self.load_maps()

    def load_maps(self) -> None:
        """Load all maps from the maps directory."""
        map_files: List[str] = sorted(
            [f for f in os.listdir(MAP_DIR) if f.startswith("map.")],
            key=lambda x: int(x.split(".")[1]),
        )
        self.max_level = len(map_files)
        for filename in map_files:
            try:
                with open(os.path.join(MAP_DIR, filename), "r") as f:
                    level_map: List[List[int]] = []
                    for line in f:
                        row: List[int] = [int(char) for char in line.strip() if char.isdigit()]
                        if row:
                            level_map.append(row)
                    self.maps.append(level_map)
            except (IOError, ValueError) as e:
                print(f"Failed to load or parse map {filename}: {e}")

    def get_map(self, level_index: int) -> List[List[int]] | None:
        """
        Returns the map for the given level index.

        Args:
            level_index: The index of the level to return.

        Returns:
            The map for the given level index, or None if the level does not exist.
        """
        if 0 <= level_index < len(self.maps):
            return self.maps[level_index]
        return None
