# src/directory_tree.py

# ... (imports existentes) ...
import os
import stat
import datetime
from pathlib import Path # Asegúrate de tener Path importado
import json
import re

# Importar las clases y funciones necesarias
from .filesystem_node import FileSystemNode # FileSystemNode ahora tiene saved_content_path
from .directory_scanner import scan_directory # scan_directory ahora toma save_full_content_to_disk_path
from .tree_printer import build_tree_string


class DirectoryTree:
    """
    Gestiona la estructura del árbol de directorios escaneado y proporciona
    métodos para escanear, imprimir, buscar y acceder a nodos.
    """
    def __init__(self):
        self.root: FileSystemNode | None = None
        self.node_index: dict[int, FileSystemNode] = {}
        self._next_node_id = 0
        # Opcional: Podríamos almacenar la ruta donde se guardaron los archivos
        # si necesitamos limpiarlos más tarde, pero no se pidió explícitamente.
        # self._saved_content_dir: Path | None = None


    def _assign_id_and_index(self, node: FileSystemNode):
        # ... (igual) ...
        node.node_id = self._next_node_id
        self.node_index[self._next_node_id] = node
        self._next_node_id += 1
        if node.is_directory:
            for child in node.children: # Iterar sobre la lista interna para indexar
                self._assign_id_and_index(child)


    def scan(
        self,
        path: str,
        depth: int = -1,
        read_content: bool = False,
        read_full_content: bool = False,
        save_content_to_disk_dir: str | None = None, # <-- NUEVO PARAMETRO: Directorio donde guardar contenido completo
        content_preview_bytes: int = 1024
    ) -> FileSystemNode | None:
        """
        Escanea el directorio especificado y construye el árbol.
        Sobrescribe cualquier árbol escaneado previamente.
        Permite leer contenido (previsualización o completo) y guardar contenido completo en disco.
        """
        self.root = None
        self.node_index = {}
        self._next_node_id = 0
        # self._saved_content_dir = None # Resetear la ruta de guardado si se almacenara aquí

        start_path_obj = Path(path.strip().strip('"\''))

        print(f"Iniciando escaneo de: {start_path_obj}")
        if depth >= 0: print(f"Profundidad máxima de escaneo: {depth}")

        save_path_obj: Path | None = None
        if save_content_to_disk_dir:
            try:
                save_path_obj = Path(save_content_to_disk_dir).expanduser().resolve() # Expandir ~ y resolver ruta absoluta
                save_path_obj.mkdir(parents=True, exist_ok=True) # Crear el directorio si no existe
                # self._saved_content_dir = save_path_obj # Almacenar la ruta si fuera necesario
                print(f"Guardando contenido completo de archivos en disco en: {save_path_obj}")
                # Si se pide guardar en disco, read_content y read_full_content se fuerzan a True
                read_content = True
                read_full_content = True

            except Exception as e:
                 print(f"Error: No se pudo crear o acceder al directorio de guardado '{save_content_to_disk_dir}': {e}")
                 save_path_obj = None # No se podrá guardar

        # --- ADVERTENCIA DE USO DE MEMORIA SI read_full_content es True Y NO se guarda en disco ---
        # Esta advertencia es importante para el caso donde se pide --read-full-content pero SIN --save-content-to-disk
        elif read_full_content:
             print("!!! ADVERTENCIA !!! Leyendo el CONTENIDO COMPLETO de los archivos EN MEMORIA.")
             print("    Esto puede consumir una ENORME cantidad de memoria y colapsar el sistema en directorios grandes.")
             print("    Considere usar la opción --save-content-to-disk <directorio> para guardar en disco.")
        elif read_content:
             print(f"Leyendo previsualización del contenido de los archivos (hasta {content_preview_bytes} bytes por archivo).")
        else:
             print("No se leerá el contenido de los archivos.")


        try:
            # Usar la función de escaneo, pasando todos los parámetros
            self.root = scan_directory(
                start_path_obj,
                max_depth=depth,
                read_content=read_content,
                read_full_content=read_full_content,
                save_full_content_to_disk_path=save_path_obj, # <-- Pasar la ruta de guardado (Path obj o None)
                content_preview_bytes=content_preview_bytes,
                on_node_created=self._assign_id_and_index
            )

            if self.root:
                print("Escaneo completado.")
                print(f"Total de nodos escaneados: {len(self.node_index)}")
            else:
                print(f"Error: No se pudo escanear la ruta '{path}'.")

            return self.root

        except Exception as e:
            print(f"Ocurrió un error inesperado durante el escaneo: {e}")
            return None


    def print_tree(self, depth: int = -1, show_metadata: bool = True):
        # ... (igual) ...
        if not self.root: print("Árbol vacío. Escanee un directorio primero.") ; return
        print("\n--- Estructura del Directorio ---")
        print(f"Mostrando hasta profundidad: {'Ilimitada' if depth < 0 else depth}")
        tree_lines = build_tree_string(self.root, max_depth=depth, show_metadata=show_metadata)
        for line in tree_lines: print(line)
        print("--- Fin de la estructura ---")


    def save_tree_printout(self, filename: str, depth: int = -1, show_metadata: bool = True):
        # ... (igual) ...
        if not self.root: print("Árbol vacío. Escanee un directorio primero.") ; return
        print(f"Generando representación del árbol para guardar en '{filename}'...")
        print(f"Guardando hasta profundidad: {'Ilimitada' if depth < 0 else depth}")
        try:
            tree_lines = build_tree_string(self.root, max_depth=depth, show_metadata=show_metadata)
            with open(filename, 'w', encoding='utf-8') as f: f.write('\n'.join(tree_lines))
            print(f"Representación del árbol guardada exitosamente en '{filename}'.")
        except IOError as e: print(f"Error al guardar el archivo '{filename}': {e}")
        except Exception as e: print(f"Ocurrió un error inesperado al guardar: {e}")


    def get_node_by_id(self, node_id: int) -> FileSystemNode | None:
        # ... (igual) ...
         return self.node_index.get(node_id)


    def display_node_details(self, node_id: int):
        """
        Muestra la información detallada de un nodo específico.
        Si el contenido completo fue guardado en disco, lo lee desde allí.
        De lo contrario, muestra la previsualización o marcador en memoria.
        """
        node = self.get_node_by_id(node_id)
        if not node:
            print(f"Error: No se encontró ningún nodo con ID {node_id}.")
            return

        print(f"\n--- Detalles del Nodo [ID: {node.node_id}] ---")
        print(f"  Nombre: {node.name}")
        print(f"  Ruta: {node.path}")
        print(f"  Tipo: {'Directorio' if node.is_directory else 'Archivo'}")
        print(f"  Nivel en el árbol: {node.get_level()}")

        # Mostrar Metadatos
        print("  Metadatos:")
        metadata = node.metadata
        try: mod_time = datetime.datetime.fromtimestamp(metadata.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        except Exception: mod_time = "Fecha de modificación desconocida"
        try: creation_time = datetime.datetime.fromtimestamp(metadata.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
        except Exception: creation_time = "Fecha de creación/cambio desconocida"
        print(f"    Tamaño: {metadata.st_size} bytes")
        print(f"    Modificado: {mod_time}")
        print(f"    Creado/Cambiado: {creation_time}")
        print(f"    Permisos (modo): {stat.filemode(metadata.st_mode)}")

        # --- LOGICA DE MOSTRAR CONTENIDO (desde disco o memoria) ---
        if not node.is_directory:
             print("  Contenido:")
             if node.saved_content_path:
                  # Si la ruta de guardado existe, intentar leer desde allí
                  print(f"    (Contenido guardado en disco: {node.saved_content_path})")
                  try:
                      saved_file_path = Path(node.saved_content_path)
                      if saved_file_path.exists():
                           print("    --------------------")
                           # Leer y intentar decodificar el contenido guardado
                           with open(saved_file_path, 'rb') as f:
                               content_bytes = f.read()
                           try:
                               print(content_bytes.decode('utf-8', errors='replace')) # Usar 'replace' para manejar errores de decodificación
                           except Exception:
                               print(f"<No se pudo decodificar el contenido (binario?), {len(content_bytes)} bytes>")
                           print("    --------------------")
                      else:
                           print(f"    <Error: Archivo de contenido guardado no encontrado en {node.saved_content_path}>")
                  except Exception as e:
                       print(f"    <Error leyendo contenido guardado desde disco: {e}>")

             elif node.content is not None:
                  # Si no se guardó en disco, mostrar lo que está en memoria (previsualización o full)
                  print("    (Contenido en memoria):")
                  if isinstance(node.content, str) and (node.content.startswith('<Binary content') or node.content.startswith('<Error')):
                       print(f"    {node.content}")
                  else: # Contenido de texto (posiblemente truncado)
                       print("    --------------------")
                       print(node.content)
                       print("    --------------------")
                       if node.metadata.st_size > 0 and node.content == "":
                            print("    (Archivo vacío o no se pudo leer el contenido)")
                       # Verificar si el contenido en memoria está truncado (solo relevante si NO es full content)
                       # Esto es complejo de verificar con precisión solo por el string content.
                       # Asumimos que si no se usó --read-full-content y no hay ellipsis, puede estar truncado.
                       elif node.metadata.st_size > len(str(node.content).encode('utf-8')) and not (isinstance(node.content, str) and node.content.endswith("...")) and not isinstance(node.content, bytes):
                            print("    (Contenido en memoria probablemente truncado - use --read-full-content o --save-content-to-disk para leer completo)")


             else: # node.content is None
                 print("  Contenido: No se leyó el contenido para este archivo (opción read_content/read_full_content/save-content-to-disk fue False).")

        elif node.is_directory:
             print(f"  Contenido: Este es un directorio con {len(node.get_children())} {'hijo' if len(node.get_children()) == 1 else 'hijos'}.")

        print("---------------------------")


    def search_nodes(self, **criteria) -> list[FileSystemNode]:
        # ... (igual) ...
        if not self.root: print("Árbol vacío. Escanee un directorio primero.") ; return []
        print(f"Buscando nodos con criterios: {criteria}")

        matching_nodes = []

        def parse_size(size_str):
            # ... (igual) ...
            if isinstance(size_str, (int, float)): return size_str
            size_str = str(size_str).strip().upper()
            if size_str.endswith("KB"): return float(size_str[:-2]) * 1024
            if size_str.endswith("MB"): return float(size_str[:-2]) * 1024 * 1024
            if size_str.endswith("GB"): return float(size_str[:-2]) * 1024 * 1024 * 1024
            try: return float(size_str)
            except ValueError: return -1

        min_size = parse_size(criteria.get('min_size', -1))
        max_size = parse_size(criteria.get('max_size', float('inf')))
        target_level = criteria.get('level', None)

        name_pattern = criteria.get('name', None)
        name_regex = None
        if name_pattern:
            try:
                if '*' in name_pattern or '?' in name_pattern: name_regex = re.compile(re.escape(name_pattern).replace(r'\*', '.*').replace(r'\?', '.'))
                else: name_regex = re.compile(re.escape(name_pattern) + r'$')
            except re.error as e: print(f"Error en el patrón de nombre (regex): {e}") ; name_regex = None

        content_text = criteria.get('content', None)
        content_regex = None
        if content_text:
             try: content_regex = re.compile(re.escape(content_text), re.IGNORECASE)
             except re.error as e: print(f"Error en el patrón de contenido (regex): {e}") ; content_regex = None

        # Note: Search by content will only work if content was read (preview or full)
        # It will NOT automatically read content from disk if saved_content_path is set
        # Implementing search by content from disk would require significant modifications
        # to potentially read many files from disk during search, which can be slow.
        # For now, search by content operates only on the `node.content` attribute.


        def _search_recursive(node: FileSystemNode):
            matches = True

            if name_regex and not name_regex.search(node.name): matches = False
            node_type_crit = criteria.get('type', None)
            if node_type_crit:
                if node_type_crit.lower() == 'file' and node.is_directory: matches = False
                elif node_type_crit.lower() == 'dir' and not node.is_directory: matches = False

            if not node.is_directory:
                if node.metadata.st_size < min_size or node.metadata.st_size > max_size: matches = False
            elif 'min_size' in criteria or 'max_size' in criteria: matches = False

            if target_level is not None and node.get_level() != target_level: matches = False

            # Criterio: Contenido (solo para archivos que tienen content en memoria, NO desde saved_content_path)
            if not node.is_directory and content_regex:
                 if not isinstance(node.content, str) or node.content.startswith('<'): matches = False
                 elif not content_regex.search(node.content): matches = False
            elif node.is_directory and content_regex: matches = False


            if matches: matching_nodes.append(node)
            if node.is_directory:
                for child in node.get_children(): _search_recursive(child)

        _search_recursive(self.root)
        print(f"Encontrados {len(matching_nodes)} nodos que coinciden.")
        return matching_nodes