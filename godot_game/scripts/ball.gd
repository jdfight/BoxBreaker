extends RigidBody2D

enum BallState { ON_PADDLE, MOVING }

const MIN_SPEED = 200
const MAX_SPEED = 400

var state: BallState = BallState.ON_PADDLE
var is_bomb: bool = false

@onready var sprite = $Sprite
@onready var bomb_texture = preload("res://assets/pixmaps/ball_bomb.png")
@onready var normal_texture = preload("res://assets/pixmaps/ball.png")

var paddle = null

func _ready():
	# Find the paddle in the scene tree. This is a simple way, but for
	# larger scenes, signals or groups would be better.
	add_to_group("balls")
	paddle = get_parent().get_node("Paddle")
	connect("body_entered", _on_body_entered)
	freeze = true

func _on_body_entered(body):
	if body.is_in_group("bricks"):
		if is_bomb:
			explode(body)
		else:
			body.take_damage()

func _physics_process(delta):
	if state == BallState.ON_PADDLE:
		position = paddle.position + Vector2(0, -25)
	elif state == BallState.MOVING:
		# Clamp speed
		if linear_velocity.length() > MAX_SPEED:
			linear_velocity = linear_velocity.normalized() * MAX_SPEED
		elif linear_velocity.length() < MIN_SPEED:
			linear_velocity = linear_velocity.normalized() * MIN_SPEED

func launch():
	if state == BallState.ON_PADDLE:
		freeze = false
		state = BallState.MOVING
		var launch_direction = Vector2(randf_range(-1, 1), -1).normalized()
		linear_velocity = launch_direction * MIN_SPEED
		# Apply a bit of angular impulse to make it more interesting
		apply_central_impulse(launch_direction * 10)
		AudioManager.play_sound("sfx-02")

func set_as_bomb(is_bomb_ball: bool):
	is_bomb = is_bomb_ball
	if is_bomb:
		sprite.texture = bomb_texture
	else:
		sprite.texture = normal_texture

func reset_ball():
	state = BallState.ON_PADDLE
	freeze = true
	linear_velocity = Vector2.ZERO
	angular_velocity = 0
	set_as_bomb(false)

func explode(hit_brick):
	var explosion_radius = 100
	var bricks_in_radius = []
	for brick in get_tree().get_nodes_in_group("bricks"):
		if brick.global_position.distance_to(hit_brick.global_position) < explosion_radius:
			bricks_in_radius.append(brick)

	for brick in bricks_in_radius:
		brick.destroy_brick()

	set_as_bomb(false)
