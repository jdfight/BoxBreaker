extends Area2D

var speed = 400

func _physics_process(delta):
	position.y -= speed * delta
	if position.y < -10:
		queue_free()

func _on_body_entered(body):
	if body.is_in_group("bricks"):
		body.take_damage()
		queue_free()
