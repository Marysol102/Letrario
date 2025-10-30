extends Control

@onready var tiles_hbox := $TilesHBox
var TileScene := preload("res://scenes/Tile.tscn")

func _ready() -> void:
    refresh_hand()

func refresh_hand() -> void:
    for c in tiles_hbox.get_children():
        c.queue_free()
    if not Engine.has_singleton("GameManager"):
        return
    var gm = GameManager
    for i in range(gm.hand.size()):
        var letra := gm.hand[i]
        var tile := TileScene.instantiate()
    tile.setup(str(letra), i)
    tile.connect("pressed", Callable(self, "_on_tile_pressed"), [i])
    tiles_hbox.add_child(tile)

func _on_tile_pressed(index: int) -> void:
    # backward-compat: still support opening PlaceWord
    var parent := get_parent()
    if parent and parent.has_method("open_place_word"):
        parent.open_place_word()
        var pw := parent.place_word_panel
        if pw:
            pw.add_tile_from_hand(index)