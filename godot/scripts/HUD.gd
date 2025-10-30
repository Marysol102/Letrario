extends Control

@onready var start_button := $Panel/StartButton
@onready var hand_label := $Panel/HandLabel

var HandPanelScene := preload("res://scenes/HandPanel.tscn")
var PlaceWordScene := preload("res://scenes/PlaceWord.tscn")
var ShopScene := preload("res://scenes/Shop.tscn")

var hand_panel
var place_word_panel
var shop_panel

func _ready() -> void:
    start_button.pressed.connect(_on_start_pressed)
    $Panel/PlaceWordButton.connect("pressed", Callable(self, "open_place_word"))
    $Panel/ShopButton.connect("pressed", Callable(self, "open_shop"))
    # Instanciar panels
    hand_panel = HandPanelScene.instantiate()
    add_child(hand_panel)
    hand_panel.rect_position = Vector2(20, 120)

    place_word_panel = PlaceWordScene.instantiate()
    add_child(place_word_panel)
    place_word_panel.visible = false

    shop_panel = ShopScene.instantiate()
    add_child(shop_panel)
    shop_panel.visible = false

    _update_hand_display()
        $Panel/SaveButton.connect("pressed", Callable(self, "_on_save_pressed"))
        $Panel/LoadButton.connect("pressed", Callable(self, "_on_load_pressed"))
    # Try to load an exported Theme resource. If it doesn't exist, create a
    # small runtime fallback so the UI still looks okay.
    var theme_path := "res://godot/assets/theme.tres"
    var theme_res := null
    if FileAccess.file_exists(ProjectSettings.globalize_path(theme_path)):
        theme_res = ResourceLoader.load(theme_path)

    if theme_res and theme_res is Theme:
        self.theme = theme_res
        if hand_panel: hand_panel.theme = theme_res
        if place_word_panel: place_word_panel.theme = theme_res
        if shop_panel: shop_panel.theme = theme_res
    else:
        # Fallback runtime Theme (keeps previous look when theme.tres missing)
        var theme := Theme.new()

        var btn_normal := StyleBoxFlat.new()
        btn_normal.bg_color = Color8(40, 116, 166)
        btn_normal.border_width = 2
        btn_normal.border_color = Color8(255,255,255)
        btn_normal.corner_radius_top_left = 8
        btn_normal.corner_radius_top_right = 8
        btn_normal.corner_radius_bottom_left = 8
        btn_normal.corner_radius_bottom_right = 8
        theme.set_stylebox("normal", "Button", btn_normal)

        var btn_pressed := StyleBoxFlat.new()
        btn_pressed.bg_color = Color8(28, 90, 130)
        btn_pressed.border_width = 2
        btn_pressed.border_color = Color8(220,220,220)
        btn_pressed.corner_radius_top_left = 8
        btn_pressed.corner_radius_top_right = 8
        btn_pressed.corner_radius_bottom_left = 8
        btn_pressed.corner_radius_bottom_right = 8
        theme.set_stylebox("pressed", "Button", btn_pressed)

        theme.set_color("font_color", "Button", Color8(255,255,255))
        theme.set_color("font_color", "Label", Color8(24,24,24))

        # Apply theme to HUD and child panels so controls pick it up
        self.theme = theme
        if hand_panel: hand_panel.theme = theme
        if place_word_panel: place_word_panel.theme = theme
        if shop_panel: shop_panel.theme = theme

func _on_start_pressed() -> void:
    if Engine.has_singleton("GameManager"):
        var gm = GameManager
        gm.reset_estado_inicial()
        _update_hand_display()
        if hand_panel:
            hand_panel.refresh_hand()
    else:
        print("GameManager no cargado como AutoLoad. Revisa project.godot")

func _update_hand_display() -> void:
    if Engine.has_singleton("GameManager"):
        var gm = GameManager
        hand_label.text = "Mano: %s" % str(gm.hand)
    else:
        hand_label.text = "Mano: (GameManager no disponible)"

func open_place_word() -> void:
    place_word_panel.visible = true
    place_word_panel.show()

func close_place_word() -> void:
    place_word_panel.visible = false

func open_shop() -> void:
    shop_panel.visible = true

    func _on_save_pressed() -> void:
        if Engine.has_singleton("GameManager"):
            GameManager.save_state()

    func _on_load_pressed() -> void:
        if Engine.has_singleton("GameManager"):
            var ok := GameManager.load_state()
            if ok:
                if hand_panel and hand_panel.has_method("refresh_hand"):
                    hand_panel.refresh_hand()
                _update_hand_display()

func close_shop() -> void:
    shop_panel.visible = false
