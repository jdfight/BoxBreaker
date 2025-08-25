extends Node

var sound_players = []
const MAX_SOUND_PLAYERS = 16

const SOUNDS = {
	"sfx-01": preload("res://assets/audio/sfx-01.mp3"),
	"sfx-01b": preload("res://assets/audio/sfx-01b.mp3"),
	"sfx-02": preload("res://assets/audio/sfx-02.mp3"),
	"sfx-03": preload("res://assets/audio/sfx-03.mp3"),
	"sfx-04": preload("res://assets/audio/sfx-04.mp3"),
	"sfx-05": preload("res://assets/audio/sfx-05.mp3"),
	"sfx-06": preload("res://assets/audio/sfx-06.mp3"),
	"sfx-07": preload("res://assets/audio/sfx-07.mp3"),
	"sfx-08": preload("res://assets/audio/sfx-08.mp3"),
	"sfx-09": preload("res://assets/audio/sfx-09.mp3"),
}

func _ready():
	for i in range(MAX_SOUND_PLAYERS):
		var player = AudioStreamPlayer.new()
		add_child(player)
		sound_players.append(player)

func play_sound(sound_name):
	if SOUNDS.has(sound_name):
		for player in sound_players:
			if not player.playing:
				player.stream = SOUNDS[sound_name]
				player.play()
				return
