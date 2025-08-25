"""
This module contains the main game logic.
"""

import pygame
import sys
import os
from typing import List, Tuple
from Box2D.b2 import world, polygonShape, staticBody, dynamicBody, kinematicBody, contactListener, contact

from .constants import SCREEN_WIDTH, SCREEN_HEIGHT, TITLE, FPS, PPM, WHITE, BLACK
from .utils import AssetManager, MapLoader
from .entities import Paddle, Ball, Brick, Bullet, PowerUp, Particle


class GameContactListener(contactListener):
    """
    Handles collisions between game objects.
    """

    def __init__(self, game: "Game") -> None:
        """
        Initializes the GameContactListener.

        Args:
            game: The main game object.
        """
        super().__init__()
        self.game: "Game" = game

    def BeginContact(self, contact: contact) -> None:
        """
        Called when two fixtures begin to touch.

        Args:
            contact: The contact object.
        """
        fixture_a = contact.fixtureA
        fixture_b = contact.fixtureB
        body_a = fixture_a.body
        body_b = fixture_b.body

        sprite_a = body_a.userData
        sprite_b = body_b.userData

        if sprite_a and sprite_b:
            if isinstance(sprite_a, Ball) and isinstance(sprite_b, Brick):
                self.game.handle_ball_brick_collision(sprite_a, sprite_b)
            elif isinstance(sprite_b, Ball) and isinstance(sprite_a, Brick):
                self.game.handle_ball_brick_collision(sprite_b, sprite_a)
            elif isinstance(sprite_a, Ball) and sprite_b == "floor":
                self.game.handle_ball_floor_collision(sprite_a)
            elif isinstance(sprite_b, Ball) and sprite_a == "floor":
                self.game.handle_ball_floor_collision(sprite_b)
            elif isinstance(sprite_a, Bullet) and isinstance(sprite_b, Brick):
                self.game.handle_bullet_brick_collision(sprite_a, sprite_b)
            elif isinstance(sprite_b, Bullet) and isinstance(sprite_a, Brick):
                self.game.handle_bullet_brick_collision(sprite_b, sprite_a)


class Game:
    """Main class for the game."""

    def __init__(self) -> None:
        """Initializes the game."""
        pygame.init()
        self.screen: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        self.game_surface: pygame.Surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.assets: AssetManager = AssetManager()
        self.map_loader: MapLoader = MapLoader()
        self.font: pygame.font.Font = pygame.font.Font(None, 36)
        self.game_mode: str = "start_menu"
        self.bodies_to_destroy: List["b2Body"] = []
        self.should_create_new_ball: bool = False
        self.paddle_resize_needed: bool = False
        self.save_path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "savegame.dat")
        self.score: int = 0
        self.lives: int = 0
        self.current_level: int = 0
        self.ammo: int = 0
        self.grow_active: bool = False
        self.score_val: int = -1
        self.lives_val: int = -1
        self.ammo_val: int = -1
        self.score_text: pygame.Surface | None = None
        self.lives_text: pygame.Surface | None = None
        self.ammo_text: pygame.Surface | None = None
        self._setup_buttons()
        self._setup_physics()

    def play_sound(self, sound_name: str) -> None:
        """
        Play a sound if it exists.

        Args:
            sound_name: The name of the sound to play.
        """
        if sound_name in self.assets.sounds:
            self.assets.sounds[sound_name].play()

    def _get_scaled_mouse_pos(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        """
        Scales the mouse position to the game surface coordinates.

        Args:
            pos: The mouse position.

        Returns:
            The scaled mouse position.
        """
        screen_width, screen_height = self.screen.get_size()
        scale: float = min(screen_width / SCREEN_WIDTH, screen_height / SCREEN_HEIGHT)
        scaled_width: int = int(SCREEN_WIDTH * scale)
        scaled_height: int = int(SCREEN_HEIGHT * scale)
        pos_x: float = (screen_width - scaled_width) / 2
        pos_y: float = (screen_height - scaled_height) / 2

        mouse_x, mouse_y = pos
        unscaled_x: float = (mouse_x - pos_x) / scale
        unscaled_y: float = (mouse_y - pos_y) / scale

        return int(unscaled_x), int(unscaled_y)

    def _setup_buttons(self) -> None:
        """Create rects for menu buttons."""
        self.new_game_button_rect: pygame.Rect = self.assets.images["btn_newGame"].get_rect(
            topleft=(256, 270)
        )
        self.continue_button_rect: pygame.Rect = self.assets.images["btn_continue"].get_rect(
            topleft=(256, 320)
        )

    def _setup_physics(self) -> None:
        """Sets up the Box2D physics world."""
        self.world: world = world(gravity=(0, 8), doSleep=True)
        self.contact_listener: GameContactListener = GameContactListener(self)
        self.world.contactListener = self.contact_listener

        # Create walls and floor sensor
        self.walls: List[staticBody] = []
        floor: staticBody = self.world.CreateStaticBody(
            position=(0, SCREEN_HEIGHT / PPM),
            shapes=polygonShape(box=(SCREEN_WIDTH / PPM, 1 / PPM)),
        )
        floor.fixtures[0].isSensor = True
        floor.userData = "floor"
        self.walls.append(floor)

        wall_top: staticBody = self.world.CreateStaticBody(position=(0, 0))
        wall_top.CreateEdgeChain(
            [
                (0, 0),
                (SCREEN_WIDTH / PPM, 0),
            ]
        )
        self.walls.append(wall_top)

        wall_left: staticBody = self.world.CreateStaticBody(position=(0, 0))
        wall_left.CreateEdgeChain([(0, 0), (0, SCREEN_HEIGHT / PPM)])
        self.walls.append(wall_left)

        wall_right: staticBody = self.world.CreateStaticBody(position=(SCREEN_WIDTH / PPM, 0))
        wall_right.CreateEdgeChain([(0, 0), (0, SCREEN_HEIGHT / PPM)])
        self.walls.append(wall_right)

    def save_progress(self, level: int) -> None:
        """
        Save the current level to the save file.

        Args:
            level: The level to save.
        """
        try:
            with open(self.save_path, "w") as f:
                f.write(str(level))
        except IOError as e:
            print(f"Error saving progress: {e}")

    def load_progress(self) -> int:
        """Load the level from the save file."""
        try:
            if os.path.exists(self.save_path):
                with open(self.save_path, "r") as f:
                    return int(f.read().strip())
        except (IOError, ValueError) as e:
            print(f"Error loading progress: {e}")
        return 0

    def _start_game(self, new_game: bool) -> None:
        """
        Starts a new game or continues from a saved game.

        Args:
            new_game: True to start a new game, False to continue.
        """
        for body in self.world.bodies:
            if isinstance(body.userData, Brick):
                self.bodies_to_destroy.append(body)
                body.userData.kill()

        if hasattr(self, 'paddle') and self.paddle:
            self.bodies_to_destroy.append(self.paddle.body)
            self.paddle.kill()

        for body in self.bodies_to_destroy:
            self.world.DestroyBody(body)

        self.bodies_to_destroy = []
        self.score = 0
        self.lives = 5
        self.current_level = 0 if new_game else self.load_progress()
        self.ammo = 0
        self.grow_active = False
        self.play_sound("sfx-08")

        self.all_sprites: pygame.sprite.Group = pygame.sprite.Group()
        self.bricks: pygame.sprite.Group = pygame.sprite.Group()
        self.balls: pygame.sprite.Group = pygame.sprite.Group()
        self.particles: pygame.sprite.Group = pygame.sprite.Group()
        self.powerups: pygame.sprite.Group = pygame.sprite.Group()
        self.bullets: pygame.sprite.Group = pygame.sprite.Group()

        self.paddle: Paddle = Paddle(self.assets, self.world, self)
        self.all_sprites.add(self.paddle)

        self.ball: Ball = Ball(self.assets, self.paddle, self.world, self)
        self.all_sprites.add(self.ball)
        self.balls.add(self.ball)

        self._setup_level(self.current_level)
        self.game_mode = "playing"

    def _setup_level(self, level_num: int) -> None:
        """
        Sets up the level.

        Args:
            level_num: The level number to set up.
        """
        for brick in self.bricks:
            if(brick.body not in self.bodies_to_destroy):
                self.bodies_to_destroy.append(brick.body)
                brick.kill()

        level_map: List[List[int]] | None = self.map_loader.get_map(level_num)
        if not level_map:
            self.game_mode = "game_over"
            return

        brick_width: int = self.assets.images["brick"].get_width()
        brick_height: int = self.assets.images["brick"].get_height()

        num_columns: int = len(level_map[0])
        total_grid_width: int = (num_columns * brick_width) + ((num_columns - 1) * 2)
        start_x: int = (SCREEN_WIDTH - total_grid_width) // 2

        for y, row in enumerate(level_map):
            for x, brick_hp in enumerate(row):
                if brick_hp > 0:
                    brick_x: int = start_x + x * (brick_width + 2)
                    brick_y: int = y * (brick_height + 2) + 36
                    brick: Brick = Brick(
                        self.assets, brick_x, brick_y, brick_hp, self, self.world
                    )
                    self.all_sprites.add(brick)
                    self.bricks.add(brick)

    def run(self) -> None:
        """Runs the main game loop."""
        running: bool = True
        while running:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                self._handle_events(event)

            self._update()
            self._draw()

        pygame.quit()
        sys.exit()

    def _handle_events(self, event: pygame.event.Event) -> None:
        """
        Handles game events.

        Args:
            event: The event to handle.
        """
        if self.game_mode == "start_menu":
            pygame.mouse.set_visible(True)
            pygame.event.set_grab(False)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = self._get_scaled_mouse_pos(event.pos)
                if self.new_game_button_rect.collidepoint(mouse_pos):
                    self._start_game(new_game=True)
                elif self.continue_button_rect.collidepoint(
                    mouse_pos
                ) and os.path.exists(self.save_path):
                    self._start_game(new_game=False)
        elif self.game_mode == "playing":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left-click
                    for ball in self.balls:
                        ball.launch()
                elif event.button == 3:  # Right-click
                    self.shoot_bullet()
        elif self.game_mode == "game_over":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.game_mode = "start_menu"

    def shoot_bullet(self) -> None:
        """Shoots a bullet."""
        if self.ammo > 0:
            self.ammo -= 1
            bullet: Bullet = Bullet(
                self.assets,
                self.paddle.rect.centerx,
                self.paddle.rect.top,
                self.world,
                self,
            )
            self.all_sprites.add(bullet)
            self.bullets.add(bullet)
            self.play_sound("sfx-09")

    def _update(self) -> None:
        """Updates the game state."""
        if self.game_mode == "playing":
            for body in self.bodies_to_destroy:
                self.world.DestroyBody(body)
            self.bodies_to_destroy.clear()

            if self.should_create_new_ball:
                self.ball = Ball(self.assets, self.paddle, self.world, self)
                self.all_sprites.add(self.ball)
                self.balls.add(self.ball)
                self.should_create_new_ball = False

            self.world.Step(1 / FPS, 6, 2)

            if self.paddle_resize_needed:
                self.paddle.resize(self.assets.images["paddle"].get_rect().width)
                self.paddle_resize_needed = False

            if self.score != self.score_val:
                self.score_val = self.score
                self.score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            if self.lives != self.lives_val:
                self.lives_val = self.lives
                self.lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
            if self.ammo != self.ammo_val:
                self.ammo_val = self.ammo
                self.ammo_text = self.font.render(f"Ammo: {self.ammo}", True, WHITE)

            self.all_sprites.update()
            self.particles.update()
            self.powerups.update()
            self._handle_powerup_collisions()

            if not self.bricks:
                self.current_level += 1
                if self.current_level >= self.map_loader.max_level:
                    self.game_mode = "game_over"
                else:
                    if self.current_level > self.load_progress():
                        self.save_progress(self.current_level)
                    self._setup_level(self.current_level)
                    for ball in self.balls:
                        self.world.DestroyBody(ball.body)
                        ball.kill()
                    self.ball = Ball(self.assets, self.paddle, self.world, self)
                    self.all_sprites.add(self.ball)
                    self.balls.add(self.ball)

    def handle_ball_brick_collision(self, ball: Ball, brick: Brick) -> None:
        """
        Handles the collision between a ball and a brick.

        Args:
            ball: The ball that collided.
            brick: The brick that was hit.
        """
        if ball.is_bomb:
            self.explode(brick)
            ball.is_bomb = False
            ball.image = self.assets.images["ball"]
        else:
            brick.hit()
        self.score += 100

    def handle_bullet_brick_collision(self, bullet: Bullet, brick: Brick) -> None:
        """
        Handles the collision between a bullet and a brick.

        Args:
            bullet: The bullet that collided.
            brick: The brick that was hit.
        """
        if bullet in self.bullets:
            if (bullet.body not in self.bodies_to_destroy):
                self.bodies_to_destroy.append(bullet.body)
                bullet.kill()
                brick.hit()
                self.score += 100

    def handle_ball_floor_collision(self, ball: Ball) -> None:
        """
        Handles the collision between a ball and the floor.

        Args:
            ball: The ball that hit the floor.
        """
        if ball in self.balls:
            if(ball.body not in self.bodies_to_destroy):
                self.bodies_to_destroy.append(ball.body)
                ball.kill()
            if not self.balls:
                self.lives -= 1
                self.play_sound("sfx-01")
                if self.grow_active:
                    self.paddle_resize_needed = True
                    self.grow_active = False
                if self.lives <= 0:
                    self.game_mode = "game_over"
                else:
                    self.should_create_new_ball = True

    def explode(self, brick: Brick) -> None:
        """
        Explodes a brick, destroying it and surrounding bricks.

        Args:
            brick: The brick to explode.
        """
        for b in self.bricks.copy():
            if b.rect.colliderect(brick.rect.inflate(50, 50)):
                b.destroy()

    def _handle_powerup_collisions(self) -> None:
        """Handles collisions between the paddle and power-ups."""
        collided_powerups: List[PowerUp] = pygame.sprite.spritecollide(
            self.paddle, self.powerups, True
        )
        for powerup in collided_powerups:
            self.play_sound("sfx-06")
            if powerup.type == "ball":
                new_ball: Ball = Ball(self.assets, self.paddle, self.world, self)
                new_ball.launch()
                self.all_sprites.add(new_ball)
                self.balls.add(new_ball)

            elif powerup.type == "bomb":
                for ball in self.balls:
                    ball.is_bomb = True
                    ball.image = self.assets.images["ball_bomb"]
            elif powerup.type == "gold":
                self.score += 500
            elif powerup.type == "shot":
                self.ammo = 20
            elif powerup.type == "ballMulti":
                for _ in range(4):
                    new_ball = Ball(self.assets, self.paddle, self.world, self)
                    new_ball.launch()
                    self.all_sprites.add(new_ball)
                    self.balls.add(new_ball)
            elif powerup.type == "life":
                self.lives += 1
            elif powerup.type == "grow":
                if not self.grow_active:
                    self.grow_active = True
                    self.paddle.resize(self.paddle.rect.width * 1.5)

    def _draw(self) -> None:
        """Draws the game screen."""
        if self.game_mode == "start_menu":
            self._draw_start_menu()
        elif self.game_mode == "playing":
            self._draw_gameplay()
        elif self.game_mode == "game_over":
            self._draw_game_over()

        # Scale the game surface to the window size, maintaining aspect ratio
        screen_width, screen_height = self.screen.get_size()

        # determine the scale factor
        scale: float = min(screen_width / SCREEN_WIDTH, screen_height / SCREEN_HEIGHT)

        # calculate the new size of the game surface
        scaled_width: int = int(SCREEN_WIDTH * scale)
        scaled_height: int = int(SCREEN_HEIGHT * scale)

        # scale the game surface
        scaled_surface: pygame.Surface = pygame.transform.smoothscale(self.game_surface, (scaled_width, scaled_height))

        # calculate the position to center the scaled surface
        pos_x: float = (screen_width - scaled_width) / 2
        pos_y: float = (screen_height - scaled_height) / 2

        # blit the scaled surface to the screen
        self.screen.fill(BLACK) # fill with black bars
        self.screen.blit(scaled_surface, (pos_x, pos_y))

        pygame.display.flip()

    def _draw_start_menu(self) -> None:
        """Draws the start menu."""
        self.game_surface.blit(self.assets.images["bgTitle"], (0, 0))
        self.game_surface.blit(self.assets.images["btn_newGame"], self.new_game_button_rect)
        if os.path.exists(self.save_path):
            self.game_surface.blit(
                self.assets.images["btn_continue"], self.continue_button_rect
            )

    def _draw_gameplay(self) -> None:
        """Draws the gameplay screen."""
        self.game_surface.blit(self.assets.images["bg1"], (0, 0))
        for sprite in self.all_sprites:
            if isinstance(sprite, Paddle):
                sprite.draw(self.game_surface)
            else:
                self.game_surface.blit(sprite.image, sprite.rect)
        self.particles.draw(self.game_surface)
        if self.score_text:
            self.game_surface.blit(self.score_text, (10, 10))
        if self.lives_text:
            self.game_surface.blit(self.lives_text, (SCREEN_WIDTH - self.lives_text.get_width() - 10, 10))
        if self.ammo > 0 and self.ammo_text:
            self.game_surface.blit(
                self.ammo_text, (SCREEN_WIDTH // 2 - self.ammo_text.get_width() // 2, 10)
            )

    def _draw_game_over(self) -> None:
        """Draws the game over screen."""
        self.game_surface.blit(self.assets.images["bgGameOver"], (0, 0))
        go_text: pygame.Surface = self.font.render("Click to continue", True, WHITE)
        self.game_surface.blit(
            go_text, (SCREEN_WIDTH // 2 - go_text.get_width() // 2, 300)
        )
