extends Window

@onready var offers_vbox := $OffersVBox

func _ready() -> void:
    refresh_offers()

func refresh_offers() -> void:
    for c in offers_vbox.get_children():
        c.queue_free()
    if not Engine.has_singleton("GameManager"): return
    var gm = GameManager
    var ofertas := gm.ofertas_tienda
    if ofertas.size() == 0:
        ofertas = gm.generar_ofertas_tienda(3)
    for idm in ofertas:
        var h := HBoxContainer.new()
        var lbl := Label.new()
        lbl.text = "%s - %s M" % [idm, str(gm.MEJORAS_DISPONIBLES[idm]['costo'])]
        var btn := Button.new()
        btn.text = "Comprar"
        btn.connect("pressed", Callable(self, "_on_buy_pressed"), [idm])
        h.add_child(lbl)
        h.add_child(btn)
        offers_vbox.add_child(h)

func _on_buy_pressed(idm: String) -> void:
    if not Engine.has_singleton("GameManager"): return
    var gm = GameManager
    var costo := int(gm.MEJORAS_DISPONIBLES[idm]['costo'])
    if gm.monedas < costo:
        print("Monedas insuficientes")
        return
    var ok := gm.aplicar_mejora(idm)
    if ok:
        gm.monedas -= costo
        print("Mejora %s comprada" % idm)
        refresh_offers()
    else:
        print("No se pudo aplicar mejora %s" % idm)
