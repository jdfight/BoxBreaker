extends Node

var maps = []
var max_level = 0

const MAP_DIR = "res://../py_game/maps"

func _ready():
	load_maps()

func load_maps():
	var dir = DirAccess.open(MAP_DIR)
	if dir:
		dir.list_dir_begin()
		var file_name = dir.get_next()
		var map_files = []
		while file_name != "":
			if file_name.begins_with("map.") and not file_name.ends_with(".import"):
				map_files.append(file_name)
			file_name = dir.get_next()

		map_files.sort_custom(func(a, b): return a.get_slice(".", 1).to_int() < b.get_slice(".", 1).to_int())

		max_level = map_files.size()
		for map_file in map_files:
			var file = FileAccess.open(dir.get_current_dir().path_join(map_file), FileAccess.READ)
			var level_map = []
			while not file.eof_reached():
				var line = file.get_line()
				var row = []
				for char in line:
					if char.is_valid_int():
						row.append(char.to_int())
				if not row.is_empty():
					level_map.append(row)
			maps.append(level_map)
			file.close()
	else:
		print("Error opening map directory: ", MAP_DIR)

func get_map(level_index: int):
	if level_index >= 0 and level_index < maps.size():
		return maps[level_index]
	return null
