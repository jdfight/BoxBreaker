extends Area2D

signal powerup_collected(type)

var type: String
var speed: int = 100

const POWERUP_TEXTURES = {
	"ball": preload("res://assets/pixmaps/bonus_ball.png"),
	"bomb": preload("res://assets/pixmaps/bonus_bomb.png"),
	"gold": preload("res://assets/pixmaps/bonus_gold.png"),
	"shot": preload("res://assets/pixmaps/bonus_shot.png"),
	"ballMulti": preload("res://assets/pixmaps/bonus_ballMulti.png"),
	"life": preload("res://assets/pixmaps/bonus_paddle.png"),
	"grow": preload("res://assets/pixmaps/bonus_grow.png"),
}

func _physics_process(delta):
	position.y += speed * delta
	if position.y > get_viewport_rect().size.y + 10:
		queue_free()

func set_type(new_type: String):
	type = new_type
	if POWERUP_TEXTURES.has(type):
		$Sprite2D.texture = POWERUP_TEXTURES[type]
	else:
		# Default to ball if type is invalid
		$Sprite2D.texture = POWERUP_TEXTURES["ball"]
		type = "ball"

func _on_body_entered(body):
	if body.is_in_group("paddle"):
		emit_signal("powerup_collected", type)
		queue_free()
