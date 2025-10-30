Godot 4 scaffold para LetterlikeSP

Archivos añadidos:
- `project.godot` — configuración mínima del proyecto (autocarga GameManager).
- `scripts/GameManager.gd` — gestor del estado del juego (portado parcialmente desde `LLSP.py`).
- `scripts/HUD.gd` — script para la UI básica de ejemplo.
- `scenes/Main.tscn` y `scenes/HUD.tscn` — escenas mínimas; la HUD incluye un botón "Iniciar / Reset" y una etiqueta con la mano.

Próximos pasos para usar el scaffold:
1. Instala Godot 4.x (recomendado 4.2+).
2. Copia tu `diccionario.es.txt` en `godot/data/diccionario.es.txt` (crea la carpeta `data/` si no existe).

   Opciones para subir el diccionario al repo:
   - En tu máquina con Git:
     ```bash
     # copia el archivo al repo
     cp /ruta/a/tu/diccionario.es.txt /workspaces/LetterlikeSP/godot/data/diccionario.es.txt
     git add godot/data/diccionario.es.txt
     git commit -m "Añadir diccionario para Godot"
     git push
     ```
   - En VS Code: arrastra el archivo al panel del explorador dentro de `godot/data/`.
   - En GitHub web: abre el repo y usa "Add file" → "Upload files" y súbelo a `godot/data/`.

3. Abre Godot y abre la carpeta `godot/` como proyecto. El `GameManager.gd` está configurado como AutoLoad en `project.godot`.
4. Desde el editor: ejecuta la escena `res://scenes/Main.tscn`. Presiona "Iniciar / Reset" para inicializar la bolsa y repartir la mano.

Notas y limitaciones del scaffold actual:
5. Interacción táctil disponible en el scaffold:
  - Toca fichas en la mano para añadirlas a la zona "Colocar palabra".
  - Si tocas un comodín `*`, se abrirá un diálogo para elegir la letra que representa.
  - En la zona de selección puedes tocar una ficha seleccionada para quitarla.
  - Usa "Guardar" y "Cargar" para persistir el estado (se crea `user://savegame.json` en ejecución).
   - También soporta drag & drop: arrastra una ficha desde la mano hacia la zona "Colocar palabra".
   - Entrada manual: en el panel "Colocar palabra" puedes escribir una palabra en la caja de texto y confirmar (útil si prefieres teclear en lugar de arrastrar fichas).

Notas y limitaciones del scaffold actual:
- Se ha completado la portación de muchas reglas: maldiciones básicas (C_NOPUNTO_4LETRAS,C_VOCALES_MEDIAS,C_NOPA), C_DOBLE_RONDA en consumo de fichas, mejoras U01,U02,U03,U04,U06,U07 y U08-U13 (aumentan niveles) y U14-U22 (multiplicadores por posición). Algunas reglas extremas y balance fino pueden necesitar ajustes.
- La UI táctil es funcional (selección por toque, diálogo para comodín, tienda básica, guardado), pero todavía requiere pulido visual (tamaños, estilos y drag & drop avanzado). Si quieres, en la siguiente iteración hago el rediseño visual completo y pruebas en móvil.

Si quieres que continúe portando más funciones y construya la UI táctil completa (drag & drop, teclado, shop, guardado), dime y lo hago en la siguiente iteración. También puedo crear un PR con estos cambios para revisión.
