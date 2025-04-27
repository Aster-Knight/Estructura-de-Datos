# src/directory_scanner.py

import os
import stat
import datetime
from pathlib import Path
from typing import Callable # Para type hint de la función de creación de nodo

# Importar la clase FileSystemNode del mismo directorio src
from .filesystem_node import FileSystemNode

def scan_directory(
    start_path: Path,
    max_depth: int = -1, # -1 para escaneo completo, 0 para solo la raíz, 1 para raíz + hijos, etc.
    read_content: bool = False,
    content_preview_bytes: int = 1024,
    on_node_created: Callable[[FileSystemNode], None] = None # Función callback para asignar ID y indexar
) -> FileSystemNode | None:
    """
    Escanea un directorio de forma recursiva construyendo una estructura de FileSystemNode.

    Args:
        start_path (Path): La ruta inicial (como objeto pathlib.Path).
        max_depth (int, optional): La profundidad máxima para escanear (-1 = ilimitado, 0 = solo raíz).
                                   Defaults to -1.
        read_content (bool, optional): Si es True, intenta leer el contenido de los archivos.
                                       Defaults to False.
        content_preview_bytes (int, optional): Limita la lectura de contenido a este número de bytes.
                                             Defaults to 1024.
        on_node_created (Callable[[FileSystemNode], None], optional): Función a llamar
                                                                       cada vez que se crea un nodo.
                                                                       Útil para asignar ID y indexar.
                                                                       Defaults to None.

    Returns:
        FileSystemNode | None: El nodo raíz de la estructura escaneada, o None si la ruta no existe.
    """

    if not start_path.exists():
        # print(f"Error: La ruta no existe -> {start_path}") # Mover impresión de error a main.py
        return None

    try:
        # Obtener metadatos de la ruta inicial
        metadata = start_path.stat()
        is_directory_root = start_path.is_dir()
        root_name = start_path.name if start_path.name else str(start_path) # Usar .name de Path, manejar raíz

        # Crear el nodo raíz
        root_node = FileSystemNode(-1, root_name, str(start_path), is_directory_root, metadata) # ID temporal -1
        if on_node_created:
            on_node_created(root_node) # Asignar ID real y indexar

        # Función recursiva interna
        def _scan_recursive(current_path_obj: Path, parent_node: FileSystemNode, current_depth: int):
            # Detener la recursión si excede la profundidad máxima y no es la raíz (nivel 0)
            # o si el nodo padre no es un directorio.
            if not parent_node.is_directory or (max_depth >= 0 and current_depth > max_depth):
                return

            try:
                # Usar .iterdir() que devuelve objetos Path
                # sorted() ya maneja la ordenación por tipo y nombre
                for entry_obj in current_path_obj.iterdir():
                    try:
                        # Intentar obtener metadatos primero para verificar permisos y tipo
                        entry_metadata = entry_obj.stat()
                        is_directory = entry_obj.is_dir()
                        content = None

                        # Leer contenido solo si es un archivo, la lectura de contenido está activada,
                        # y no es un enlace simbólico que apunta a un directorio (para evitar bucles o errores)
                        if not is_directory and read_content and not entry_obj.is_symlink():
                            try:
                                with open(entry_obj, 'rb') as f:
                                    content_bytes = f.read(content_preview_bytes)
                                    try:
                                        content = content_bytes.decode('utf-8')
                                    except UnicodeDecodeError:
                                        content = f"<Binary content or encoding error, first {len(content_bytes)} bytes: {content_bytes}>"

                                    if entry_metadata.st_size > content_preview_bytes:
                                         if isinstance(content, str) and content.startswith('<Binary content') == False:
                                             content += "..."
                                         elif isinstance(content, str) and content.startswith('<Binary content'):
                                             content = content.rstrip('>') + f"... (total size: {entry_metadata.st_size} bytes)>"
                                         # Si es de otro tipo o error, no añadir nada extra o ya está manejado


                            except IOError as e:
                                content = f"<Error reading file: {e}>"
                            except Exception as e:
                                content = f"<Error processing file content: {e}>"

                        # Crear el nodo FileSystemNode (ID temporal -1)
                        child_node = FileSystemNode(-1, entry_obj.name, str(entry_obj), is_directory, entry_metadata, content=content)

                        # Agregar al padre y establecer la referencia de padre (ya manejado en add_child)
                        parent_node.add_child(child_node)

                        # Asignar ID real y indexar usando el callback
                        if on_node_created:
                             on_node_created(child_node)

                        # Llamada recursiva si es un directorio
                        if is_directory:
                            _scan_recursive(entry_obj, child_node, current_depth + 1)

                    except PermissionError:
                        # print(f"Permiso denegado para acceder a: {entry_obj}") # Desactivar impresión aquí
                        # Crear un nodo dummy para indicar la existencia, pero sin hijos/metadata completa
                        dummy_metadata = type('obj', (object,), {'st_size': 0, 'st_mode': 0, 'st_mtime': 0, 'st_ctime': 0})()
                        # ID temporal -1, se asignará real por el callback
                        child_node = FileSystemNode(-1, entry_obj.name, str(entry_obj), entry_obj.is_dir(), dummy_metadata, content="<Permission Denied>")
                        parent_node.add_child(child_node)
                        if on_node_created:
                             on_node_created(child_node) # Asignar ID real y indexar
                    except Exception as e:
                         # print(f"Error al procesar {entry_obj}: {e}") # Desactivar impresión aquí
                         # Crear un nodo dummy
                         dummy_metadata = type('obj', (object,), {'st_size': 0, 'st_mode': 0, 'st_mtime': 0, 'st_ctime': 0})()
                         # ID temporal -1, se asignará real por el callback
                         child_node = FileSystemNode(-1, entry_obj.name, str(entry_obj), entry_obj.is_dir(), dummy_metadata, content=f"<Processing Error: {e}>")
                         parent_node.add_child(child_node)
                         if on_node_created:
                              on_node_created(child_node) # Asignar ID real y indexar


            except PermissionError:
                # print(f"Permiso denegado para listar directorio: {current_path_obj}") # Desactivar impresión aquí
                 pass # Si no se puede listar, el nodo padre ya fue creado, no añadimos hijos.
            except Exception as e:
                 # print(f"Error al escanear {current_path_obj}: {e}") # Desactivar impresión aquí
                 pass # Si hay error listando, el nodo padre existe pero no añadimos hijos.


        # Iniciar el escaneo recursivo si es un directorio
        if root_node.is_directory and (max_depth != 0): # Si max_depth es 0, solo creamos la raíz, no escaneamos hijos
             _scan_recursive(start_path, root_node, 1) # Los hijos de la raíz están en el nivel 1

        return root_node

    except PermissionError:
        # print(f"Permiso denegado para acceder a la ruta inicial: {start_path}") # Mover impresión de error a main.py
        return None
    except Exception as e:
         # print(f"Error inicial al procesar {start_path}: {e}") # Mover impresión de error a main.py
         return None