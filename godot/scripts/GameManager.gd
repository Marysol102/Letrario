extends Node

# GameManager completo: gestor del estado del juego (portado desde LLSP.py)
# Diseñado como AutoLoad (ver project.godot). No depende del editor.

@export var hand_size: int = 7

var diccionario_set: Dictionary = {}
var distribution: Dictionary = {}
var bag: Array = []
var hand: Array = []

var puntuaciones_letras: Dictionary = {
    'A':1,'E':1,'O':1,'S':1,'I':1,'U':1,'N':1,'R':1,'T':1,
    'D':2,'G':2,'L':2,'C':3,'M':3,'B':3,'P':3,'F':4,'H':4,'V':4,'Y':4,
    'Q':5,'J':8,'Ñ':8,'X':8,'K':10,'Z':10,'W':10,'*':0
}

var nivel_longitudes: Dictionary = {2:1,3:1,4:1,5:1,6:1,7:1}
var multiplicadores_posicion: Dictionary = {0:1,1:1,2:1,3:1,4:1,5:1,6:1}

# Mejoras y maldiciones (estructuras mínimas, expandibles)
var mejoras_adquiridas: Array = []
var MEJORAS_DISPONIBLES: Dictionary = {
    'U01': {'nombre':'Diccionario Mayor','costo':1,'descripcion':'Letras 1 punto valen 2 (perm).'},
    'U02': {'nombre':'Mano Extendida','costo':1,'descripcion':'Aumenta tamaño mano +1 (max10).'},
    'U03': {'nombre':'Bolsa Reforzada','costo':1,'descripcion':'Aumenta límite de descartes del próximo nivel.'},
    'U04': {'nombre':'Multiplicador Vocal','costo':1,'descripcion':'x2 si 3+ vocales distintas.'},
    'U06': {'nombre':'Economía de Descarte','costo':1,'descripcion':'Descartes valen doble.'},
    'U07': {'nombre':'Ronda de Bono','costo':1,'descripcion':'Comienzas cada nivel con +1 ronda máxima.'},
    'U08': {'nombre':'Nivel L2','costo':2,'descripcion':'Sube el nivel de puntuación de palabras de 2 letras.'},
    'U09': {'nombre':'Nivel L3','costo':2,'descripcion':'Sube el nivel de puntuación de palabras de 3 letras.'},
    'U10': {'nombre':'Nivel L4','costo':3,'descripcion':'Sube el nivel de puntuación de palabras de 4 letras.'},
    'U11': {'nombre':'Nivel L5','costo':3,'descripcion':'Sube el nivel de puntuación de palabras de 5 letras.'},
    'U12': {'nombre':'Nivel L6','costo':4,'descripcion':'Sube el nivel de puntuación de palabras de 6 letras.'},
    'U13': {'nombre':'Nivel L7+','costo':4,'descripcion':'Sube el nivel de puntuación de palabras de 7+ letras.'},
    'U14': {'nombre':'Posición x2 (1)','costo':2,'descripcion':'x2 en posición 1.'},
    'U15': {'nombre':'Posición x2 (2)','costo':2,'descripcion':'x2 en posición 2.'},
    'U16': {'nombre':'Posición x2 (3)','costo':2,'descripcion':'x2 en posición 3.'},
    'U17': {'nombre':'Posición x2 (4)','costo':2,'descripcion':'x2 en posición 4.'},
    'U18': {'nombre':'Posición x3 (5)','costo':3,'descripcion':'x3 en posición 5.'},
    'U19': {'nombre':'Posición x5 (6)','costo':4,'descripcion':'x5 en posición 6.'},
    'U20': {'nombre':'Posición x6 (7)','costo':5,'descripcion':'x6 en posición 7.'},
    'U21': {'nombre':'Posición x2 (1-3)','costo':3,'descripcion':'x2 en posiciones 1,2,3.'},
    'U22': {'nombre':'Posición x3 (4-7)','costo':5,'descripcion':'x3 en posiciones 4-7.'}
}

var MALDICIONES: Dictionary = {
    'C_NOPUNTO_4LETRAS':'Las palabras de 4 letras o menos no dan PUNTOS.',
    'C_VOCALES_MEDIAS':'Las vocales puntúan la MITAD.',
    'C_NOPA':'La letra A no puntúa NADA.'
}

var ofertas_tienda: Array = []
var monedas: int = 0
var nivel_actual: int = 1
var puntuacion_actual: int = 0
var rondas_maximas: int = 5
var descartes_restantes: int = 3

var rng := RandomNumberGenerator.new()

func _ready() -> void:
    rng.randomize()
    _load_distribution()
    var dic_path := "res://data/diccionario.es.txt"
    if FileAccess.file_exists(dic_path):
        cargar_diccionario(dic_path)
    else:
        push_warning("No se encontró 'res://data/diccionario.es.txt'. Copia tu diccionario en esa ruta.")

func _load_distribution() -> void:
    distribution = {
        'A':12,'E':12,'O':9,'S':6,'I':6,'U':5,'N':5,'R':6,'T':4,
        'D':5,'G':2,'L':5,'C':4,'M':2,'B':2,'P':2,'F':1,'H':2,'V':1,'Y':1,
        'Q':1,'J':1,'Ñ':1,'X':1,'K':1,'Z':1,'W':1,'*':4
    }

func normalizar_palabra(palabra: String) -> String:
    var p := palabra.to_upper()
    p = p.replace("Á","A").replace("É","E").replace("Í","I").replace("Ó","O").replace("Ú","U").replace("Ü","U")
    return p

func cargar_diccionario(ruta: String) -> bool:
    if not FileAccess.file_exists(ruta):
        push_error("Diccionario no encontrado: %s" % ruta)
        return false

    diccionario_set.clear()
    var f := FileAccess.open(ruta, FileAccess.READ)
    if f == null:
        push_error("No se pudo abrir: %s" % ruta)
        return false

    while not f.eof_reached():
        var line := f.get_line().strip_edges()
        if line != "":
            var w := normalizar_palabra(line)
            diccionario_set[w] = true

    f.close()
    print("✅ Diccionario cargado: %d palabras." % diccionario_set.size())
    return true

func inicializar_bolsa_completa() -> void:
    bag.clear()
    for letra in distribution.keys():
        var cant := int(distribution[letra])
        for i in range(cant):
            bag.append(letra)
    rng.shuffle(bag)
    print("🎲 Bolsa inicializada: %d fichas." % bag.size())

func repartir_mano(tamano: int) -> Array:
    var num := min(tamano, bag.size())
    var drawn := []
    for i in range(num):
        var idx := rng.randi_range(0, bag.size() - 1)
        drawn.append(bag[idx])
        bag.remove_at(idx)
    hand = hand + drawn
    return drawn

func revolver_mano() -> void:
    rng.shuffle(hand)
    print("Mano revuelta: %s" % str(hand))

func obtener_multiplicador_longitud(longitud: int) -> int:
    var long_clave := min(longitud, 7)
    var nivel := nivel_longitudes.get(long_clave, 1)
    var multi_base := 1
    if longitud <= 3:
        multi_base = 3
    elif longitud == 4:
        multi_base = 4
    elif longitud == 5:
        multi_base = 5
    elif longitud == 6:
        multi_base = 7
    else:
        multi_base = 9
    return multi_base + (nivel - 1)

func obtener_bono_longitud(longitud: int) -> int:
    var long_clave := min(longitud, 7)
    var nivel := nivel_longitudes.get(long_clave, 1)
    var bono_base := 0
    if longitud == 2:
        bono_base = 30
    elif longitud == 3:
        bono_base = 60
    elif longitud == 4:
        bono_base = 160
    elif longitud == 5:
        bono_base = 300
    elif longitud == 6:
        bono_base = 560
    elif longitud >= 7:
        bono_base = 900
    return bono_base + (nivel - 1) * 30

func calcular_puntuacion(palabra_resultante: String, fichas_usadas_str: String) -> int:
    if palabra_resultante.length() != fichas_usadas_str.length():
        return 0
    var puntuacion_total := 0
    for i in range(min(palabra_resultante.length(), 7)):
        var letra := palabra_resultante[i]
        var valor := int(puntuaciones_letras.get(letra, 0))
        var mult := int(multiplicadores_posicion.get(i, 1))
        puntuacion_total += valor * mult
    return puntuacion_total

func es_valida_en_dic(palabra: String) -> bool:
    return diccionario_set.has(normalizar_palabra(palabra))

func consumir_letras(hand_actual: Array, fichas_usadas: String, palabra_resultante: String, maldicion_activa: String = "") -> Array:
    # Verifica y remueve fichas de la mano, devuelve nueva mano o null si no válido
    var temp := hand_actual.duplicate()

    # Contar requerimientos por letra
    var requeridos := {}
    for ch in fichas_usadas:
        var s := String(ch)
        requeridos[s] = requeridos.get(s, 0) + 1

    # Si maldición C_DOBLE_RONDA activa, aumentar requeridos por repeticiones
    if maldicion_activa == 'C_DOBLE_RONDA':
        for k in requeridos.keys():
            var cuenta := int(requeridos[k])
            if cuenta > 1:
                # por cada repetición adicional, exigir una ficha extra
                requeridos[k] = cuenta + (cuenta - 1)

    # Verificar disponibilidad
    for letra in requeridos.keys():
        var need := int(requeridos[letra])
        var available := 0
        for t in temp:
            if String(t) == String(letra):
                available += 1
        if available < need:
            return null

    # Remover las fichas requeridas
    for letra in requeridos.keys():
        var need := int(requeridos[letra])
        while need > 0:
            temp.remove_at(temp.find(letra))
            need -= 1

    return temp

func descartar_y_robar(mano_actual: Array, letras_a_descartar: Array) -> Array:
    var temp := mano_actual.duplicate()
    var confirmed := []
    for letra in letras_a_descartar:
        if letra == '*':
            if temp.has('*'):
                temp.remove_at(temp.find('*'))
                confirmed.append('*')
        else:
            var ln := normalizar_palabra(String(letra))
            if temp.has(ln):
                temp.remove_at(temp.find(ln))
                confirmed.append(ln)
    if confirmed.size() == 0:
        return mano_actual
    var robadas := repartir_mano(confirmed.size())
    temp = temp + robadas
    hand = temp
    return hand

func calcular_recompensa(puntuacion_obtenida: int, descartes_rest: int) -> int:
    var monedas_puntos := max(0, puntuacion_obtenida) / 10
    var multiplicador_descarte := 2 if mejoras_adquiridas.has('U06') else 1
    var monedas_desc := descartes_rest * multiplicador_descarte
    var total := int(monedas_puntos) + int(monedas_desc)
    return total

func aplicar_mejora(id_mejora: String) -> bool:
    # U02 escalable
    if id_mejora == 'U02':
        if hand_size < 10:
            hand_size += 1
            if not mejoras_adquiridas.has(id_mejora):
                mejoras_adquiridas.append(id_mejora)
            MEJORAS_DISPONIBLES[id_mejora]['nombre'] = 'Mano Extendida (T%d)' % hand_size
            return true
        return false

    # Permanentes simples
    if id_mejora == 'U01' and not mejoras_adquiridas.has('U01'):
        for l in puntuaciones_letras.keys():
            if int(puntuaciones_letras[l]) == 1:
                puntuaciones_letras[l] = 2
        mejoras_adquiridas.append('U01')
        return true

    if id_mejora in ['U03','U04','U06','U07'] and not mejoras_adquiridas.has(id_mejora):
        mejoras_adquiridas.append(id_mejora)
        return true

    # Mejora por niveles U08..U13
    var niveles_map := {'U08':2,'U09':3,'U10':4,'U11':5,'U12':6,'U13':7}
    if id_mejora in niveles_map:
        var longitud := niveles_map[id_mejora]
        nivel_longitudes[longitud] = nivel_longitudes.get(longitud,1) + 1
        if not mejoras_adquiridas.has(id_mejora):
            mejoras_adquiridas.append(id_mejora)
        MEJORAS_DISPONIBLES[id_mejora]['nombre'] = 'Nivel L%d (N%d)' % [longitud, nivel_longitudes[longitud]]
        return true

    # Mejora por posición U14..U22
    var pos_map := {
        'U14': {0:2}, 'U15': {1:2}, 'U16': {2:2}, 'U17': {3:2},
        'U18': {4:3}, 'U19': {5:5}, 'U20': {6:6}, 'U21': {0:2,1:2,2:2}, 'U22': {3:3,4:3,5:3,6:3}
    }
    if id_mejora in pos_map:
        if mejoras_adquiridas.has(id_mejora):
            return false
        var nuevos := pos_map[id_mejora]
        for k in nuevos.keys():
            multiplicadores_posicion[k] = nuevos[k]
        mejoras_adquiridas.append(id_mejora)
        return true

    return false

func generar_ofertas_tienda(num_ofertas: int = 3) -> Array:
    var all := MEJORAS_DISPONIBLES.keys()
    var pool := []
    for idm in all:
        if idm == 'U02' and hand_size >= 10:
            continue
        if idm in ['U01','U03','U04','U06','U07'] and idm in mejoras_adquiridas:
            continue
        pool.append(idm)
    var n := min(pool.size(), num_ofertas)
    var ofertas := []
    for i in range(n):
        var idx := rng.randi_range(0, pool.size() - 1)
        ofertas.append(pool[idx])
        pool.remove_at(idx)
    ofertas_tienda = ofertas
    return ofertas

func aplicar_maldicion(nivel: int) -> String:
    if nivel > 0 and nivel % 3 == 0:
        var claves := MALDICIONES.keys()
        var indice := int((nivel / 3 - 1) % claves.size())
        var clave := claves[indice]
        return clave
    return ""

func validar_y_puntuar(palabra: String, fichas_usadas: String, maldicion_activa: String = "") -> Dictionary:
    var result := {'puntos':0,'valida':false}
    if palabra == "":
        return result
    var norm := normalizar_palabra(palabra)
    if not es_valida_en_dic(norm):
        return result
    var puntuacion := calcular_puntuacion(norm, fichas_usadas)
    var puntuacion_antes := puntuacion
    if puntuacion > 0:
        var mult := obtener_multiplicador_longitud(norm.length())
        puntuacion *= mult
    # Aplicar maldiciones simples
    if maldicion_activa == 'C_NOPUNTO_4LETRAS' and norm.length() <= 4:
        puntuacion = 0
    if maldicion_activa == 'C_VOCALES_MEDIAS':
        var mod := 0
        for i in range(min(norm.length(), fichas_usadas.length())):
            var l := norm[i]
            var val := int(puntuaciones_letras.get(l, 0))
            if l in ['A','E','I','O','U']:
                val = val / 2
            mod += val * int(multiplicadores_posicion.get(i,1))
        puntuacion = mod * obtener_multiplicador_longitud(norm.length()) if mod > 0 else 0
    if maldicion_activa == 'C_NOPA':
        var mod2 := 0
        for i in range(min(norm.length(), fichas_usadas.length())):
            var l := norm[i]
            var val := int(puntuaciones_letras.get(l, 0))
            if l == 'A':
                val = 0
            mod2 += val * int(multiplicadores_posicion.get(i,1))
        puntuacion = mod2 * obtener_multiplicador_longitud(norm.length()) if mod2 > 0 else 0
    # U04: multiplicador vocal (3+ distintas)
    if puntuacion > 0 and mejoras_adquiridas.has('U04'):
        var vocales := {}
        for ch in norm:
            if ch in ['A','E','I','O','U']:
                vocales[ch] = true
        if vocales.size() >= 3:
            puntuacion *= 2
    # Bono fijo
    if puntuacion > 0:
        var bono := obtener_bono_longitud(norm.length())
        puntuacion += bono
    result['puntos'] = int(puntuacion)
    result['valida'] = puntuacion > 0 or (calcular_puntuacion(norm, fichas_usadas) > 0)
    return result

func reset_estado_inicial() -> void:
    mejoras_adquiridas.clear()
    monedas = 0
    nivel_actual = 1
    puntuacion_actual = 0
    descartes_restantes = 3
    multiplicadores_posicion = {0:1,1:1,2:1,3:1,4:1,5:1,6:1}
    nivel_longitudes = {2:1,3:1,4:1,5:1,6:1,7:1}
    inicializar_bolsa_completa()
    hand.clear()
    repartir_mano(hand_size)

func save_state() -> bool:
    var data := {
        'mejoras_adquiridas': mejoras_adquiridas.duplicate(),
        'monedas': monedas,
        'nivel_actual': nivel_actual,
        'puntuacion_actual': puntuacion_actual,
        'hand_size': hand_size,
        'nivel_longitudes': nivel_longitudes,
        'multiplicadores_posicion': multiplicadores_posicion,
        'hand': hand.duplicate(),
        'bag': bag.duplicate()
    }
    var path := "user://savegame.json"
    var f := FileAccess.open(path, FileAccess.WRITE)
    if f == null:
        push_error("No se pudo abrir save para escribir: %s" % path)
        return false
    f.store_string(JSON.print(data))
    f.close()
    print("✅ Juego guardado en %s" % path)
    return true

func load_state() -> bool:
    var path := "user://savegame.json"
    if not FileAccess.file_exists(path):
        return false
    var f := FileAccess.open(path, FileAccess.READ)
    if f == null:
        return false
    var content := f.get_as_text()
    f.close()
    var parsed := JSON.parse_string(content)
    if parsed.error != OK:
        push_error("Error parseando save: %s" % str(parsed.error))
        return false
    var data := parsed.result
    mejoras_adquiridas = data.get('mejoras_adquiridas', [])
    monedas = int(data.get('monedas', 0))
    nivel_actual = int(data.get('nivel_actual', 1))
    puntuacion_actual = int(data.get('puntuacion_actual', 0))
    hand_size = int(data.get('hand_size', 7))
    nivel_longitudes = data.get('nivel_longitudes', nivel_longitudes)
    multiplicadores_posicion = data.get('multiplicadores_posicion', multiplicadores_posicion)
    hand = data.get('hand', [])
    bag = data.get('bag', [])
    print("✅ Save cargado desde %s" % path)
    return true
