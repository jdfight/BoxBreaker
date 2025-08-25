extends StaticBody2D

signal brick_destroyed(brick)

const PowerUp = preload("res://scenes/powerup.tscn")
const BrickParticles = preload("res://scenes/brick_particles.tscn")

const BRICK_TEXTURES = {
	1: preload("res://assets/pixmaps/brick.png"),
	2: preload("res://assets/pixmaps/brick_blue.png"),
	3: preload("res://assets/pixmaps/brick_gold.png"),
	4: preload("res://assets/pixmaps/brick_green.png"),
	5: preload("res://assets/pixmaps/brick_orange.png"),
	6: preload("res://assets/pixmaps/brick_purple.png"),
	7: preload("res://assets/pixmaps/brick_black.png"),
	8: preload("res://assets/pixmaps/brick_silver.png"),
}

const BRICK_COLORS = {
	1: Color("firebrick"),
	2: Color("cornflowerblue"),
	3: Color("gold"),
	4: Color("limegreen"),
	5: Color("orange"),
	6: Color("purple"),
	7: Color(0.2, 0.2, 0.2), # Dark gray for black bricks
	8: Color("silver"),
}

var hp: int = 1

@onready var sprite = $Sprite

func _ready():
	add_to_group("bricks")

func set_hp(new_hp: int):
	hp = new_hp
	if BRICK_TEXTURES.has(hp):
		sprite.texture = BRICK_TEXTURES[hp]
		sprite.modulate = BRICK_COLORS.get(hp, Color.WHITE)
	else:
		# Default to the first texture if hp value is invalid
		sprite.texture = BRICK_TEXTURES[1]
		sprite.modulate = BRICK_COLORS[1]

func take_damage():
	hp -= 1
	if hp <= 0:
		destroy_brick()
		AudioManager.play_sound("sfx-01b")
	else:
		set_hp(hp)
		AudioManager.play_sound("sfx-05")

func destroy_brick():
	emit_signal("brick_destroyed", self)

	if randf() < 0.2: # 20% chance to spawn a power-up
		var powerup_types = ["ball", "bomb", "gold", "shot", "ballMulti", "life", "grow"]
		var chosen_type = powerup_types.pick_random()
		var new_powerup = PowerUp.instantiate()
		new_powerup.set_type(chosen_type)
		new_powerup.position = global_position
		get_parent().add_child(new_powerup)

	var particles = BrickParticles.instantiate()
	particles.position = global_position
	particles.initial_velocity_min = 100.0
	particles.initial_velocity_max = 150.0
	particles.emitting = true

	# Set particle color based on brick color
	var brick_color = sprite.modulate
	particles.color = brick_color

	get_parent().add_child(particles)

	queue_free()
