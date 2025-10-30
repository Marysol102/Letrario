extends Button

var tile_letter: String = ""
var tile_index: int = -1

func setup(letter: String, index: int) -> void:
    tile_letter = letter
    tile_index = index
    text = tile_letter
    rect_min_size = Vector2(72, 72)
    focus_mode = Control.FOCUS_NONE

func _ready() -> void:
    # hover and press micro-animations
    connect("mouse_entered", Callable(self, "_on_mouse_entered"))
    connect("mouse_exited", Callable(self, "_on_mouse_exited"))
    connect("pressed", Callable(self, "_on_pressed"))

func _on_mouse_entered() -> void:
    # slight scale up for hover (touch devices will not show hover but desktop will)
    if Engine.is_editor_hint(): return
    var tw = get_tree().create_tween()
    tw.tween_property(self, "rect_scale", Vector2(1.05, 1.05), 0.12).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)

func _on_mouse_exited() -> void:
    var tw = get_tree().create_tween()
    tw.tween_property(self, "rect_scale", Vector2(1, 1), 0.12).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)

func _on_pressed() -> void:
    # quick press feedback
    var tw = get_tree().create_tween()
    tw.tween_property(self, "rect_scale", Vector2(0.9, 0.9), 0.06).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
    tw.tween_property(self, "rect_scale", Vector2(1, 1), 0.12).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)

func get_drag_data(position: Vector2) -> Dictionary:
    var data := {'letter': tile_letter, 'index': tile_index}
    var preview := Label.new()
    preview.text = tile_letter
    preview.rect_min_size = Vector2(72,72)
    set_drag_preview(preview)
    return data
