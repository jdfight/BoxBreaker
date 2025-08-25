"""
This module contains all the game entities.
"""

import pygame
import random
from typing import TYPE_CHECKING, Dict, List
from Box2D.b2 import polygonShape, fixtureDef, dynamicBody, kinematicBody, staticBody

from .constants import SCREEN_WIDTH, SCREEN_HEIGHT, PPM, MAX_BALL_SPEED, MIN_BALL_SPEED, FPS, WHITE

if TYPE_CHECKING:
    from .game import Game
    from .utils import AssetManager


class Paddle(pygame.sprite.Sprite):
    """
    The paddle that the player controls.
    """

    def __init__(self, assets: "AssetManager", world: "world", game: "Game") -> None:
        """
        Initializes the Paddle.

        Args:
            assets: The asset manager.
            world: The Box2D world.
            game: The main game object.
        """
        super().__init__()
        self.assets: "AssetManager" = assets
        self.world: "world" = world
        self.game: "Game" = game
        self.image: pygame.Surface = self.assets.images["paddle"]
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.x = (SCREEN_WIDTH - self.rect.width) // 2
        self.rect.y = SCREEN_HEIGHT - self.rect.height - 10
        self.create_body()

    def create_body(self) -> None:
        """Creates the Box2D body for the paddle."""
        width: float = self.rect.width / 2 / PPM
        height: float = self.rect.height / 2 / PPM

        top_y: float = height
        bottom_y: float = -height
        top_width: float = width
        bottom_width: float = width * 0.8

        vertices: List[tuple[float, float]] = [
            (-top_width, top_y),
            (top_width, top_y),
            (bottom_width, bottom_y),
            (-bottom_width, bottom_y),
        ]

        self.body: "kinematicBody" = self.world.CreateKinematicBody(
            position=(self.rect.centerx / PPM, self.rect.centery / PPM),
            shapes=polygonShape(vertices=vertices),
        )
        self.body.userData = self

    def resize(self, width: float) -> None:
        """
        Resizes the paddle.

        Args:
            width: The new width of the paddle.
        """
        self.body.DestroyFixture(self.body.fixtures[0])

        new_width: float = width / 2 / PPM
        height: float = self.rect.height / 2 / PPM

        top_y: float = height
        bottom_y: float = -height
        top_width: float = new_width
        bottom_width: float = new_width * 0.8

        vertices: List[tuple[float, float]] = [
            (-top_width, top_y),
            (top_width, top_y),
            (bottom_width, bottom_y),
            (-bottom_width, bottom_y),
        ]

        self.body.CreateFixture(
            fixtureDef(
                shape=polygonShape(vertices=vertices)
            )
        )
        self.image = pygame.transform.scale(self.assets.images["paddle"], (int(width), self.rect.height))
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self) -> None:
        """Updates the paddle's position based on the mouse position."""
        mouse_x, _ = self.game._get_scaled_mouse_pos(pygame.mouse.get_pos())
        self.body.position = (mouse_x / PPM, self.body.position.y)
        self.rect.centerx = self.body.position.x * PPM

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draws the paddle on the screen.

        Args:
            surface: The surface to draw on.
        """
        vertices = [(self.body.transform * v) * PPM for v in self.body.fixtures[0].shape.vertices]
        #pygame.draw.polygon(surface, WHITE, vertices)
        surface.blit(self.image, self.rect)


class Ball(pygame.sprite.Sprite):
    """
    The ball that bounces around the screen.
    """

    def __init__(self, assets: "AssetManager", paddle: "Paddle", world: "world", game: "Game") -> None:
        """
        Initializes the Ball.

        Args:
            assets: The asset manager.
            paddle: The paddle object.
            world: The Box2D world.
            game: The main game object.
        """
        super().__init__()
        self.assets: "AssetManager" = assets
        self.paddle: "Paddle" = paddle
        self.world: "world" = world
        self.game: "Game" = game
        self.image: pygame.Surface = self.assets.images["ball"]
        self.rect: pygame.Rect = self.image.get_rect()
        self.state: str = "on_paddle"
        self.is_bomb: bool = False
        self.create_body()
        self.reset()

    def create_body(self) -> None:
        """Creates the Box2D body for the ball."""
        self.body: "dynamicBody" = self.world.CreateDynamicBody(
            position=(self.paddle.rect.centerx / PPM, self.paddle.rect.top / PPM - 1),
        )
        self.body.CreateFixture(
            fixtureDef(
                shape=polygonShape(
                    box=(self.rect.width / 2 / PPM, self.rect.height / 2 / PPM)
                ),
                density=1.0,
                friction=0.0,
                restitution=1.0,
            )
        )
        self.body.linearDamping = 0.0
        self.body.angularDamping = 0.0
        self.body.bullet = True
        self.body.userData = self

    def reset(self) -> None:
        """Resets the ball to its initial state on the paddle."""
        self.state = "on_paddle"
        self.body.linearVelocity = (0, 0)
        self.body.angularVelocity = 0
        self.body.position = (
            self.paddle.body.position.x,
            self.paddle.body.position.y
            - (self.paddle.rect.height / 2 / PPM)
            - (self.rect.height / 2 / PPM),
        )
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)

    def launch(self) -> None:
        """Launches the ball from the paddle."""
        if self.state == "on_paddle":
            self.state = "moving"
            impulse: tuple[float, int] = (random.uniform(-7, 7), -15)
            self.body.ApplyLinearImpulse(impulse, self.body.worldCenter, True)
            self.game.play_sound("sfx-02")
            pygame.event.set_grab(True)
            pygame.mouse.set_visible(False)

    def update(self) -> None:
        """Updates the ball's position."""
        if self.state == "on_paddle":
            self.body.position = (
                self.paddle.body.position.x,
                self.paddle.body.position.y
                - (self.paddle.rect.height / 2 / PPM)
                - (self.rect.height / 2 / PPM),
            )
        elif self.state == "moving":
            vel: "b2Vec2" = self.body.linearVelocity
            speed: float = vel.length
            if speed > MAX_BALL_SPEED:
                self.body.linearVelocity = (MAX_BALL_SPEED / speed) * vel
            elif speed > 0 and speed < MIN_BALL_SPEED:
                self.body.linearVelocity = (MIN_BALL_SPEED / speed) * vel

        self.rect.center = (self.body.position.x * PPM, self.body.position.y * PPM)


class Brick(pygame.sprite.Sprite):
    """
    The bricks that the player needs to destroy.
    """
    BRICK_IMAGES: Dict[int, str] = {
        1: "brick",
        2: "brick_blue",
        3: "brick_gold",
        4: "brick_green",
        5: "brick_orange",
        6: "brick_purple",
        7: "brick_black",
        8: "brick_silver",
    }
    BRICK_PARTICLE_COLORS: Dict[int, str] = {
        1: "red",
        2: "blue",
        3: "yellow",
        4: "green",
        5: "orange",
        6: "purple",
        7: "black",
        8: "silver",
    }

    def __init__(self, assets: "AssetManager", x: int, y: int, hp: int, game: "Game", world: "world") -> None:
        """
        Initializes the Brick.

        Args:
            assets: The asset manager.
            x: The x-coordinate of the brick.
            y: The y-coordinate of the brick.
            hp: The health points of the brick.
            game: The main game object.
            world: The Box2D world.
        """
        super().__init__()
        self.assets: "AssetManager" = assets
        self.hp: int = hp
        self.game: "Game" = game
        self.world: "world" = world
        self.image: pygame.Surface = self.assets.images[self.BRICK_IMAGES.get(self.hp, "brick")]
        self.rect: pygame.Rect = self.image.get_rect(topleft=(x, y))
        self.create_body()

    def create_body(self) -> None:
        """Creates the Box2D body for the brick."""
        self.body: "staticBody" = self.world.CreateStaticBody(
            position=(self.rect.centerx / PPM, self.rect.centery / PPM),
            shapes=polygonShape(
                box=(
                    self.rect.width / 2 / PPM,
                    self.rect.height / 2 / PPM,
                )
            ),
        )
        self.body.userData = self

    def destroy(self) -> None:
        """Destroys the brick."""
        color: str = self.BRICK_PARTICLE_COLORS.get(self.hp, "red")
        for _ in range(5):
            particle: "Particle" = Particle(
                self.assets, self.rect.centerx, self.rect.centery, color
            )
            self.game.all_sprites.add(particle)
            self.game.particles.add(particle)
        if random.random() < 0.2:  # 20% chance of dropping a power-up
            powerup_type: str = random.choice(
                ["ball", "bomb", "gold", "shot", "ballMulti", "life", "grow"]
            )
            powerup: "PowerUp" = PowerUp(
                self.assets, self.rect.centerx, self.rect.centery, powerup_type
            )
            self.game.all_sprites.add(powerup)
            self.game.powerups.add(powerup)
        self.game.play_sound("sfx-01b")
        if(self.body not in self.game.bodies_to_destroy):
            self.game.bodies_to_destroy.append(self.body)
            self.kill()

    def hit(self) -> None:
        """Handles the brick being hit."""
        self.hp -= 1
        if self.hp <= 0:
            self.destroy()
        else:
            self.image = self.assets.images[self.BRICK_IMAGES.get(self.hp, "brick")]
            self.game.play_sound("sfx-05")


class PowerUp(pygame.sprite.Sprite):
    """
    The power-ups that drop from bricks.
    """

    def __init__(self, assets: "AssetManager", x: int, y: int, type: str) -> None:
        """
        Initializes the PowerUp.

        Args:
            assets: The asset manager.
            x: The x-coordinate of the power-up.
            y: The y-coordinate of the power-up.
            type: The type of the power-up.
        """
        super().__init__()
        self.assets: "AssetManager" = assets
        self.type: str = type
        if type == "life":
            self.image: pygame.Surface = self.assets.images["bonus_paddle"]
        else:
            self.image = self.assets.images[f"bonus_{self.type}"]
        self.rect: pygame.Rect = self.image.get_rect(center=(x, y))
        self.vy: int = 2

    def update(self) -> None:
        """Updates the power-up's position."""
        self.rect.y += self.vy
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Particle(pygame.sprite.Sprite):
    """
    The particles that are created when a brick is destroyed.
    """

    def __init__(self, assets: "AssetManager", x: int, y: int, color: str) -> None:
        """
        Initializes the Particle.

        Args:
            assets: The asset manager.
            x: The x-coordinate of the particle.
            y: The y-coordinate of the particle.
            color: The color of the particle.
        """
        super().__init__()
        self.assets: "AssetManager" = assets
        self.image: pygame.Surface = random.choice(self.assets.particle_images[color])
        self.rect: pygame.Rect = self.image.get_rect(center=(x, y))
        self.vx: float = random.uniform(-2, 2)
        self.vy: float = random.uniform(-5, 0)
        self.gravity: float = 0.1
        self.life: int = FPS * 2  # 2 seconds

    def update(self) -> None:
        """Updates the particle's position."""
        self.vy += self.gravity
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.life -= 1
        if self.life <= 0:
            self.kill()


class Bullet(pygame.sprite.Sprite):
    """
    The bullets that the player can shoot.
    """

    def __init__(self, assets: "AssetManager", x: int, y: int, world: "world", game: "Game") -> None:
        """
        Initializes the Bullet.

        Args:
            assets: The asset manager.
            x: The x-coordinate of the bullet.
            y: The y-coordinate of the bullet.
            world: The Box2D world.
            game: The main game object.
        """
        super().__init__()
        self.assets: "AssetManager" = assets
        self.world: "world" = world
        self.game: "Game" = game
        self.image: pygame.Surface = self.assets.images["bullet"]
        self.rect: pygame.Rect = self.image.get_rect(center=(x, y))
        self.create_body()

    def create_body(self) -> None:
        """Creates the Box2D body for the bullet."""
        self.body: "dynamicBody" = self.world.CreateDynamicBody(
            position=(self.rect.centerx / PPM, self.rect.centery / PPM),
            bullet=True,
        )
        self.body.CreateFixture(
            fixtureDef(
                shape=polygonShape(
                    box=(self.rect.width / 2 / PPM, self.rect.height / 2 / PPM)
                ),
                isSensor=True,
            )
        )
        self.body.linearVelocity = (0, -20)
        self.body.userData = self

    def update(self) -> None:
        """Updates the bullet's position."""
        self.rect.center = (self.body.position.x * PPM, self.body.position.y * PPM)
        if self.rect.bottom < 0:
            if self.body not in self.game.bodies_to_destroy:
                self.game.bodies_to_destroy.append(self.body)
                self.kill()
