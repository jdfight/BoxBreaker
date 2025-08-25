extends CharacterBody2D

const LERP_FACTOR = 0.2

func _ready():
	add_to_group("paddle")

@onready var sprite = $Sprite
@onready var collision_shape = $CollisionShape

func _physics_process(delta):
	var target_x = get_global_mouse_position().x
	var new_position = position
	new_position.x = lerp(position.x, target_x, LERP_FACTOR)

	# Clamp position within screen bounds
	var screen_width = get_viewport_rect().size.x
	var paddle_width = sprite.get_rect().size.x / 2
	new_position.x = clamp(new_position.x, paddle_width, screen_width - paddle_width)

	position = new_position
	move_and_slide()

func resize_paddle(new_width: float):
	var original_size = sprite.texture.get_size()
	sprite.scale.x = new_width / original_size.x

	var new_shape_size = Vector2(new_width, collision_shape.shape.size.y)
	collision_shape.shape.size = new_shape_size
