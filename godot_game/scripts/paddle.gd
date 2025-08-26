extends CharacterBody2D

const LERP_FACTOR = 0.2

func _ready():
	add_to_group("paddle")

@onready var sprite = $Sprite
@onready var collision_shape = $CollisionShape

func _physics_process(delta):
	# Calculate target position, clamped within screen bounds
	var screen_width = get_viewport_rect().size.x
	var paddle_width = sprite.get_rect().size.x / 2
	var target_x = clamp(get_global_mouse_position().x, paddle_width, screen_width - paddle_width)

	# Set velocity to move towards the target X position
	# The multiplier controls how quickly it follows the mouse (like a lerp factor)
	velocity.x = (target_x - position.x) * 15
	velocity.y = 0 # Ensure no vertical movement

	move_and_slide()

func resize_paddle(new_width: float):
	var original_size = sprite.texture.get_size()
	sprite.scale.x = new_width / original_size.x

	var new_shape_size = Vector2(new_width, collision_shape.shape.size.y)
	collision_shape.shape.size = new_shape_size

func reset_paddle():
	var screen_width = get_viewport_rect().size.x
	position.x = screen_width / 2
