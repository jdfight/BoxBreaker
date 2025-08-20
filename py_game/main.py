import pygame
import sys
import os
import random

# --- Constants ---
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
TITLE = "Box Breaker"
FPS = 60

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
        self.load_assets()

    def load_assets(self):
        """Load all images and sounds."""
        for filename in os.listdir(IMAGE_DIR):
            if filename.endswith(".png"):
                name = os.path.splitext(filename)[0]
                try:
                    image = pygame.image.load(os.path.join(IMAGE_DIR, filename)).convert_alpha()
                    self.images[name] = image
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
        except pygame.error as e:
            print(f"Failed to initialize mixer or load sound: {e}")

class MapLoader:
    """A class to load and manage game maps."""
    def __init__(self):
        self.maps = []
        self.max_level = 0
        self.load_maps()

    def load_maps(self):
        map_files = sorted([f for f in os.listdir(MAP_DIR) if f.startswith("map.")], key=lambda x: int(x.split('.')[1]))
        self.max_level = len(map_files)
        for filename in map_files:
            try:
                with open(os.path.join(MAP_DIR, filename), 'r') as f:
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

# --- Game Object Classes ---

class Paddle(pygame.sprite.Sprite):
    def __init__(self, assets):
        super().__init__()
        self.assets = assets
        self.image = self.assets.images['paddle']
        self.rect = self.image.get_rect()
        self.rect.x = (SCREEN_WIDTH - self.rect.width) // 2
        self.rect.y = SCREEN_HEIGHT - self.rect.height - 10

    def update(self):
        self.rect.centerx = pygame.mouse.get_pos()[0]
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH: self.rect.right = SCREEN_WIDTH

class Ball(pygame.sprite.Sprite):
    def __init__(self, assets, paddle):
        super().__init__()
        self.assets = assets
        self.paddle = paddle
        self.image = self.assets.images['ball']
        self.rect = self.image.get_rect()
        self.state = 'on_paddle'
        self.vx = 0
        self.vy = 0
        self.reset()

    def reset(self):
        self.state = 'on_paddle'
        self.rect.centerx = self.paddle.rect.centerx
        self.rect.bottom = self.paddle.rect.top
        self.vx = 0
        self.vy = 0

    def launch(self):
        if self.state == 'on_paddle':
            self.state = 'moving'
            # Give a slight random horizontal direction on launch
            self.vx = random.choice([-5, 5])
            self.vy = -5

    def update(self):
        if self.state == 'on_paddle':
            self.rect.centerx = self.paddle.rect.centerx
            self.rect.bottom = self.paddle.rect.top
        elif self.state == 'moving':
            self.rect.x += self.vx
            self.rect.y += self.vy
            if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH: self.vx *= -1
            if self.rect.top <= 0: self.vy *= -1

class Brick(pygame.sprite.Sprite):
    BRICK_IMAGES = {1: 'brick', 2: 'brick_blue', 3: 'brick_gold', 4: 'brick_green', 5: 'brick_orange', 6: 'brick_purple', 7: 'brick_black', 8: 'brick_silver'}
    def __init__(self, assets, x, y, hp):
        super().__init__()
        self.assets = assets
        self.hp = hp
        self.image = self.assets.images[self.BRICK_IMAGES.get(self.hp, 'brick')]
        self.rect = self.image.get_rect(topleft=(x, y))

    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            self.kill()
        else:
            self.image = self.assets.images[self.BRICK_IMAGES.get(self.hp, 'brick')]

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

        self.game_mode = 'start_menu'
        self._setup_buttons()

    def _setup_buttons(self):
        """Create rects for menu buttons."""
        self.new_game_button_rect = self.assets.images['btn_newGame'].get_rect(topleft=(256, 270))
        self.continue_button_rect = self.assets.images['btn_continue'].get_rect(topleft=(256, 320))

    def _reset_game(self):
        """Reset the game to its initial state."""
        self.score = 0
        self.lives = 5
        self.current_level = 0

        self.all_sprites = pygame.sprite.Group()
        self.bricks = pygame.sprite.Group()
        self.balls = pygame.sprite.Group()

        self.paddle = Paddle(self.assets)
        self.all_sprites.add(self.paddle)

        self.ball = Ball(self.assets, self.paddle)
        self.all_sprites.add(self.ball)
        self.balls.add(self.ball)

        self._setup_level(self.current_level)
        self.game_mode = 'playing'

    def _setup_level(self, level_num):
        for brick in self.bricks:
            brick.kill()

        level_map = self.map_loader.get_map(level_num)
        if not level_map:
            self.game_mode = 'game_over'
            return

        brick_width = self.assets.images['brick'].get_width()
        brick_height = self.assets.images['brick'].get_height()

        for y, row in enumerate(level_map):
            for x, brick_hp in enumerate(row):
                if brick_hp > 0:
                    brick_x = x * (brick_width + 2) + 1
                    brick_y = y * (brick_height + 2) + 36
                    brick = Brick(self.assets, brick_x, brick_y, brick_hp)
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
        if self.game_mode == 'start_menu':
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.new_game_button_rect.collidepoint(event.pos):
                    self._reset_game()
                # For simplicity, continue also starts a new game
                elif self.continue_button_rect.collidepoint(event.pos):
                    self._reset_game()
        elif self.game_mode == 'playing':
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.ball.launch()
        elif self.game_mode == 'game_over':
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.game_mode = 'start_menu'


    def _update(self):
        if self.game_mode == 'playing':
            self.all_sprites.update()
            self._handle_collisions()

            if self.ball.rect.top > SCREEN_HEIGHT:
                self.lives -= 1
                if self.lives <= 0:
                    self.game_mode = 'game_over'
                else:
                    self.ball.reset()
            if not self.bricks:
                self.current_level += 1
                if self.current_level >= self.map_loader.max_level:
                    self.game_mode = 'game_over'
                else:
                    self._setup_level(self.current_level)
                    self.ball.reset()

    def _handle_collisions(self):
        ball = self.ball
        if ball.rect.colliderect(self.paddle.rect):
            ball.rect.bottom = self.paddle.rect.top
            ball.vy *= -1
            offset = (ball.rect.centerx - self.paddle.rect.centerx) / (self.paddle.rect.width / 2)
            offset = max(-1, min(1, offset))
            ball.vx = offset * 7

        collided_bricks = pygame.sprite.spritecollide(ball, self.bricks, False)
        for brick in collided_bricks:
            brick.hit()
            self.score += 100
            dx = ball.rect.centerx - brick.rect.centerx
            dy = ball.rect.centery - brick.rect.centery
            w = (ball.rect.width + brick.rect.width) / 2
            h = (ball.rect.height + brick.rect.height) / 2
            ox = w - abs(dx)
            oy = h - abs(dy)
            if ox > oy:
                ball.vy *= -1
                if dy > 0: ball.rect.top = brick.rect.bottom
                else: ball.rect.bottom = brick.rect.top
            else:
                ball.vx *= -1
                if dx > 0: ball.rect.left = brick.rect.right
                else: ball.rect.right = brick.rect.left

    def _draw(self):
        if self.game_mode == 'start_menu':
            self._draw_start_menu()
        elif self.game_mode == 'playing':
            self._draw_gameplay()
        elif self.game_mode == 'game_over':
            self._draw_game_over()

        pygame.display.flip()

    def _draw_start_menu(self):
        self.screen.blit(self.assets.images['bgTitle'], (0, 0))
        self.screen.blit(self.assets.images['btn_newGame'], self.new_game_button_rect)
        self.screen.blit(self.assets.images['btn_continue'], self.continue_button_rect)

    def _draw_gameplay(self):
        self.screen.blit(self.assets.images['bg1'], (0, 0))
        self.all_sprites.draw(self.screen)
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (SCREEN_WIDTH - lives_text.get_width() - 10, 10))

    def _draw_game_over(self):
        self.screen.blit(self.assets.images['bgGameOver'], (0, 0))
        go_text = self.font.render("Click to continue", True, WHITE)
        self.screen.blit(go_text, (SCREEN_WIDTH // 2 - go_text.get_width() // 2, 300))

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
