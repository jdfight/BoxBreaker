import pygame
import sys
import os
import random
import math
import Box2D
from Box2D.b2 import (
    world,
    polygonShape,
    staticBody,
    dynamicBody,
    kinematicBody,
    contactListener,
    fixtureDef,
)

# --- Constants ---
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
TITLE = "Box Breaker"
FPS = 60
PPM = 20.0  # Pixels per meter
MIN_BALL_SPEED = 10
MAX_BALL_SPEED = 25

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# --- Paths ---
BASE_DIR = os.path.dirname(__file__)
ASSET_DIR = os.path.join(BASE_DIR, "res")
IMAGE_DIR = os.path.join(ASSET_DIR, "pixmaps")
SOUND_DIR = os.path.join(ASSET_DIR, "audio")
MAP_DIR = os.path.join(BASE_DIR, "maps")


class AssetManager:
    """A class to manage loading and storing game assets."""

    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.particle_images = {
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

    def load_assets(self):
        """Load all images and sounds."""
        for filename in os.listdir(IMAGE_DIR):
            if filename.endswith(".png"):
                name = os.path.splitext(filename)[0]
                try:
                    image = pygame.image.load(
                        os.path.join(IMAGE_DIR, filename)
                    ).convert_alpha()
                    self.images[name] = image
                    if name.startswith("p") and "_" in name:
                        parts = name.split("_")
                        if (
                            len(parts) == 2
                            and parts[0].startswith("p")
                            and parts[0][1:].isdigit()
                        ):
                            color = parts[1]
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
                    sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, filename))
                    self.sounds[name] = sound
                    #print(f"Loaded sound: {name}")
        except pygame.error as e:
            print(f"Failed to initialize mixer or load sound: {e}")


class MapLoader:
    """A class to load and manage game maps."""

    def __init__(self):
        self.maps = []
        self.max_level = 0
        self.load_maps()

    def load_maps(self):
        map_files = sorted(
            [f for f in os.listdir(MAP_DIR) if f.startswith("map.")],
            key=lambda x: int(x.split(".")[1]),
        )
        self.max_level = len(map_files)
        for filename in map_files:
            try:
                with open(os.path.join(MAP_DIR, filename), "r") as f:
                    level_map = []
                    for line in f:
                        row = [int(char) for char in line.strip() if char.isdigit()]
                        if row:
                            level_map.append(row)
                    self.maps.append(level_map)
            except (IOError, ValueError) as e:
                print(f"Failed to load or parse map {filename}: {e}")

    def get_map(self, level_index):
        if 0 <= level_index < len(self.maps):
            return self.maps[level_index]
        return None


class GameContactListener(contactListener):
    def __init__(self, game):
        super().__init__()
        self.game = game

    def BeginContact(self, contact):
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


# --- Game Object Classes ---


class Paddle(pygame.sprite.Sprite):
    def __init__(self, assets, world, game):
        super().__init__()
        self.assets = assets
        self.world = world
        self.game = game
        self.image = self.assets.images["paddle"]
        self.rect = self.image.get_rect()
        self.rect.x = (SCREEN_WIDTH - self.rect.width) // 2
        self.rect.y = SCREEN_HEIGHT - self.rect.height - 10
        self.create_body()

    def create_body(self):
        self.body = self.world.CreateKinematicBody(
            position=(self.rect.centerx / PPM, self.rect.centery / PPM),
            shapes=polygonShape(
                box=(
                    self.rect.width / 2 / PPM,
                    self.rect.height / 2 / PPM,
                )
            ),
        )
        self.body.userData = self

    def resize(self, width):
        self.body.DestroyFixture(self.body.fixtures[0])
        self.body.CreateFixture(
            fixtureDef(
                shape=polygonShape(
                    box=(width / 2 / PPM, self.rect.height / 2 / PPM)
                )
            )
        )
        self.image = pygame.transform.scale(self.assets.images["paddle"], (width, self.rect.height))
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self):
        mouse_x = pygame.mouse.get_pos()[0]
        self.body.position = (mouse_x / PPM, self.body.position.y)
        self.rect.centerx = self.body.position.x * PPM


class Ball(pygame.sprite.Sprite):
    def __init__(self, assets, paddle, world, game):
        super().__init__()
        self.assets = assets
        self.paddle = paddle
        self.world = world
        self.game = game
        self.image = self.assets.images["ball"]
        self.rect = self.image.get_rect()
        self.state = "on_paddle"
        self.is_bomb = False
        self.create_body()
        self.reset()

    def create_body(self):
        self.body = self.world.CreateDynamicBody(
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

    def reset(self):
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

    def launch(self):
        if self.state == "on_paddle":
            self.state = "moving"
            impulse = (random.uniform(-7, 7), -15)
            self.body.ApplyLinearImpulse(impulse, self.body.worldCenter, True)
            self.game.play_sound("sfx-02")
            pygame.event.set_grab(True)
            pygame.mouse.set_visible(False)

    def update(self):
        if self.state == "on_paddle":
            self.body.position = (
                self.paddle.body.position.x,
                self.paddle.body.position.y
                - (self.paddle.rect.height / 2 / PPM)
                - (self.rect.height / 2 / PPM),
            )
        elif self.state == "moving":
            vel = self.body.linearVelocity
            speed = vel.length
            if speed > MAX_BALL_SPEED:
                self.body.linearVelocity = (MAX_BALL_SPEED / speed) * vel
            elif speed > 0 and speed < MIN_BALL_SPEED:
                self.body.linearVelocity = (MIN_BALL_SPEED / speed) * vel

        self.rect.center = (self.body.position.x * PPM, self.body.position.y * PPM)


class Brick(pygame.sprite.Sprite):
    BRICK_IMAGES = {
        1: "brick",
        2: "brick_blue",
        3: "brick_gold",
        4: "brick_green",
        5: "brick_orange",
        6: "brick_purple",
        7: "brick_black",
        8: "brick_silver",
    }
    BRICK_PARTICLE_COLORS = {
        1: "red",
        2: "blue",
        3: "yellow",
        4: "green",
        5: "orange",
        6: "purple",
        7: "black",
        8: "silver",
    }

    def __init__(self, assets, x, y, hp, game, world):
        super().__init__()
        self.assets = assets
        self.hp = hp
        self.game = game
        self.world = world
        self.image = self.assets.images[self.BRICK_IMAGES.get(self.hp, "brick")]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.create_body()

    def create_body(self):
        self.body = self.world.CreateStaticBody(
            position=(self.rect.centerx / PPM, self.rect.centery / PPM),
            shapes=polygonShape(
                box=(
                    self.rect.width / 2 / PPM,
                    self.rect.height / 2 / PPM,
                )
            ),
        )
        self.body.userData = self

    def destroy(self):
        color = self.BRICK_PARTICLE_COLORS.get(self.hp, "red")
        for _ in range(10):
            particle = Particle(
                self.assets, self.rect.centerx, self.rect.centery, color
            )
            self.game.all_sprites.add(particle)
            self.game.particles.add(particle)
        if random.random() < 0.2:  # 20% chance of dropping a power-up
            powerup_type = random.choice(
                ["ball", "bomb", "gold", "shot", "ballMulti", "life", "grow"]
            )
            powerup = PowerUp(
                self.assets, self.rect.centerx, self.rect.centery, powerup_type
            )
            self.game.all_sprites.add(powerup)
            self.game.powerups.add(powerup)
        self.game.play_sound("sfx-01b")
        self.game.bodies_to_destroy.append(self.body)
        self.kill()

    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            self.destroy()
        else:
            self.image = self.assets.images[self.BRICK_IMAGES.get(self.hp, "brick")]
            self.game.play_sound("sfx-05")


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, assets, x, y, type):
        super().__init__()
        self.assets = assets
        self.type = type
        if type == "life":
            self.image = self.assets.images["bonus_paddle"]
        else:
            self.image = self.assets.images[f"bonus_{self.type}"]
        self.rect = self.image.get_rect(center=(x, y))
        self.vy = 2

    def update(self):
        self.rect.y += self.vy
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Particle(pygame.sprite.Sprite):
    def __init__(self, assets, x, y, color):
        super().__init__()
        self.assets = assets
        self.image = random.choice(self.assets.particle_images[color])
        self.rect = self.image.get_rect(center=(x, y))
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-5, 0)
        self.gravity = 0.1
        self.life = FPS * 2  # 2 seconds

    def update(self):
        self.vy += self.gravity
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.life -= 1
        if self.life <= 0:
            self.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, assets, x, y, world, game):
        super().__init__()
        self.assets = assets
        self.world = world
        self.game = game
        self.image = self.assets.images["bullet"]
        self.rect = self.image.get_rect(center=(x, y))
        self.create_body()

    def create_body(self):
        self.body = self.world.CreateDynamicBody(
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

    def update(self):
        self.rect.center = (self.body.position.x * PPM, self.body.position.y * PPM)
        if self.rect.bottom < 0:
            self.game.bodies_to_destroy.append(self.body)
            self.kill()


# --- Game Class ---


class Game:
    """Main class for the game."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.assets = AssetManager()
        self.map_loader = MapLoader()
        self.font = pygame.font.Font(None, 36)
        self.game_mode = "start_menu"
        self.bodies_to_destroy = []
        self.should_create_new_ball = False
        self.paddle_resize_needed = False
        self.save_path = os.path.join(BASE_DIR, "savegame.dat")
        self.score_val = -1
        self.lives_val = -1
        self.ammo_val = -1
        self.score_text = None
        self.lives_text = None
        self.ammo_text = None
        self._setup_buttons()
        self._setup_physics()

    def play_sound(self, sound_name):
        """Play a sound if it exists."""
        if sound_name in self.assets.sounds:
            self.assets.sounds[sound_name].play()

    def _setup_buttons(self):
        """Create rects for menu buttons."""
        self.new_game_button_rect = self.assets.images["btn_newGame"].get_rect(
            topleft=(256, 270)
        )
        self.continue_button_rect = self.assets.images["btn_continue"].get_rect(
            topleft=(256, 320)
        )

    def _setup_physics(self):
        self.world = world(gravity=(0, 8), doSleep=True)
        self.contact_listener = GameContactListener(self)
        self.world.contactListener = self.contact_listener

        # Create walls and floor sensor
        self.walls = []
        floor = self.world.CreateStaticBody(
            position=(0, SCREEN_HEIGHT / PPM),
            shapes=polygonShape(box=(SCREEN_WIDTH / PPM, 1 / PPM)),
        )
        floor.fixtures[0].isSensor = True
        floor.userData = "floor"
        self.walls.append(floor)

        wall_top = self.world.CreateStaticBody(position=(0, 0))
        wall_top.CreateEdgeChain(
            [
                (0, 0),
                (SCREEN_WIDTH / PPM, 0),
            ]
        )
        self.walls.append(wall_top)

        wall_left = self.world.CreateStaticBody(position=(0, 0))
        wall_left.CreateEdgeChain([(0, 0), (0, SCREEN_HEIGHT / PPM)])
        self.walls.append(wall_left)

        wall_right = self.world.CreateStaticBody(position=(SCREEN_WIDTH / PPM, 0))
        wall_right.CreateEdgeChain([(0, 0), (0, SCREEN_HEIGHT / PPM)])
        self.walls.append(wall_right)

    def save_progress(self, level):
        """Save the current level to the save file."""
        try:
            with open(self.save_path, "w") as f:
                f.write(str(level))
        except IOError as e:
            print(f"Error saving progress: {e}")

    def load_progress(self):
        """Load the level from the save file."""
        try:
            if os.path.exists(self.save_path):
                with open(self.save_path, "r") as f:
                    return int(f.read().strip())
        except (IOError, ValueError) as e:
            print(f"Error loading progress: {e}")
        return 0

    def _reset_game(self):
        """Reset the game to its initial state."""
        if hasattr(self, 'paddle') and self.paddle:
            self.bodies_to_destroy.append(self.paddle.body)
            self.paddle.kill()

        self.score = 0
        self.lives = 5
        self.current_level = 0
        self.ammo = 20
        self.grow_active = False
        self.play_sound("sfx-08")

        self.all_sprites = pygame.sprite.Group()
        self.bricks = pygame.sprite.Group()
        self.balls = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()

        self.paddle = Paddle(self.assets, self.world, self)
        self.all_sprites.add(self.paddle)

        self.ball = Ball(self.assets, self.paddle, self.world, self)
        self.all_sprites.add(self.ball)
        self.balls.add(self.ball)

        self._setup_level(self.current_level)
        self.game_mode = "playing"

    def _continue_game(self):
        """Continue the game from the saved level."""
        if hasattr(self, 'paddle') and self.paddle:
            self.bodies_to_destroy.append(self.paddle.body)
            self.paddle.kill()

        self.score = 0
        self.lives = 5
        self.current_level = self.load_progress()
        self.ammo = 20
        self.grow_active = False
        self.play_sound("sfx-08")

        self.all_sprites = pygame.sprite.Group()
        self.bricks = pygame.sprite.Group()
        self.balls = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()

        self.paddle = Paddle(self.assets, self.world, self)
        self.all_sprites.add(self.paddle)

        self.ball = Ball(self.assets, self.paddle, self.world, self)
        self.all_sprites.add(self.ball)
        self.balls.add(self.ball)

        self._setup_level(self.current_level)
        self.game_mode = "playing"

    def _setup_level(self, level_num):
        for brick in self.bricks:
            self.bodies_to_destroy.append(brick.body)
            brick.kill()

        level_map = self.map_loader.get_map(level_num)
        if not level_map:
            self.game_mode = "game_over"
            return

        brick_width = self.assets.images["brick"].get_width()
        brick_height = self.assets.images["brick"].get_height()

        num_columns = len(level_map[0])
        total_grid_width = (num_columns * brick_width) + ((num_columns - 1) * 2)
        start_x = (SCREEN_WIDTH - total_grid_width) // 2

        for y, row in enumerate(level_map):
            for x, brick_hp in enumerate(row):
                if brick_hp > 0:
                    brick_x = start_x + x * (brick_width + 2)
                    brick_y = y * (brick_height + 2) + 36
                    brick = Brick(
                        self.assets, brick_x, brick_y, brick_hp, self, self.world
                    )
                    self.all_sprites.add(brick)
                    self.bricks.add(brick)

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self._handle_events(event)

            self._update()
            self._draw()

        pygame.quit()
        sys.exit()

    def _handle_events(self, event):
        if self.game_mode == "start_menu":
            pygame.mouse.set_visible(True)
            pygame.event.set_grab(False)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.new_game_button_rect.collidepoint(event.pos):
                    self._reset_game()
                elif self.continue_button_rect.collidepoint(
                    event.pos
                ) and os.path.exists(self.save_path):
                    self._continue_game()
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

    def shoot_bullet(self):
        if self.ammo > 0:
            self.ammo -= 1
            bullet = Bullet(
                self.assets,
                self.paddle.rect.centerx,
                self.paddle.rect.top,
                self.world,
                self,
            )
            self.all_sprites.add(bullet)
            self.bullets.add(bullet)
            self.play_sound("sfx-09")

    def _update(self):
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

    def handle_ball_brick_collision(self, ball, brick):
        if ball.is_bomb:
            self.explode(brick)
            ball.is_bomb = False
            ball.image = self.assets.images["ball"]
        else:
            brick.hit()
        self.score += 100

    def handle_bullet_brick_collision(self, bullet, brick):
        if bullet in self.bullets:
            self.bodies_to_destroy.append(bullet.body)
            bullet.kill()
            brick.hit()
            self.score += 100

    def handle_ball_floor_collision(self, ball):
        if ball in self.balls:
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

    def explode(self, brick):
        for b in self.bricks.copy():
            if b.rect.colliderect(brick.rect.inflate(50, 50)):
                b.destroy()

    def _handle_powerup_collisions(self):
        collided_powerups = pygame.sprite.spritecollide(
            self.paddle, self.powerups, True
        )
        for powerup in collided_powerups:
            self.play_sound("sfx-06")
            if powerup.type == "ball":
                new_ball = Ball(self.assets, self.paddle, self.world, self)
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
                for _ in range(10):
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

    def _draw(self):
        if self.game_mode == "start_menu":
            self._draw_start_menu()
        elif self.game_mode == "playing":
            self._draw_gameplay()
        elif self.game_mode == "game_over":
            self._draw_game_over()

        pygame.display.flip()

    def _draw_start_menu(self):
        self.screen.blit(self.assets.images["bgTitle"], (0, 0))
        self.screen.blit(self.assets.images["btn_newGame"], self.new_game_button_rect)
        if os.path.exists(self.save_path):
            self.screen.blit(
                self.assets.images["btn_continue"], self.continue_button_rect
            )

    def _draw_gameplay(self):
        self.screen.blit(self.assets.images["bg1"], (0, 0))
        self.all_sprites.draw(self.screen)
        self.particles.draw(self.screen)
        if self.score_text:
            self.screen.blit(self.score_text, (10, 10))
        if self.lives_text:
            self.screen.blit(self.lives_text, (SCREEN_WIDTH - self.lives_text.get_width() - 10, 10))
        if self.ammo > 0 and self.ammo_text:
            self.screen.blit(
                self.ammo_text, (SCREEN_WIDTH // 2 - self.ammo_text.get_width() // 2, 10)
            )

    def _draw_game_over(self):
        self.screen.blit(self.assets.images["bgGameOver"], (0, 0))
        go_text = self.font.render("Click to continue", True, WHITE)
        self.screen.blit(
            go_text, (SCREEN_WIDTH // 2 - go_text.get_width() // 2, 300)
        )


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()