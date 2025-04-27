
# Herramienta Interactiva de Gestión de Estructuras de Directorios (Directory Tree JScan/SScan)


> Herramienta de línea de comandos interactiva para **escanear, construir y gestionar representaciones en memoria de estructuras de directorios como árboles (Directory Trees)**.

---

## Descripción

Este proyecto es una utilidad de consola desarrollada en Python para interactuar con el sistema de archivos. Su función principal es **escanear directorios recursivamente y modelar su estructura como un árbol (Directory Tree) en la memoria**. En este árbol, cada nodo representa un archivo o una carpeta del sistema de archivos, manteniendo sus nombres, rutas, metadatos y (opcionalmente) una previsualización de su contenido.

Una vez que la estructura del directorio ha sido escaneada y construida como un árbol, la herramienta te permite interactuar con esta representación en memoria utilizando una serie de comandos para explorarla, buscar nodos, visualizar el árbol en la consola o exportarlo a un archivo.

---

## Características Principales

*   **Construcción del Árbol de Directorios:** Escanea el sistema de archivos para crear una representación en memoria fiel a la estructura de carpetas y archivos, incluyendo metadatos clave y contenido (opcional) en cada nodo del árbol.
*   **Escaneo Flexible (`j-scan`):** Permite construir el árbol con control sobre la profundidad máxima de escaneo y la opción de leer (o previsualizar) el contenido de los archivos para los nodos del árbol.
*   **Escaneo Simple (`s-scan`):** Construye un árbol completo de un directorio de forma rápida (profundidad ilimitada), sin leer contenido por defecto.
*   **Indexación de Nodos:** Asigna un ID único a cada nodo en el árbol escaneado para facilitar el acceso directo a elementos específicos.
*   **Impresión Visual del Árbol:** Muestra la **estructura arbórea** en la consola con indentación y símbolos, controlando la profundidad de visualización y si se muestran los metadatos de los nodos.
*   **Guardar la Representación del Árbol:** Exporta la **estructura del árbol visualizada** a un archivo de texto o Markdown.
*   **Búsqueda y Filtrado en el Árbol:** Permite encontrar nodos específicos dentro del árbol escaneado basándose en varios criterios como nombre (con wildcards), tipo, tamaño, nivel y contenido (si fue leído).
*   **Ver Detalles de Nodos:** Muestra información detallada sobre un nodo específico del árbol por su ID, incluyendo todos sus metadatos y previsualización de contenido.

---

## Uso

Ejecuta el script principal desde la terminal:

```bash
python main.py
```

Esto iniciará la interfaz de línea de comandos interactiva. Verás el prompt `>`. Escribe `help` para ver la lista de comandos disponibles.

### Comandos Disponibles

*   **`help [comando]`**: Muestra la ayuda general o específica para un comando.
    *   Ejemplo: `help scan`
    *   Ejemplo: `help search`

*   **`j-scan <ruta> [--depth <nivel>] [--read-content] [--preview-bytes <bytes>]`**: **Construye el árbol** escaneando un directorio con opciones configurables.
    *   `<ruta>`: La ruta del directorio a escanear. **Encierra rutas con espacios entre comillas dobles (`"`)**.
    *   `--depth <nivel>`: Nivel de profundidad máxima a escanear. `-1` para ilimitado (por defecto), `0` para solo la raíz, `1` para raíz + hijos directos, etc.
    *   `--read-content`: Si se incluye, intenta leer una parte del contenido de los archivos para los nodos del árbol.
    *   `--preview-bytes <bytes>`: Si `--read-content` está activo, limita la lectura a este número de bytes (por defecto 1024).
    *   Ejemplo: `j-scan "C:\Users\Mi Carpeta" --depth 3 --read-content`
    *   Ejemplo: `j-scan /home/user/docs --read-content --preview-bytes 512`

*   **`s-scan <ruta>`**: **Construye un árbol completo** de un directorio (profundidad ilimitada) de forma rápida, sin leer contenido por defecto.
    *   `<ruta>`: La ruta del directorio a escanear. **Encierra rutas con espacios entre comillas dobles (`"`)**.
    *   Ejemplo: `s-scan "D:\Archivos del Proyecto"`
    *   Ejemplo: `s-scan ./mis_fotos`

*   **`print [--depth <nivel>] [--show-metadata] [--hide-metadata]`**: Imprime la **estructura del árbol escaneado** en la consola.
    *   `--depth <nivel>`: Profundidad máxima de impresión. `-1` para ilimitado (por defecto). `0` para solo la raíz, etc.
    *   `--show-metadata`: Muestra tamaño y fecha de modificación (por defecto).
    *   `--hide-metadata`: Oculta tamaño y fecha de modificación.
    *   Ejemplo: `print --depth 2`
    *   Ejemplo: `print --hide-metadata`

*   **`search <criterio1=valor1> [<criterio2=valor2> ...]`**: Busca nodos **en el árbol escaneado** que coincidan con *todos* los criterios especificados.
    *   Criterios soportados (las claves son *case-insensitive*):
        *   `name=<patron>`: Busca por nombre. Soporta wildcards simples `*` (cero o más caracteres) y `?` (exactamente un carácter). También acepta patrones de expresión regular si no usas wildcards.
        *   `type=file` | `type=dir`: Busca solo archivos o solo directorios.
        *   `min_size=<valor>` | `<valor>KB` | `<valor>MB` | `<valor>GB`: Tamaño mínimo (solo para archivos).
        *   `max_size=<valor>` | `<valor>KB` | `<valor>MB` | `<valor>GB`: Tamaño máximo (solo para archivos).
        *   `level=<nivel>`: Busca nodos en un nivel de profundidad exacto **dentro del árbol**.
        *   `content=<texto>`: Busca archivos **en el árbol** cuyo contenido (si fue leído con `--read-content`) contenga el texto especificado (búsqueda *case-insensitive*).
    *   Ejemplo: `search type=file name=*.log min_size=100KB max_size=5MB level=2`
    *   Ejemplo: `search type=dir name=*backup*`
    *   Ejemplo: `search content="error fatal"`

*   **`open <node_id>`**: Muestra detalles completos y previsualización de contenido (si fue leído) para un nodo específico **del árbol** utilizando su ID numérico. Puedes encontrar los IDs en la salida del comando `print` o `search`.
    *   Ejemplo: `open 42`

*   **`save <filename> [--depth <nivel>] [--show-metadata] [--hide-metadata]`**: Guarda la **representación visual del árbol** en un archivo. Si el archivo ya existe, se sobrescribe.
    *   `<filename>`: Nombre del archivo de salida (ej: `mi_arbol.txt`, `documentacion_md.md`).
    *   Las opciones `--depth`, `--show-metadata`, `--hide-metadata` funcionan igual que en el comando `print` y controlan **la profundidad de la representación guardada**.
    *   Ejemplo: `save tree_structure.txt --depth 5`

*   **`exit`**: Sale de la aplicación.

---

## Cómo Extender o Contribuir

La modularidad del proyecto, centrada en la gestión del `DirectoryTree`, facilita la adición de nuevas funcionalidades:

1.  **Añadir un Nuevo Comando de Consola:**
    *   Modifica `main.py`.
    *   Define un nuevo `argparse.ArgumentParser` para tu comando.
    *   Añade tu comando y su parser al diccionario `command_parsers`.
    *   Añade un nuevo `elif command == 'tu_comando':` en el bucle principal para manejarlo.
    *   Dentro de este bloque, usa `tu_comando_parser.parse_args(args, ...)` para obtener los argumentos del usuario.
    *   Implementa la lógica de tu comando, probablemente llamando a métodos que interactúan con la instancia `directory_tree` (el árbol gestionado).
    *   Actualiza la ayuda en el comando `help`.

2.  **Añadir Nueva Funcionalidad al Árbol (ej: Nuevo criterio de búsqueda, exportar a otro formato):**
    *   La lógica principal para interactuar **con la estructura del árbol** reside en la clase `DirectoryTree` (`src/directory_tree.py`).
    *   Añade un nuevo método a la clase `DirectoryTree` para encapsular la nueva funcionalidad (ej: `export_tree_to_json(self, filename)`).
    *   Si la nueva funcionalidad requiere acceder a datos adicionales de los nodos, podría ser necesario modificar `FileSystemNode` (`src/filesystem_node.py`) y/o la lógica de escaneo en `scan_directory` (`src/directory_scanner.py`) para que **la construcción del árbol capture esos datos**.
    *   Si la nueva funcionalidad es una nueva forma de imprimir o visualizar el árbol, podría añadirse lógica en `tree_printer.py`.
    *   Una vez implementada la lógica subyacente que opera **sobre el árbol**, añádela como un nuevo comando en `main.py` (como se describe en el punto 1) para exponerla a través de la consola.

3.  **Mejoras en la Construcción o Visualización del Árbol:**
    *   Las funciones `scan_directory` (`src/directory_scanner.py`) son responsables de la **construcción inicial del árbol**. Las mejoras en la eficiencia del escaneo, manejo de permisos o la captura de metadatos irían aquí.
    *   `build_tree_string` (`src/tree_printer.py`) es responsable de la **representación visual del árbol**. Las mejoras en el formato de impresión irían aquí.

---
