#Primera Construcción, sin implementaciones. 

# Bloque 1: Importar librerías y definir la clase FileSystemNode

import os
import sys
import stat # Para obtener más detalles de metadata
import datetime # Para formatear las fechas de metadata

class FileSystemNode:
    """
    Representa un archivo o carpeta en el sistema de archivos.
    """
    def __init__(self, name: str, path: str, is_directory: bool, metadata: os.stat_result, content=None):
        """
        Inicializa un nodo del sistema de archivos.

        Args:
            name (str): El nombre del archivo o carpeta.
            path (str): La ruta completa del archivo o carpeta.
            is_directory (bool): True si es una carpeta, False si es un archivo.
            metadata (os.stat_result): Objeto stat con metadatos del archivo/carpeta.
            content (bytes, optional): Contenido del archivo (solo para archivos). Defaults to None.
        """
        self.name = name
        self.path = path
        self.is_directory = is_directory
        self.metadata = metadata
        self.content = content  # Almacena el contenido (puede ser grande)
        self.children = [] # Lista de FileSystemNode para directorios

    def add_child(self, child_node: 'FileSystemNode'):
        """Agrega un nodo hijo a este nodo (si es un directorio)."""
        if self.is_directory:
            self.children.append(child_node)
        else:
            print(f"Advertencia: Intentando añadir hijo a un archivo: {self.name}")

    def get_children(self):
        """Retorna la lista de nodos hijos (vacía si es un archivo)."""
        return self.children

    def __repr__(self):
        """Representación amigable del nodo."""
        type_str = "Dir" if self.is_directory else "File"
        return f"{type_str}: {self.name}"

# La clase Tree original no es necesaria con esta estructura,
# la raíz del árbol será simplemente un objeto FileSystemNode.

# Bloque 2: Función para escanear el sistema de archivos (Recursiva)

def scan_directory_tree(path: str, read_content=False, content_preview_bytes=1024) -> FileSystemNode | None:
    """
    Escanea recursivamente un directorio y construye la estructura FileSystemNode.

    Args:
        path (str): La ruta del directorio a escanear.
        read_content (bool, optional): Si es True, intenta leer el contenido de los archivos.
                                       Por defecto es False para evitar leer archivos grandes.
        content_preview_bytes (int, optional): Si read_content es True, limita la lectura
                                             a este número de bytes para archivos grandes.

    Returns:
        FileSystemNode | None: El nodo raíz de la estructura escaneada, o None si la ruta no existe o no es un directorio.
    """
    if not os.path.exists(path):
        print(f"Error: La ruta no existe -> {path}")
        return None
    if not os.path.isdir(path):
        print(f"Error: La ruta no es un directorio -> {path}")
        return None

    try:
        # Obtener metadatos de la carpeta raíz
        metadata = os.stat(path)
        root_name = os.path.basename(path) if os.path.basename(path) else path # Manejar caso raíz como '.' o '/'
        root_node = FileSystemNode(root_name, path, True, metadata)

        # Función recursiva para escanear subdirectorios
        def _scan(current_path: str, parent_node: FileSystemNode):
            try:
                with os.scandir(current_path) as entries:
                    for entry in sorted(entries, key=lambda e: (not e.is_dir(), e.name)): # Ordenar dirs primero, luego por nombre
                        entry_path = os.path.join(current_path, entry.name)
                        try:
                            entry_metadata = entry.stat()
                            is_directory = entry.is_dir()
                            content = None

                            if not is_directory and read_content:
                                try:
                                    # Leer contenido del archivo (con límite)
                                    with open(entry_path, 'rb') as f: # Usar modo binario para evitar problemas de codificación iniciales
                                        content_bytes = f.read(content_preview_bytes)
                                        # Intentar decodificar si parece texto, si no, guardar bytes o marcar como binario
                                        try:
                                            content = content_bytes.decode('utf-8') # Intentar UTF-8 por defecto
                                        except UnicodeDecodeError:
                                            content = f"<Binary content or encoding error, first {len(content_bytes)} bytes: {content_bytes}>"
                                        if entry_metadata.st_size > content_preview_bytes:
                                             if isinstance(content, str): # Add ellipsis if content was successfully decoded
                                                 content += "..."
                                             else: # Append info if content is binary/error string
                                                 content = content.rstrip('>') + f"... (total size: {entry_metadata.st_size} bytes)>"


                                except IOError as e:
                                    content = f"<Error reading file: {e}>"

                            child_node = FileSystemNode(entry.name, entry_path, is_directory, entry_metadata, content=content)
                            parent_node.add_child(child_node)

                            if is_directory:
                                _scan(entry_path, child_node) # Llamada recursiva

                        except PermissionError:
                            print(f"Permiso denegado para acceder a: {entry_path}")
                            # Crear un nodo dummy para indicar la existencia, pero sin hijos/metadata completa
                            dummy_metadata = type('obj', (object,), {'st_size': 0, 'st_mode': 0, 'st_mtime': 0, 'st_ctime': 0})() # Simple dummy
                            parent_node.add_child(FileSystemNode(entry.name, entry_path, is_directory, dummy_metadata, content="<Permission Denied>"))
                        except Exception as e:
                             print(f"Error al procesar {entry_path}: {e}")
                             # Crear un nodo dummy para indicar el error
                             dummy_metadata = type('obj', (object,), {'st_size': 0, 'st_mode': 0, 'st_mtime': 0, 'st_ctime': 0})() # Simple dummy
                             parent_node.add_child(FileSystemNode(entry.name, entry_path, is_directory, dummy_metadata, content=f"<Processing Error: {e}>"))


            except PermissionError:
                print(f"Permiso denegado para listar directorio: {current_path}")
            except Exception as e:
                 print(f"Error al escanear {current_path}: {e}")


        _scan(path, root_node) # Iniciar el escaneo recursivo
        return root_node

    except PermissionError:
        print(f"Permiso denegado para acceder a la ruta inicial: {path}")
        return None
    except Exception as e:
         print(f"Error inicial al procesar {path}: {e}")
         return None
    
# Bloque 3: Función para construir la cadena de impresión del árbol de directorios

def build_directory_tree_string(node: FileSystemNode, indent: str = "", is_last: bool = True, show_metadata: bool = True) -> list[str]:
    """
    Construye una lista de cadenas representando visualmente la estructura del árbol
    de directorios de forma recursiva.

    Args:
        node (FileSystemNode): El nodo actual a procesar.
        indent (str, optional): La cadena de indentación acumulada. Defaults to "".
        is_last (bool, optional): Indica si este nodo es el último hijo de su padre. Defaults to True.
        show_metadata (bool, optional): Si es True, muestra metadatos básicos (tamaño y fecha). Defaults to True.

    Returns:
        list[str]: Una lista de cadenas, donde cada cadena es una línea de la salida visual.
    """
    lines = []

    # Símbolos para dibujar el árbol
    if indent == "": # El nodo raíz no tiene prefijo de rama
        branch_prefix = ""
    else:
        branch_prefix = '└── ' if is_last else '├── '

    print_str = f"{indent}{branch_prefix}{node.name}"

    if show_metadata:
        # Formatear metadatos básicos
        size_kb = node.metadata.st_size / 1024
        # Convertir timestamp a fecha legible
        try:
             mod_time = datetime.datetime.fromtimestamp(node.metadata.st_mtime).strftime('%Y-%m-%d %H:%M')
        except Exception: # Handle potential errors with invalid timestamps
             mod_time = "Fecha desconocida"

        meta_info = f" ({'Dir' if node.is_directory else f'{size_kb:.2f} KB'}, Mod: {mod_time})"
        print_str += meta_info

    lines.append(print_str)

    # Prefijo de indentación para los hijos
    child_indent_prefix = indent + ('    ' if indent != "" and is_last else '│   ') # Ajustar indentación para hijos del nodo raíz

    # Construir cadenas para los hijos
    # Se ordena la lista de hijos antes de procesar para una salida consistente
    # Ordenar: directorios primero, luego archivos, ambos por nombre
    sorted_children = sorted(node.get_children(), key=lambda child: (not child.is_directory, child.name))

    for i, child in enumerate(sorted_children):
        child_is_last = (i == len(sorted_children) - 1)
        # Llamada recursiva y añadir las líneas de los hijos a la lista actual
        child_lines = build_directory_tree_string(child, child_indent_prefix, child_is_last, show_metadata)
        lines.extend(child_lines) # Usa extend para añadir todas las líneas de los hijos

    return lines

# Bloque 4: Script principal para recibir input, escanear y guardar en archivo

if __name__ == "__main__":
    # 1. Preguntar por la dirección en consola
    start_path = input("Por favor, introduce la ruta del directorio a escanear: ")

    # Eliminar comillas si el usuario las puso (común para rutas con espacios en algunas consolas)
    start_path = start_path.strip().strip('"\'')

    # --- INICIO MODIFICACIÓN (Sin cambios aquí, solo la llamada a la función) ---
    # Generar el nombre del archivo de salida basado en el nombre de la carpeta
    # Extraer el nombre de la carpeta de la ruta proporcionada
    directory_name = os.path.basename(start_path)

    # Manejar el caso de que la ruta sea la raíz o termine en slash, donde basename podría ser vacío
    if not directory_name:
        # Si basename está vacío, intenta obtener el nombre del directorio padre
        parent_dir = os.path.dirname(start_path)
        directory_name = os.path.basename(parent_dir)
        # Si aún está vacío (ej: '/' o 'C:\'), usar un nombre por defecto o la letra de la unidad
        if not directory_name:
             # En Windows, podría ser solo la letra de la unidad
             drive, path_part = os.path.splitdrive(start_path)
             if drive:
                  directory_name = drive.replace(':', '') # Usar la letra de la unidad sin ':'
             else:
                  directory_name = "root" # Nombre por defecto para la raíz (Unix/Linux)


    # Construir el nombre final del archivo
    output_filename = f"{directory_name}_directory_tree.txt"
    # --- FIN MODIFICACIÓN ---


    # Opciones (pueden ajustarse aquí)
    # CUIDADO con read_content=True en directorios grandes, puede consumir mucha memoria
    read_file_content = False # Si es True, intenta leer una parte del contenido de los archivos
    show_file_metadata = True # Si es True, muestra tamaño y fecha de modificación en la impresión
    content_preview_size = 256 # Bytes para previsualización del contenido si read_content es True


    print(f"Escaneando directorio: {start_path}")

    # 2. Escanear y 3. Representar usando la estructura (FileSystemNode)
    # --- INICIO CORRECCIÓN ---
    # Corregir el nombre del parámetro de 'content_preview_size' a 'content_preview_bytes'
    root_directory_node = scan_directory_tree(start_path, read_content=read_file_content, content_preview_bytes=content_preview_size)
    # --- FIN CORRECCIÓN ---

    if root_directory_node:
        print("\n--- Generando estructura del árbol ---")
        # Construir la representación en cadena del árbol
        # Asegurar que el nombre de la raíz mostrado en el archivo sea el nombre del directorio principal
        # aunque el objeto root_directory_node ya lo tiene.
        tree_string_lines = build_directory_tree_string(root_directory_node, show_metadata=show_file_metadata)

        # 4. Guardar la impresión en un documento
        try:
            print(f"Guardando estructura del árbol en '{output_filename}'...")
            with open(output_filename, 'w', encoding='utf-8') as f: # Usar UTF-8 por si hay nombres con caracteres especiales
                f.write('\n'.join(tree_string_lines))
            print(f"--- Estructura del árbol guardada exitosamente ---")

            # Opcional: Imprimir también en consola la estructura generada
            # print("\n--- Estructura del árbol (consola) ---")
            # for line in tree_string_lines:
            #      print(line)

        except IOError as e:
            print(f"\nError al guardar el archivo '{output_filename}': {e}")
        except Exception as e:
            print(f"\nOcurrió un error inesperado al guardar o imprimir: {e}")


        # Puedes acceder a los datos del árbol (name, path, metadata, content, children)
        # a través del objeto root_directory_node aquí.
        # Por ejemplo:
        # print(f"\nDatos del nodo raíz:")
        # print(f"  Nombre: {root_directory_node.name}")
        # print(f"  Ruta: {root_directory_node.path}")
        # print(f"  ¿Es directorio?: {root_directory_node.is_directory}")
        # print(f"  Tamaño (bytes): {root_directory_node.metadata.st_size}")
        # # Para acceder a hijos: root_directory_node.get_children()

    else:
        print("No se pudo escanear el directorio.")