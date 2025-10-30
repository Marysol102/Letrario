import random
import unicodedata 
import re 
import math 

# =================================================================
# 1. CONSTANTES Y ESTADO DEL JUEGO
# =================================================================

PUNTUACIONES_LETRAS = {
    'A': 1, 'E': 1, 'O': 1, 'S': 1, 'I': 1, 'U': 1, 'N': 1, 'R': 1, 'T': 1,
    'D': 2, 'G': 2, 'L': 2,
    'C': 3, 'M': 3, 'B': 3, 'P': 3,
    'F': 4, 'H': 4, 'V': 4, 'Y': 4,
    'Q': 5,
    'J': 8, 'Ñ': 8, 'X': 8, 
    'K': 10, 'Z': 10, 'W': 10,
    '*': 0 
}
VOCALES = set(['A', 'E', 'I', 'O', 'U'])

# --- ESTADO DE NIVELES DE PUNTUACIÓN (Nivel 1 es el valor base original) ---
NIVEL_LONGITUDES = {
    2: 1, 
    3: 1, 
    4: 1, 
    5: 1, 
    6: 1, 
    7: 1  # 7 se usa para 7 o más
}

# --- ESTADO DE MULTIPLICADORES POR POSICIÓN (Índice 0 a 6) ---
MULTIPLICADORES_POSICION = {
    0: 1, # Posición 1
    1: 1, # Posición 2
    2: 1, # Posición 3
    3: 1, # Posición 4
    4: 1, # Posición 5
    5: 1, # Posición 6
    6: 1  # Posición 7
}

# --- ESTADO DE TAMAÑO DE MANO ESCALABLE ---
# Base 7. Se incrementa con U02. Máximo 10.
TAMANO_MANO_ACTUAL = 7

# --- DISTRIBUCIÓN MODIFICADA ---
DISTRIBUCION_ESPANOL = {
    'A': 12, 'E': 12, 'O': 9, 'S': 6, 'I': 6, 'U': 5, 'N': 5, 'R': 6, 'T': 4,
    'D': 5, 'G': 2, 'L': 5,
    'C': 4, 'M': 2, 'B': 2, 'P': 2,
    'F': 1, 'H': 2, 'V': 1, 'Y': 1,
    'Q': 1, 'J': 1, 'Ñ': 1, 'X': 1, 
    'K': 1, 'Z': 1, 'W': 1,
    '*': 4  
}

MEJORAS_DISPONIBLES = {
    'U01': {'nombre': 'Diccionario Mayor', 'costo': 1, 'descripcion': 'Letras de 1 punto valen 2 (Permanente).'},
    # U02 MODIFICADA: Ahora es escalable y se puede comprar varias veces.
    'U02': {'nombre': 'Mano Extendida', 'costo': 1, 'descripcion': 'Aumenta el tamaño de tu mano en +1 (Máx 10).'}, 
    'U03': {'nombre': 'Bolsa Reforzada', 'costo': 1, 'descripcion': 'Aumenta el límite de descartes del próximo nivel en +1.'},
    # U04 MODIFICADA: Ahora solo requiere 3 vocales diferentes.
    'U04': {'nombre': 'Multiplicador Vocal', 'costo': 1, 'descripcion': 'Doble puntuación si la palabra usa 3+ vocales diferentes.'},
    # U05 ELIMINADA.
    'U06': {'nombre': 'Economía de Descarte', 'costo': 1, 'descripcion': 'Los descartes valen el doble de monedas al final del nivel (Permanente).'},
    'U07': {'nombre': 'Ronda de Bono', 'costo': 1, 'descripcion': 'Comienzas cada nivel con +1 ronda máxima (Permanente).'},
    'U08': {'nombre': 'Nivel L2', 'costo': 2, 'descripcion': 'Sube el nivel de puntuación de palabras de 2 letras (+1x, +30 Bono)'},
    'U09': {'nombre': 'Nivel L3', 'costo': 2, 'descripcion': 'Sube el nivel de puntuación de palabras de 3 letras (+1x, +30 Bono)'},
    'U10': {'nombre': 'Nivel L4', 'costo': 3, 'descripcion': 'Sube el nivel de puntuación de palabras de 4 letras (+1x, +30 Bono)'},
    'U11': {'nombre': 'Nivel L5', 'costo': 3, 'descripcion': 'Sube el nivel de puntuación de palabras de 5 letras (+1x, +30 Bono)'},
    'U12': {'nombre': 'Nivel L6', 'costo': 4, 'descripcion': 'Sube el nivel de puntuación de palabras de 6 letras (+1x, +30 Bono)'},
    'U13': {'nombre': 'Nivel L7+', 'costo': 4, 'descripcion': 'Sube el nivel de puntuación de palabras de 7+ letras (+1x, +30 Bono)'},
    'U14': {'nombre': 'Posición x2 (1)', 'costo': 2, 'descripcion': 'Duplica el valor de la letra colocada en la primera posición de la palabra.'},
    'U15': {'nombre': 'Posición x2 (2)', 'costo': 2, 'descripcion': 'Duplica el valor de la letra colocada en la segunda posición de la palabra.'},
    'U16': {'nombre': 'Posición x2 (3)', 'costo': 2, 'descripcion': 'Duplica el valor de la letra colocada en la tercera posición de la palabra.'},
    'U17': {'nombre': 'Posición x2 (4)', 'costo': 2, 'descripcion': 'Duplica el valor de la letra colocada en la cuarta posición de la palabra.'},
    'U18': {'nombre': 'Posición x3 (5)', 'costo': 3, 'descripcion': 'Triplica el valor de la letra colocada en la quinta posición de la palabra.'},
    'U19': {'nombre': 'Posición x5 (6)', 'costo': 4, 'descripcion': 'Quintuplica el valor de la letra colocada en la sexta posición de la palabra.'},
    'U20': {'nombre': 'Posición x6 (7)', 'costo': 5, 'descripcion': 'Multiplica x6 el valor de la letra colocada en la séptima posición de la palabra.'},
    'U21': {'nombre': 'Posición x2 (1-3)', 'costo': 3, 'descripcion': 'Duplica el valor de las letras en las posiciones 1, 2 y 3.'},
    'U22': {'nombre': 'Posición x3 (4-7)', 'costo': 5, 'descripcion': 'Triplica el valor de las letras en las posiciones 4, 5, 6 y 7.'}
}

MALDICIONES = {
    'C_NOPUNTO_4LETRAS': 'Las palabras de 4 letras o menos no dan PUNTOS.',
    'C_VOCALES_MEDIAS': 'Las vocales (A, E, I, O, U) puntúan la MITAD (Redondeado abajo).',
    'C_NOPA': 'La letra A no puntúa NADA (vale 0 puntos).',
    'C_IMPARES_CERO': 'Las palabras con un número IMPAR de letras (3, 5, 7...) no puntúan.',
    'C_DOBLE_RONDA': 'Usar la misma letra dos veces en una palabra consume DOBLE de letras por esa letra.'
}

# =================================================================
# 2. FUNCIONES BASE DEL JUEGO Y PUNTUACIÓN
# =================================================================

# --- FUNCIÓN DE MULTIPLICADOR (POR NIVEL) ---
def obtener_multiplicador_longitud(longitud):
    """Devuelve el multiplicador BASADO EN EL NIVEL DE LA PALABRA."""
    long_clave = min(longitud, 7)
    nivel = NIVEL_LONGITUDES.get(long_clave, 1) 
    
    if longitud <= 3:
        multi_base = 3
    elif longitud == 4:
        multi_base = 4
    elif longitud == 5:
        multi_base = 5
    elif longitud == 6:
        multi_base = 7 
    else: # longitud >= 7
        multi_base = 9 
    
    return multi_base + (nivel - 1) 

# --- FUNCIÓN DE BONO FIJO (POR NIVEL) ---
def obtener_bono_longitud(longitud):
    """Devuelve el bono de puntos fijos BASADO EN EL NIVEL DE LA PALABRA."""
    long_clave = min(longitud, 7)
    nivel = NIVEL_LONGITUDES.get(long_clave, 1)
    
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
    else:
        bono_base = 0
        
    return bono_base + (nivel - 1) * 30
# --- FIN MODIFICACIONES ---

# --- FUNCIÓN NORMALIZAR ---
def normalizar_palabra(palabra):
    """
    Convierte a mayúsculas, elimina tildes de vocales y diéresis, PRESERVANDO la Ñ.
    """
    palabra_mayus = palabra.upper()
    replacements = {
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ü': 'U'
    }
    palabra_procesada = palabra_mayus
    for accented, normal in replacements.items():
        palabra_procesada = palabra_procesada.replace(accented, normal)
    
    return palabra_procesada

def parsear_input_comodin(input_str):
    """Parsea una cadena con notación de comodín (*L*)."""
    input_str_norm = normalizar_palabra(input_str)
    palabra_resultante = ""
    fichas_usadas_str = ""
    
    matches = re.findall(r'(\*[A-ZÑ]\*|[A-ZÑ])', input_str_norm)
    
    if not matches: return None, None
    
    reconstruido = "".join(matches)
    if reconstruido != input_str_norm.replace(" ", ""):
         print(f"Error de formato en comodín: '{input_str}'. Usa *L* para una letra.")
         return None, None

    for match in matches:
        if match.startswith('*') and match.endswith('*') and len(match) == 3:
            palabra_resultante += match[1]
            fichas_usadas_str += '*'
        elif len(match) == 1 and match in PUNTUACIONES_LETRAS:
            palabra_resultante += match
            fichas_usadas_str += match
        else:
             print(f"Error interno parseando '{match}' en '{input_str}'.")
             return None, None

    return palabra_resultante, fichas_usadas_str


def cargar_diccionario(ruta_archivo):
    """Carga el diccionario, normalizando las palabras."""
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            palabras = {normalizar_palabra(linea.strip()) for linea in f if linea.strip()}
        print(f"✅ Diccionario cargado: {len(palabras)} palabras.")
        return palabras
    except FileNotFoundError:
        print(f"❌ Error: No se encontró '{ruta_archivo}'")
        return None

def calcular_puntuacion(palabra_resultante, fichas_usadas_str):
    """
    Calcula la puntuación base, aplicando MULTIPLICADORES DE POSICIÓN.
    """
    puntuacion_total = 0
    if len(palabra_resultante) != len(fichas_usadas_str): return 0

    for i, ficha in enumerate(fichas_usadas_str):
        if i >= 7: 
            break # Límite de posición 7 (índice 6)
            
        letra_resultante = palabra_resultante[i]
        
        # 1. Obtener valor base de la letra (incluye U01 si aplica)
        valor_base = PUNTUACIONES_LETRAS.get(letra_resultante, 0)
        
        # 2. Obtener multiplicador por posición (índice 'i')
        multiplicador_pos = MULTIPLICADORES_POSICION.get(i, 1)
        
        # 3. Aplicar y sumar
        puntuacion_letra = valor_base * multiplicador_pos
        puntuacion_total += puntuacion_letra

        if multiplicador_pos > 1:
             print(f"   [P{i+1}: x{multiplicador_pos}] {letra_resultante} ({valor_base} * {multiplicador_pos} = {puntuacion_letra} pts)")

    return puntuacion_total


def validar_y_puntuar(palabra_resultante, fichas_usadas_str, diccionario_valido, mejoras_adquiridas, maldicion_activa):
    """
    Valida la palabra, calcula puntuación, aplica multiplicadores,
    maldiciones/mejoras y BONO FIJO (incl. nivel).
    """
    if not palabra_resultante: return 0, False

    # 1. VERIFICACIÓN DE VALIDEZ
    if palabra_resultante not in diccionario_valido:
        print(f"👎 Palabra no válida: '{palabra_resultante}' no está en el diccionario.")
        return 0, False

    # 2. CALCULAR PUNTUACIÓN BASE Y MULTIPLICADOR DE LONGITUD
    puntuacion = calcular_puntuacion(palabra_resultante, fichas_usadas_str)
    puntuacion_antes_maldicion = puntuacion 

    if puntuacion > 0:
        longitud = len(palabra_resultante)
        multiplicador = obtener_multiplicador_longitud(longitud)
        puntuacion_base = puntuacion
        puntuacion *= multiplicador
        print(f"✨ Multiplicador x{multiplicador} por longitud ({longitud} letras): {puntuacion_base} -> {puntuacion}")
        puntuacion_antes_maldicion = puntuacion 
    
    # 3. LÓGICA DE MALDICIONES (Mantiene la lógica anterior)
    if maldicion_activa:
        if maldicion_activa == 'C_NOPUNTO_4LETRAS' and len(palabra_resultante) <= 4:
            print(f"💀 Maldición: Palabras <= 4 letras no puntúan.")
            puntuacion = 0
        elif maldicion_activa == 'C_IMPARES_CERO' and len(palabra_resultante) % 2 != 0:
            print(f"💀 Maldición: Palabras de longitud impar no puntúan.")
            puntuacion = 0
            
        elif puntuacion > 0: 
            puntuacion_modificada = 0
            
            # Recálculo de puntuación afectada por maldiciones
            if maldicion_activa in ['C_VOCALES_MEDIAS', 'C_NOPA']:
                for i, ficha in enumerate(fichas_usadas_str):
                    if i >= 7: break
                    letra_res = palabra_resultante[i]
                    valor_base = PUNTUACIONES_LETRAS.get(letra_res, 0)
                    multiplicador_pos = MULTIPLICADORES_POSICION.get(i, 1)

                    if maldicion_activa == 'C_VOCALES_MEDIAS' and letra_res in VOCALES: 
                        valor_base //= 2
                    elif maldicion_activa == 'C_NOPA' and letra_res == 'A':
                        valor_base = 0
                        
                    puntuacion_modificada += valor_base * multiplicador_pos
            else:
                 puntuacion_modificada = calcular_puntuacion(palabra_resultante, fichas_usadas_str) 

            # Reaplicamos el multiplicador de longitud
            if puntuacion_modificada > 0:
                 puntuacion_final_maldicion = puntuacion_modificada * obtener_multiplicador_longitud(len(palabra_resultante))
                 if puntuacion_final_maldicion < puntuacion_antes_maldicion:
                      print(f"💀 Maldición aplicada. Puntuación: {puntuacion_final_maldicion}")
                      puntuacion = puntuacion_final_maldicion
            else:
                 puntuacion = 0 

    # 4. LÓGICA U04: Multiplicador Vocal (MODIFICADO a 3 vocales)
    if puntuacion > 0 and 'U04' in mejoras_adquiridas:
        vocales_diferentes = set(letra for letra in palabra_resultante if letra in VOCALES)
        # Solo 3 vocales diferentes ahora
        if len(vocales_diferentes) >= 3: 
            puntuacion_original = puntuacion
            puntuacion *= 2
            print(f"⭐ U04: 3+ vocales distintas! Puntuación x2 ({puntuacion_original} -> {puntuacion})")

    # --- APLICAR BONO FIJO POR LONGITUD (ÚLTIMO PASO) ---
    if puntuacion > 0:
        longitud = len(palabra_resultante)
        bono = obtener_bono_longitud(longitud)
        
        if bono > 0:
            puntuacion_original = puntuacion
            puntuacion += bono
            print(f"💰 BONO FIJO por longitud ({longitud} letras): +{bono} puntos. ({puntuacion_original} -> {puntuacion})")
    
    # Mensaje final
    if puntuacion > 0:
        print(f"👍 Palabra válida. Puntuación final: {puntuacion} puntos.")
    else:
        puntuacion_sin_comodines = calcular_puntuacion(palabra_resultante, fichas_usadas_str) 
        msg = "por comodines/maldición" if puntuacion_sin_comodines > 0 else "(palabra base sin valor)"
        print(f"✅ Palabra válida, pero puntúa {puntuacion} {msg}.")

    return puntuacion, True

# =================================================================
# 3. FUNCIONES DE GESTIÓN DE LA BOLSA Y LA MANO Y UTILIDADES
# =================================================================

def inicializar_bolsa_completa(distribucion):
    """Crea la lista (bolsa) de todas las fichas."""
    bolsa = [letra for letra, cant in distribucion.items() for _ in range(cant)]
    print(f"🎲 Bolsa inicializada con {len(bolsa)} fichas.")
    return bolsa

def repartir_mano(bolsa_actual, tamano_mano):
    """Reparte letras de la bolsa."""
    if not bolsa_actual: return [], []
    num_a_repartir = min(len(bolsa_actual), tamano_mano)
    if num_a_repartir < tamano_mano:
          print(f"ADVERTENCIA: Solo quedan {num_a_repartir} fichas. Repartiendo esas.")

    mano = random.sample(bolsa_actual, num_a_repartir)
    temp_bolsa = bolsa_actual[:]
    for m in mano: temp_bolsa.remove(m)
    bolsa_restante = temp_bolsa

    return mano, bolsa_restante

def consumir_letras(mano_actual, fichas_usadas_str, palabra_resultante, maldicion_activa):
    """Verifica si las fichas están en la mano y calcula cuántas reponer."""
    temp_mano = mano_actual[:]
    
    for ficha in fichas_usadas_str:
        if ficha in temp_mano:
            temp_mano.remove(ficha)
        else:
            return False, mano_actual, 0

    letras_a_reponer = len(fichas_usadas_str)

    if maldicion_activa == 'C_DOBLE_RONDA':
        letras_extras_consumidas = 0
        letras_contadas = {}
        for letra in palabra_resultante:
            letras_contadas[letra] = letras_contadas.get(letra, 0) + 1

        for letra_representada, cuenta in letras_contadas.items():
            if cuenta > 1:
                fichas_extra_necesarias = cuenta - 1
                print(f"💀 Maldición C_DOBLE_RONDA: Letra '{letra_representada}' usada {cuenta} veces.")
                letras_extras_consumidas += fichas_extra_necesarias

        letras_a_reponer += letras_extras_consumidas
        if letras_extras_consumidas > 0:
             print(f"Total a reponer por C_DOBLE_RONDA: {letras_a_reponer} letras.")

    print(f"✅ Se consumieron {len(fichas_usadas_str)} fichas. Se repondrán {letras_a_reponer}.")
    return True, temp_mano, letras_a_reponer


def descartar_y_robar(mano_actual, bolsa_actual, letras_a_descartar):
    """Gestiona el descarte."""
    temp_mano = mano_actual[:]
    fichas_confirmadas_a_descartar = []

    comodines_a_descartar = letras_a_descartar.count('*')
    comodines_en_mano = temp_mano.count('*')
    
    descarte_valido = True
    if comodines_a_descartar > comodines_en_mano:
        print(f"🛑 ERROR: Intentas descartar {comodines_a_descartar} comodines (*), pero solo tienes {comodines_en_mano}.")
        descarte_valido = False
    else:
        for _ in range(comodines_a_descartar):
            temp_mano.remove('*')
            fichas_confirmadas_a_descartar.append('*')

    if descarte_valido:
        for letra_input in letras_a_descartar:
            if letra_input == '*': continue 

            letra_norm = normalizar_palabra(letra_input)
            if not letra_norm: continue

            if letra_norm in temp_mano:
                temp_mano.remove(letra_norm)
                fichas_confirmadas_a_descartar.append(letra_norm)
            else:
                 print(f"Advertencia: La ficha '{letra_norm}' no se encontró en la mano para descartar.")


    if not descarte_valido or not fichas_confirmadas_a_descartar:
        if descarte_valido:
             print("No se seleccionó ninguna ficha válida para descartar.")
        return mano_actual, bolsa_actual # Devolver estado original si falla

    cantidad_a_robar = len(fichas_confirmadas_a_descartar)
    print(f"\n🔄 Descartando {cantidad_a_robar} fichas ({fichas_confirmadas_a_descartar}). Robando {cantidad_a_robar} nuevas...")

    letras_robadas, bolsa_final = repartir_mano(bolsa_actual, cantidad_a_robar)
    nueva_mano = temp_mano + letras_robadas
    print(f"Nueva mano: {nueva_mano}")

    return nueva_mano, bolsa_final

def calcular_recompensa(puntuacion_obtenida, descartes_restantes, mejoras_adquiridas):
    """Calcula monedas (considera U06)."""
    monedas_puntos = max(0, puntuacion_obtenida) // 10 
    multiplicador_descarte = 2 if 'U06' in mejoras_adquiridas else 1
    if multiplicador_descarte == 2: print("⭐ U06: Descarte vale el doble.")
    monedas_descartes = descartes_restantes * multiplicador_descarte
    total_monedas = monedas_puntos + monedas_descartes

    print("\n--- RECOMPENSA DE NIVEL ---")
    print(f"Puntos {puntuacion_obtenida} = {monedas_puntos} monedas")
    print(f"Descartes x{multiplicador_descarte} ({descartes_restantes}) = {monedas_descartes} monedas")
    print(f"Monedas ganadas: {total_monedas}")
    return total_monedas

def aplicar_mejora(id_mejora, mejoras_adquiridas, PUNTUACIONES_LETRAS, NIVEL_LONGITUDES, MULTIPLICADORES_POSICION):
    """Aplica efectos de mejoras. Actualizada para U02 escalable y U14-U22."""
    global TAMANO_MANO_ACTUAL

    # --- LÓGICA U02 ESCALABLE (Mano Extendida) ---
    if id_mejora == 'U02':
        if TAMANO_MANO_ACTUAL < 10:
            TAMANO_MANO_ACTUAL += 1
            print(f">>> ✋ U02: Mano Extendida. Tamaño de mano ahora es {TAMANO_MANO_ACTUAL}.")
            
            # Estas se registran como adquiridas para control de compras múltiples
            if id_mejora not in mejoras_adquiridas:
                 mejoras_adquiridas.append(id_mejora)
                 
            # Cambiar nombre para reflejar el estado actual
            MEJORAS_DISPONIBLES[id_mejora]['nombre'] = f'Mano Extendida (T{TAMANO_MANO_ACTUAL})'
            return mejoras_adquiridas
        else:
             print(">>> 🛑 U02: Tamaño de mano ya está al máximo (10).")
             return mejoras_adquiridas


    # --- LÓGICA DE MEJORAS PERMANENTES NO APILABLES (U01, U03, U04, U06, U07) ---
    if id_mejora in ['U01', 'U03', 'U04', 'U06', 'U07'] and id_mejora not in mejoras_adquiridas:
        if id_mejora == 'U01':
            print(">>> ⏫ U01: Letras base valen 2.")
            for l in [l for l, v in PUNTUACIONES_LETRAS.items() if v == 1]: PUNTUACIONES_LETRAS[l] = 2
        elif id_mejora == 'U03': print(">>> 🎁 U03: Bolsa Reforzada.")
        elif id_mejora == 'U04': print(">>> ✨ U04: Multiplicador Vocal (3+).")
        elif id_mejora == 'U06': print(">>> 💰 U06: Economía de Descarte.")
        elif id_mejora == 'U07': print(">>> ⏱️ U07: Ronda de Bono.")
        
        mejoras_adquiridas.append(id_mejora)
        return mejoras_adquiridas
        
    elif id_mejora in ['U01', 'U03', 'U04', 'U06', 'U07']:
        print(f"\n❌ Ya tienes la mejora {id_mejora}.")
        return mejoras_adquiridas


    # --- LÓGICA DE MEJORAS POR NIVEL (U08 a U13) ---
    if id_mejora in ['U08', 'U09', 'U10', 'U11', 'U12', 'U13']:
        longitud_map = {'U08': 2, 'U09': 3, 'U10': 4, 'U11': 5, 'U12': 6, 'U13': 7}
        longitud = longitud_map[id_mejora]
        
        NIVEL_LONGITUDES[longitud] += 1
        nuevo_nivel = NIVEL_LONGITUDES[longitud]
        
        if id_mejora not in mejoras_adquiridas: mejoras_adquiridas.append(id_mejora)
             
        MEJORAS_DISPONIBLES[id_mejora]['nombre'] = f'Nivel L{longitud} (N{nuevo_nivel})'
             
        print(f">>> 📈 {id_mejora}: Palabras de {longitud} letras suben a Nivel {nuevo_nivel}.")
        return mejoras_adquiridas
        
    # --- LÓGICA DE MEJORAS POR POSICIÓN (U14 a U22) ---
    if id_mejora in ['U14', 'U15', 'U16', 'U17', 'U18', 'U19', 'U20', 'U21', 'U22']:
        if id_mejora in mejoras_adquiridas:
            print(f"\n❌ Ya tienes la mejora de posición {id_mejora}.")
            return mejoras_adquiridas

        multiplicadores_nuevos = {} 
        descripcion = ""

        if id_mejora == 'U14': multiplicadores_nuevos[0] = 2; descripcion = "x2 en posición 1"
        elif id_mejora == 'U15': multiplicadores_nuevos[1] = 2; descripcion = "x2 en posición 2"
        elif id_mejora == 'U16': multiplicadores_nuevos[2] = 2; descripcion = "x2 en posición 3"
        elif id_mejora == 'U17': multiplicadores_nuevos[3] = 2; descripcion = "x2 en posición 4"
        elif id_mejora == 'U18': multiplicadores_nuevos[4] = 3; descripcion = "x3 en posición 5"
        elif id_mejora == 'U19': multiplicadores_nuevos[5] = 5; descripcion = "x5 en posición 6"
        elif id_mejora == 'U20': multiplicadores_nuevos[6] = 6; descripcion = "x6 en posición 7"
        elif id_mejora == 'U21': multiplicadores_nuevos = {0: 2, 1: 2, 2: 2}; descripcion = "x2 en posiciones 1, 2, 3"
        elif id_mejora == 'U22': multiplicadores_nuevos = {3: 3, 4: 3, 5: 3, 6: 3}; descripcion = "x3 en posiciones 4, 5, 6, 7"

        print(f">>> 🎯 {id_mejora}: Aplicando {descripcion}.")
        
        for indice, nuevo_multi in multiplicadores_nuevos.items():
            MULTIPLICADORES_POSICION[indice] = nuevo_multi 
        
        mejoras_adquiridas.append(id_mejora)
        return mejoras_adquiridas
        
    # Si la mejora no se encontró
    print(f"❌ Error: Mejora {id_mejora} no reconocida o no disponible.")
    return mejoras_adquiridas


def bucle_tienda(monedas_actuales, mejoras_adquiridas, ofertas_actuales, PUNTUACIONES_LETRAS, NIVEL_LONGITUDES, MULTIPLICADORES_POSICION):
    """Bucle de la tienda, pasa el estado completo y usa el global TAMANO_MANO_ACTUAL."""
    monedas = monedas_actuales
    while True:
        print("\n=== 🏪 TIENDA ===")
        print(f"Monedas: {monedas}")
        
        # Mostrar el estado actual de los niveles
        print("\n--- NIVELES ACTUALES DE PUNTUACIÓN ---")
        for L, N in NIVEL_LONGITUDES.items():
            mult = obtener_multiplicador_longitud(L)
            bono = obtener_bono_longitud(L)
            print(f"L{L}{'+' if L==7 else ''}: Nivel {N} -> (x{mult}, +{bono})")
            
        # Mostrar el estado actual de la mano
        print(f"--- ESTADO DE LA MANO: {TAMANO_MANO_ACTUAL} Fichas (Máx 10) ---")
        
        print("------------------")
        
        if not ofertas_actuales: print("No hay ofertas.")
        else:
            for id_m in ofertas_actuales:
                if id_m in MEJORAS_DISPONIBLES:
                    data = MEJORAS_DISPONIBLES[id_m]
                    
                    estado = ""
                    # Marcar como (ADQUIRIDA) solo las permanentes no apilables (U01, U03, U04, U06, U07, U14-U22)
                    es_permanente_unica = id_m in ['U01', 'U03', 'U04', 'U06', 'U07'] or ('U14' <= id_m <= 'U22')
                    if id_m in mejoras_adquiridas and es_permanente_unica:
                         estado = " (ADQUIRIDA)"
                         
                    # Lógica especial para U02
                    if id_m == 'U02' and TAMANO_MANO_ACTUAL >= 10:
                        estado = " (MÁXIMO)"
                         
                    print(f"[{id_m}] {data['nombre']} ({data['costo']} M){estado}: {data['descripcion']}")
                else: print(f"[{id_m}] Oferta desconocida")
        
        print("\n[V] Volver")
        accion = input("Comprar ID o V: ").upper().strip()
        if accion == 'V': return monedas, ofertas_actuales
        
        if accion in ofertas_actuales and accion in MEJORAS_DISPONIBLES:
            data = MEJORAS_DISPONIBLES[accion]
            
            # Bloquear compra si es única y ya está
            es_permanente_unica = accion in ['U01', 'U03', 'U04', 'U06', 'U07'] or ('U14' <= accion <= 'U22')
            if accion in mejoras_adquiridas and es_permanente_unica: 
                print("\n❌ Ya tienes esta mejora única.")
            # Bloquear compra de U02 si está al máximo
            elif accion == 'U02' and TAMANO_MANO_ACTUAL >= 10:
                 print("\n❌ Mano Extendida ya está al máximo (10).")
            elif monedas < data['costo']: 
                print(f"\n❌ Monedas insuficientes ({data['costo']} M).")
            else:
                monedas -= data['costo']
                # PASAMOS ESTADO COMPLETO
                mejoras_adquiridas = aplicar_mejora(accion, mejoras_adquiridas, PUNTUACIONES_LETRAS, NIVEL_LONGITUDES, MULTIPLICADORES_POSICION)
                print(f"\n✅ ¡Comprada! Te quedan {monedas} M.")
        else: print("\nOpción no válida.")


def aplicar_maldicion(nivel_actual):
    """Selecciona maldición para niveles múltiplos de 3."""
    if nivel_actual > 0 and nivel_actual % 3 == 0:
        claves = list(MALDICIONES.keys())
        indice = (nivel_actual // 3 - 1) % len(claves)
        maldicion_clave = claves[indice]
        print(f"\n*** ⚠️ NIVEL MALDITO ({maldicion_clave}) ***")
        print(f"Efecto: {MALDICIONES[maldicion_clave]}")
        return maldicion_clave
    return None

def generar_ofertas_tienda(mejoras_adquiridas, num_ofertas=3):
    """Genera ofertas aleatorias. Excluye U05."""
    
    todas_mejoras = set(MEJORAS_DISPONIBLES.keys())
    
    # Excluir permanentes únicas ya adquiridas
    permanentes_unicas = [id_m for id_m in ['U01', 'U03', 'U04', 'U06', 'U07', 'U14', 'U15', 'U16', 'U17', 'U18', 'U19', 'U20', 'U21', 'U22']]
    permanentes_adquiridas = [id_m for id_m in permanentes_unicas if id_m in mejoras_adquiridas]
    
    pool_disponible = list(todas_mejoras - set(permanentes_adquiridas))
    
    # Lógica U02: Solo disponible si TAMANO_MANO_ACTUAL < 10
    if 'U02' in pool_disponible and TAMANO_MANO_ACTUAL >= 10:
        pool_disponible.remove('U02')

    num_a_mostrar = min(len(pool_disponible), num_ofertas)
    
    ofertas = random.sample(pool_disponible, num_a_mostrar) if num_a_mostrar > 0 else []
    print(f"Ofertas generadas: {ofertas}")
    return ofertas

def revolver_mano(mano_actual):
    """Revuelve el orden de las fichas en la mano para el jugador."""
    random.shuffle(mano_actual)
    print("Mano revuelta.")
    return mano_actual


# =================================================================
# 4. INICIO DEL JUEGO Y BUCLE INTERACTIVO (FINAL)
# =================================================================

RUTA_DICCIONARIO = 'diccionario.es.txt'
mi_diccionario = cargar_diccionario(RUTA_DICCIONARIO)

if mi_diccionario:
    # Reinicialización de variables globales
    PUNTUACIONES_LETRAS_ORIGINAL = {
        'A': 1, 'E': 1, 'O': 1, 'S': 1, 'I': 1, 'U': 1, 'N': 1, 'R': 1, 'T': 1, 'D': 2, 'G': 2, 'L': 2,
        'C': 3, 'M': 3, 'B': 3, 'P': 3, 'F': 4, 'H': 4, 'V': 4, 'Y': 4, 'Q': 5, 'J': 8, 'Ñ': 8, 'X': 8,
        'K': 10, 'Z': 10, 'W': 10, '*': 0
    }
    PUNTUACIONES_LETRAS = PUNTUACIONES_LETRAS_ORIGINAL.copy()
    NIVEL_LONGITUDES = {2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1}
    MULTIPLICADORES_POSICION = {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1}
    TAMANO_MANO_ACTUAL = 7
    # Reset del nombre de U02 en la tienda
    MEJORAS_DISPONIBLES['U02']['nombre'] = 'Mano Extendida' 
    
    
    bolsa_principal = inicializar_bolsa_completa(DISTRIBUCION_ESPANOL)
    bolsa_restante = bolsa_principal[:]

    monedas_totales = 0
    nivel_actual = 1
    mejoras_adquiridas = []

    jugar_niveles = True

    while jugar_niveles:

        if nivel_actual > 9:
            print("\n🏆 ¡FELICIDADES! Has superado los 3 Bloques.")
            print(f"Monedas finales: {monedas_totales}")
            jugar_niveles = False
            continue

        # --- CONFIGURACIÓN POR NIVEL ---
        PUNTOS_OBJETIVO = 15 if nivel_actual <= 3 else (50 * (nivel_actual - 3) + 15)

        RONDAS_BASE = 5
        DESCARTES_BASE = 3
        
        maldicion_activa = aplicar_maldicion(nivel_actual)
        ofertas_tienda_actual = []

        # Aplicar mejoras permanentes
        if 'U03' in mejoras_adquiridas: DESCARTES_BASE += 1
        if 'U07' in mejoras_adquiridas: RONDAS_BASE += 1; print(">>> ⏱️ U07: +1 Ronda Máx.")

        RONDAS_MAXIMAS = RONDAS_BASE
        puntuacion_actual = 0
        rondas_jugadas = 0
        descartes_restantes = DESCARTES_BASE

        # --- INICIO DEL NIVEL ---
        print("\n======================================")
        print(f"=== INICIO NIVEL {nivel_actual} (Bloque {(nivel_actual - 1) // 3 + 1}) ===")
        print(f"META: {PUNTOS_OBJETIVO} PUNTOS / {RONDAS_MAXIMAS} Rondas")
        print(f"Monedas: {monedas_totales} | Mejoras: {mejoras_adquiridas or 'Ninguna'}")
        print("======================================")
        print("--- ESTADO DE JUEGO ---")
        print(f"Tamaño de mano: {TAMANO_MANO_ACTUAL} fichas.")
        print("--- NIVELES DE PUNTUACIÓN INICIALES ---")
        for L, N in NIVEL_LONGITUDES.items():
            mult = obtener_multiplicador_longitud(L)
            bono = obtener_bono_longitud(L)
            print(f"L{L}{'+' if L==7 else ''}: Nivel {N} -> (x{mult}, +{bono})")
        print("---------------------------------------")

        mano_actual, bolsa_restante = repartir_mano(bolsa_restante, TAMANO_MANO_ACTUAL)

        # ----------------------------------------------------
        # BUCLE PRINCIPAL DEL NIVEL
        # ----------------------------------------------------
        jugar_rondas = True
        while jugar_rondas:

            if not mano_actual and not bolsa_restante:
                print("\n** ¡Sin fichas en mano ni bolsa! **")
                jugar_rondas = False
                if puntuacion_actual < PUNTOS_OBJETIVO:
                    jugar_niveles = False
                continue
                
            if puntuacion_actual >= PUNTOS_OBJETIVO:
                jugar_rondas = False
                continue
                
            if rondas_jugadas >= RONDAS_MAXIMAS:
                print(f"\n❌ DERROTA: Sin rondas. FIN DEL JUEGO.")
                jugar_rondas = False
                jugar_niveles = False
                continue

            # --- Display Ronda ---
            print(f"\n--- RONDA {rondas_jugadas + 1}/{RONDAS_MAXIMAS} ---")
            print(f"PUNTOS: {puntuacion_actual}/{PUNTOS_OBJETIVO} | DESCARTES: {descartes_restantes}/{DESCARTES_BASE}")
            
            mano_display = [f"*{l}*" if l == '*' else l for l in mano_actual]
            print(f"Mano ({len(mano_actual)}): {' '.join(mano_display)}")
            
            print("----------------------------")

            accion = input("Acción (P: Palabra, D: Descartar, R: Revolver, S: Salir): ").upper().strip()

            if accion == 'P':
                palabra_input = input("Palabra (usa *Letra* para comodín, ej: CA*S*A): ").strip()
                if not palabra_input: continue

                palabra_resultante, fichas_usadas_str = parsear_input_comodin(palabra_input)

                if palabra_resultante is None:
                     input("(Presiona Enter...)"); continue

                se_puede, mano_despues, letras_a_reponer = \
                    consumir_letras(mano_actual, fichas_usadas_str, palabra_resultante, maldicion_activa)

                if not se_puede:
                    print(f"🚫 Error: No tienes las fichas para '{fichas_usadas_str}'.")
                    input("(Presiona Enter...)"); continue

                puntuacion, es_valida = \
                    validar_y_puntuar(palabra_resultante, fichas_usadas_str, mi_diccionario, mejoras_adquiridas, maldicion_activa)

                if es_valida:
                    puntuacion_actual += puntuacion
                    rondas_jugadas += 1
                    mano_actual = mano_despues
                    # Repartir mano con el tamaño actual
                    fichas_robadas, bolsa_restante = repartir_mano(bolsa_restante, letras_a_reponer)
                    mano_actual.extend(fichas_robadas)
                else:
                    print("Intenta otra palabra.")

                input("(Presiona Enter...)")

            elif accion == 'D':
                if descartes_restantes <= 0: print("🛑 Sin descartes."); input("(Presiona Enter...)"); continue
                descartes_input = input("Fichas a descartar (separadas por coma, ej: a,*,e): ").strip()
                letras_a_descartar = [l.strip().upper() for l in descartes_input.split(',') if l.strip()]
                if not letras_a_descartar: print("No indicaste fichas."); input("(Presiona Enter...)"); continue

                mano_antes = mano_actual[:]
                mano_actual, bolsa_restante = descartar_y_robar(mano_actual, bolsa_restante, letras_a_descartar)
                if mano_actual != mano_antes: descartes_restantes -= 1
                else: print("Descarte no válido.")

                input("(Presiona Enter...)")

            elif accion == 'R':
                mano_actual = revolver_mano(mano_actual)
                input("(Presiona Enter...)")

            elif accion == 'S':
                jugar_rondas = False; jugar_niveles = False; print("Saliendo...")

            else: print("Opción no reconocida."); input("(Presiona Enter...)")


        # --- MENÚ DE TRANSICIÓN ---
        if jugar_niveles and puntuacion_actual >= PUNTOS_OBJETIVO:
            print(f"\n🎉 ¡VICTORIA NIVEL {nivel_actual}!")
            monedas_ganadas = calcular_recompensa(puntuacion_actual, descartes_restantes, mejoras_adquiridas)
            monedas_totales += monedas_ganadas
            nivel_actual += 1

            if not ofertas_tienda_actual:
                 ofertas_tienda_actual = generar_ofertas_tienda(mejoras_adquiridas, num_ofertas=3)

            while jugar_niveles: 
                print("\n==============================")
                print(f"=== TRANSICIÓN A NIVEL {nivel_actual} ===")
                print(f"Monedas: {monedas_totales}")
                print("------------------------------")
                opcion = input("(T: Tienda, S: Siguiente Nivel, F: Finalizar): ").upper().strip()

                if opcion == 'T':
                    monedas_totales, ofertas_tienda_actual = bucle_tienda(monedas_totales, mejoras_adquiridas, ofertas_tienda_actual, PUNTUACIONES_LETRAS, NIVEL_LONGITUDES, MULTIPLICADORES_POSICION)
                elif opcion == 'S':
                    print(f"\n🚀 Pasando al Nivel {nivel_actual}..."); break 
                elif opcion == 'F':
                    jugar_niveles = False; print("Saliendo...")
                else: print("Opción no válida.")

# --- FIN ---
elif not mi_diccionario:
    print("No se pudo iniciar el juego.")

if not jugar_niveles: print("\n--- FIN DE LA PARTIDA ---")