extends Window

@onready var selected_hbox := $SelectedHBox
@onready var confirm_btn := $ButtonsVBox/ConfirmButton
@onready var cancel_btn := $ButtonsVBox/CancelButton
@onready var wildcard_dialog := $WildcardDialog
@onready var wildcard_line := $WildcardDialog/WildcardLine

var selected_indices := []
var wildcard_map := {} # index -> chosen letter for '*' tiles
var manual_mode := false

func _ready() -> void:
    confirm_btn.pressed.connect(_on_confirm_pressed)
    cancel_btn.pressed.connect(_on_cancel_pressed)

func add_tile_from_hand(index: int) -> void:
    if not Engine.has_singleton("GameManager"): return
    var gm = GameManager
    if index < 0 or index >= gm.hand.size(): return
    var letra := str(gm.hand[index])
    if letra == '*':
        # pedir letra para comodín
        wildcard_dialog.popup()
        wildcard_dialog.connect("confirmed", Callable(self, "_on_wildcard_confirmed"), [index])
        return
    selected_indices.append(index)
    _refresh_selected()

func get_drag_data(position: Vector2):
    # Placeholder to prevent errors; tiles provide drag data themselves
    return null

func can_drop_data(position: Vector2, data) -> bool:
    return typeof(data) == TYPE_DICTIONARY and data.has('letter') and data.has('index')

func drop_data(position: Vector2, data) -> void:
    # Add the dragged tile's index to selection
    var idx := int(data['index'])
    if idx in selected_indices:
        return
    selected_indices.append(idx)
    _refresh_selected()

func _refresh_selected() -> void:
    for c in selected_hbox.get_children():
        c.queue_free()
    if not Engine.has_singleton("GameManager"): return
    var gm = GameManager
    for idx in selected_indices:
        var btn := Button.new()
        btn.text = str(gm.hand[idx])
        btn.connect("pressed", Callable(self, "_on_selected_tile_pressed"), [idx])
        selected_hbox.add_child(btn)

func _on_confirm_pressed() -> void:
    if not Engine.has_singleton("GameManager"): return
    var gm = GameManager
    # If manual entry present, use it; otherwise build from selected indices
    var palabra := ""
    var fichas := ""
    var manual_text := $ManualEntry.text.strip_edges()
    if manual_text != "":
        palabra = gm.normalizar_palabra(manual_text)
        # assume fichas equal letters (no comodines) when manual
        fichas = palabra
    else:
        # Ordenar indices por posición para evitar errores
        selected_indices.sort()
        for idx in selected_indices:
            var ch := str(gm.hand[idx])
            if ch == '*':
                var chosen := wildcard_map.get(idx, '')
                if chosen == '':
                    chosen = 'A'
                palabra += chosen
                fichas += '*'
            else:
                palabra += ch
                fichas += ch
    var mald := gm.aplicar_maldicion(gm.nivel_actual)
    var res := gm.validar_y_puntuar(palabra, fichas, mald)
    if res['valida']:
        # Remover letras consumidas
        var nueva := gm.consumir_letras(gm.hand, fichas, palabra, mald)
        if nueva != null:
            gm.hand = nueva
            # Reponer
            var a_reponer := fichas.length()
            var robadas := gm.repartir_mano(a_reponer)
            # Actualizar estado
            gm.puntuacion_actual += int(res['puntos'])
            print("Puntos añadidos: %d" % int(res['puntos']))
            # Actualizar UI: refrescar hand panel si existe en el padre
            var parent := get_parent()
            if parent and parent.has_node("HandPanel"):
                var hp = parent.get_node("HandPanel")
                if hp and hp.has_method("refresh_hand"):
                    hp.refresh_hand()
                if parent and parent.has_method("_update_hand_display"):
                    parent._update_hand_display()
    else:
        print("Palabra no válida o sin puntuación")
    # limpiar y ocultar
    wildcard_map.clear()
    selected_indices.clear()
    _refresh_selected()
    visible = false

func _on_cancel_pressed() -> void:
    selected_indices.clear()
    _refresh_selected()
    visible = false

func _on_selected_tile_pressed(idx: int) -> void:
    # quitar selección tocando
    if idx in selected_indices:
        selected_indices.erase(idx)
        if wildcard_map.has(idx):
            wildcard_map.erase(idx)
        _refresh_selected()

func _on_wildcard_confirmed(index: int) -> void:
    var val := wildcard_line.text.strip_edges().to_upper()
    if val == "" or val.length() != 1:
        val = "A"
    wildcard_map[index] = val
    # desconectar para evitar múltiples conexiones
    if wildcard_dialog.is_connected("confirmed", Callable(self, "_on_wildcard_confirmed")):
        wildcard_dialog.disconnect("confirmed", Callable(self, "_on_wildcard_confirmed"))
    # agregar la ficha '*' a la selección
    selected_indices.append(index)
    _refresh_selected()
