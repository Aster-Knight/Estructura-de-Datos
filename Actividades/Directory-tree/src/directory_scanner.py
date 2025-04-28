# src/directory_scanner.py

import os
import stat
import datetime
from pathlib import Path
from typing import Callable

# Importar la clase FileSystemNode del mismo directorio src
from .filesystem_node import FileSystemNode

def scan_directory(
    start_path: Path,
    max_depth: int = -1,
    read_content: bool = False, # True si se debe leer *algún* contenido (preview o full)
    read_full_content: bool = False, # True si se debe leer el contenido COMPLETO
    save_full_content_to_disk_path: Path | None = None, # <-- NUEVO PARAMETRO: Si no es None, guardar contenido COMPLETO aquí
    content_preview_bytes: int = 1024,
    on_node_created: Callable[[FileSystemNode], None] = None
) -> FileSystemNode | None:
    """
    Escanea un directorio de forma recursiva construyendo una estructura de FileSystemNode.
    Permite leer contenido (previsualización o completo) y guardar contenido completo en disco.
    """

    if not start_path.exists():
        return None

    try:
        metadata = start_path.stat()
        is_directory_root = start_path.is_dir()
        root_name = start_path.name if start_path.name else str(start_path)

        # ID temporal -1, se asignará real por el callback
        root_node = FileSystemNode(-1, root_name, str(start_path), is_directory_root, metadata)
        if on_node_created:
            on_node_created(root_node) # Asignar ID real y indexar

        def _scan_recursive(current_path_obj: Path, parent_node: FileSystemNode, current_depth: int):
            if not parent_node.is_directory or (max_depth >= 0 and current_depth > max_depth):
                return

            try:
                for entry_obj in current_path_obj.iterdir():
                    try:
                        entry_metadata = entry_obj.stat()
                        is_directory = entry_obj.is_dir()
                        content = None
                        saved_content_path = None # Inicializar el nuevo atributo

                        # Leer contenido solo si es un archivo, la lectura está activada,
                        # y no es un enlace simbólico a directorio.
                        if not is_directory and read_content and not entry_obj.is_symlink():
                            try:
                                with open(entry_obj, 'rb') as f:
                                    content_bytes = b"" # Inicializar antes del read

                                    if read_full_content:
                                        # Leer el archivo completo
                                        content_bytes = f.read()

                                        # --- LOGICA DE GUARDADO EN DISCO ---
                                        if save_full_content_to_disk_path:
                                            # Generar nombre de archivo único para la copia
                                            # Usamos un nombre simple basado en ID (que se asignará luego)
                                            # La ruta completa se construirá después de crear el nodo
                                            saved_file_name = f"temp_node_content_{id(entry_obj)}_{entry_metadata.st_size}.dat" # Nombre temporal
                                            saved_file_path_obj = save_full_content_to_disk_path / saved_file_name # Ruta completa temporal

                                            try:
                                                with open(saved_file_path_obj, 'wb') as out_f:
                                                    out_f.write(content_bytes)
                                                # Almacenar la ruta donde se guardó
                                                saved_content_path = str(saved_file_path_obj)
                                                # El atributo content en el nodo tendrá un marcador
                                                content = f"<Content saved to disk at {saved_file_path_obj.name}>" # Indicar dónde se guardó
                                                # Limpiar content_bytes de la memoria si ya se guardó en disco
                                                content_bytes = b"" # Liberar memoria lo antes posible

                                            except IOError as e:
                                                content = f"<Error saving content to disk: {e}>"
                                                saved_content_path = None
                                            except Exception as e: # Otros errores al guardar
                                                content = f"<Unexpected error saving content to disk: {e}>"
                                                saved_content_path = None

                                        else:
                                            # Si no se guarda en disco, almacenar el contenido completo en memoria (peligroso)
                                            try:
                                                content = content_bytes.decode('utf-8', errors='replace') # Decodificar contenido completo en memoria
                                            except Exception: # Falló decodificación, marcar como binario
                                                 content = f"<Binary content or decoding error, {len(content_bytes)} bytes read>"
                                            saved_content_path = None # Asegurarse de que sea None


                                    else: # read_full_content es False, solo previsualización
                                        content_bytes = f.read(content_preview_bytes)
                                        try:
                                            content = content_bytes.decode('utf-8', errors='replace')
                                        except Exception:
                                             content = f"<Binary content or decoding error, first {len(content_bytes)} bytes read>"

                                        # Añadir puntos suspensivos si es solo una previsualización y el archivo es más grande
                                        if entry_metadata.st_size > content_preview_bytes:
                                            if isinstance(content, str) and not content.startswith('<'):
                                                content += "..."
                                        saved_content_path = None # Asegurarse de que sea None


                            except IOError as e:
                                content = f"<Error reading file: {e}>"
                                saved_content_path = None
                            except Exception as e: # Capturar otros posibles errores de lectura
                                 content = f"<Error processing file content: {e}>"
                                 saved_content_path = None

                        # Crear el nodo FileSystemNode
                        child_node = FileSystemNode(
                            -1, # ID temporal
                            entry_obj.name,
                            str(entry_obj),
                            is_directory,
                            entry_metadata,
                            content=content # content ahora puede ser preview, marcador de guardado, o marcador de error/binario
                        )
                        child_node.saved_content_path = saved_content_path # <-- Asignar la ruta de guardado


                        # Agregar al padre y establecer la referencia de padre
                        parent_node.add_child(child_node)

                        # Asignar ID real y indexar usando el callback
                        if on_node_created:
                             # Si el contenido se guardó con un nombre temporal, renombrarlo ahora que tenemos el ID
                             if child_node.saved_content_path and "temp_node_content_" in child_node.saved_content_path:
                                 old_path_obj = Path(child_node.saved_content_path)
                                 new_name = f"node_content_{child_node.node_id}.dat" # Nombre final usando el ID real
                                 new_path_obj = old_path_obj.parent / new_name
                                 try:
                                     old_path_obj.rename(new_path_obj)
                                     child_node.saved_content_path = str(new_path_obj)
                                     # Actualizar el marcador en content si existe
                                     if isinstance(child_node.content, str) and child_node.content.startswith("<Content saved to disk at"):
                                         child_node.content = f"<Content saved to disk at {new_name}>"

                                 except Exception as e:
                                     print(f"Advertencia: No se pudo renombrar archivo de contenido guardado para nodo {child_node.node_id}: {e}")
                                     # Dejar la ruta temporal o marcar como error? Dejar temporal por ahora.

                             on_node_created(child_node)


                        # Llamada recursiva si es un directorio
                        if is_directory:
                            _scan_recursive(entry_obj, child_node, current_depth + 1)

                    except PermissionError:
                         dummy_metadata = type('obj', (object,), {'st_size': 0, 'st_mode': 0, 'st_mtime': 0, 'st_ctime': 0})()
                         child_node = FileSystemNode(-1, entry_obj.name, str(entry_obj), entry_obj.is_dir(), dummy_metadata, content="<Permission Denied>")
                         parent_node.add_child(child_node)
                         if on_node_created: on_node_created(child_node)
                    except Exception as e:
                         dummy_metadata = type('obj', (object,), {'st_size': 0, 'st_mode': 0, 'st_mtime': 0, 'st_ctime': 0})()
                         child_node = FileSystemNode(-1, entry_obj.name, str(entry_obj), entry_obj.is_dir(), dummy_metadata, content=f"<Processing Error: {e}>")
                         parent_node.add_child(child_node)
                         if on_node_created: on_node_created(child_node)

            except PermissionError: pass
            except Exception as e: pass

        if root_node.is_directory and (max_depth != 0):
             _scan_recursive(start_path, root_node, 1)

        return root_node

    except PermissionError: return None
    except Exception as e: return None