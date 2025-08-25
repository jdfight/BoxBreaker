extends Node2D

# Scene preloads
const Ball = preload("res://scenes/ball.tscn")
const Brick = preload("res://scenes/brick.tscn")
const Bullet = preload("res://scenes/bullet.tscn")

# Game states
enum GameState { START_MENU, PLAYING, GAME_OVER, GAME_WON }

# UI elements
@onready var start_menu = $UI/StartMenu
@onready var hud = $UI/HUD
@onready var game_over_screen = $UI/GameOverScreen
@onready var game_won_screen = $UI/GameWonScreen
@onready var score_label = $UI/HUD/ScoreLabel
@onready var lives_label = $UI/HUD/LivesLabel
@onready var ammo_label = $UI/HUD/AmmoLabel

const SAVE_PATH = "user://savegame.dat"

# Game variables
var score: int = 0
var lives: int = 5
var ammo: int = 0
var current_level: int = 0
var game_state: GameState = GameState.START_MENU

var balls = []

# Called when the node enters the scene tree for the first time.
func _ready():
	update_ui()
	get_tree().root.connect("child_entered_tree", _on_child_entered_tree)
	$UI/StartMenu/ContinueButton.visible = FileAccess.file_exists(SAVE_PATH)

func _on_child_entered_tree(node):
	if node is Area2D and node.has_signal("powerup_collected"):
		node.connect("powerup_collected", _on_powerup_collected)

func _unhandled_input(event):
	if game_state == GameState.PLAYING and event is InputEventMouseButton and event.pressed:
		if event.button_index == MOUSE_BUTTON_LEFT:
			for ball in balls:
				ball.launch()
		elif event.button_index == MOUSE_BUTTON_RIGHT:
			shoot()

func shoot():
	if ammo > 0:
		ammo -= 1
		var new_bullet = Bullet.instantiate()
		new_bullet.position = $Paddle.position + Vector2(0, -20)
		add_child(new_bullet)
		update_ui()
		AudioManager.play_sound("sfx-09")

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	if (game_state == GameState.GAME_OVER or game_state == GameState.GAME_WON) and Input.is_action_just_pressed("ui_accept"):
		change_state(GameState.START_MENU)

func change_state(new_state: GameState):
	game_state = new_state
	match game_state:
		GameState.START_MENU:
			start_menu.visible = true
			hud.visible = false
			game_over_screen.visible = false
			game_won_screen.visible = false
		GameState.PLAYING:
			start_menu.visible = false
			hud.visible = true
			game_over_screen.visible = false
			game_won_screen.visible = false
		GameState.GAME_OVER:
			start_menu.visible = false
			hud.visible = false
			game_over_screen.visible = true
			game_won_screen.visible = false
		GameState.GAME_WON:
			start_menu.visible = false
			hud.visible = false
			game_over_screen.visible = false
			game_won_screen.visible = true
	update_ui()

func update_ui():
	score_label.text = "Score: %d" % score
	lives_label.text = "Lives: %d" % lives
	ammo_label.text = "Ammo: %d" % ammo

func _on_new_game_button_pressed():
	print("New Game button pressed")
	start_game(true)

func _on_continue_button_pressed():
	print("Continue button pressed")
	start_game(false)

func start_game(new_game: bool):
	if new_game:
		score = 0
		lives = 5
		ammo = 0
		current_level = 0
	else:
		current_level = load_progress()

	change_state(GameState.PLAYING)
	AudioManager.play_sound("sfx-08")

	# Clear existing balls
	for ball in balls:
		ball.queue_free()
	balls.clear()

	create_new_ball()

	_load_level(current_level)

func _load_level(level_num):
	# Clear existing bricks
	for brick in get_tree().get_nodes_in_group("bricks"):
		brick.queue_free()

	var map_data = MapLoader.get_map(level_num)
	if not map_data:
		change_state(GameState.GAME_OVER)
		return

	var brick_size = Vector2(32, 16)
	var screen_width = get_viewport_rect().size.x
	var num_columns = map_data[0].size()
	var total_grid_width = (num_columns * brick_size.x) + ((num_columns - 1) * 2)
	var start_x = (screen_width - total_grid_width) / 2

	for y in range(map_data.size()):
		for x in range(map_data[y].size()):
			var brick_hp = map_data[y][x]
			if brick_hp > 0:
				var new_brick = Brick.instantiate()
				var brick_pos = Vector2(start_x + x * (brick_size.x + 2), y * (brick_size.y + 2) + 36)
				add_child(new_brick)
				new_brick.position = brick_pos
				new_brick.set_hp(brick_hp)
				new_brick.connect("brick_destroyed", _on_brick_destroyed)


func create_new_ball():
	var new_ball = Ball.instantiate()
	add_child(new_ball)
	balls.append(new_ball)

func _on_brick_destroyed(brick):
	score += 100
	update_ui()

	# Use call_deferred to wait for the brick to be removed from the tree
	call_deferred("_check_level_complete")

func _check_level_complete():
	if get_tree().get_nodes_in_group("bricks").is_empty():
		current_level += 1
		if current_level >= MapLoader.max_level:
			change_state(GameState.GAME_WON)
		else:
			save_progress(current_level)
			_load_level(current_level)
			for ball in balls:
				ball.queue_free()
			balls.clear()
			create_new_ball()

func _on_powerup_collected(type):
	AudioManager.play_sound("sfx-06")
	match type:
		"ball":
			create_new_ball()
		"bomb":
			for ball in balls:
				ball.set_as_bomb(true)
		"gold":
			score += 500
		"shot":
			ammo = 20
		"ballMulti":
			for i in range(4):
				create_new_ball()
		"life":
			lives += 1
		"grow":
			$Paddle.resize_paddle($Paddle.get_node("Sprite").get_rect().size.x * 1.5)

	update_ui()

func _on_floor_sensor_body_entered(body):
	if body is RigidBody2D: # It's a ball
		body.queue_free()
		balls.erase(body)

		if balls.is_empty():
			lives -= 1
			AudioManager.play_sound("sfx-01")
			update_ui()
			if lives <= 0:
				change_state(GameState.GAME_OVER)
			else:
				create_new_ball()

func save_progress(level):
	var file = FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	file.store_string(str(level))
	file.close()

func load_progress():
	if FileAccess.file_exists(SAVE_PATH):
		var file = FileAccess.open(SAVE_PATH, FileAccess.READ)
		var level = file.get_as_text().to_int()
		file.close()
		return level
	return 0
