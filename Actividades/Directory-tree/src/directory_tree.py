# src/directory_tree.py

import os
import stat
import datetime
from pathlib import Path
import json # Opcional: para guardar/cargar metadatos complejos si fuera necesario, aunque no se pide
import re # Para búsqueda por patrón (regex)

# Importar las clases y funciones necesarias del mismo directorio src
from .filesystem_node import FileSystemNode
from .directory_scanner import scan_directory
from .tree_printer import build_tree_string


class DirectoryTree:
    """
    Gestiona la estructura del árbol de directorios escaneado y proporciona
    métodos para escanear, imprimir, buscar y acceder a nodos.
    """
    def __init__(self):
        self.root: FileSystemNode | None = None
        # Diccionario para indexar nodos por su ID único
        self.node_index: dict[int, FileSystemNode] = {}
        self._next_node_id = 0 # Contador para asignar IDs únicos

    def _assign_id_and_index(self, node: FileSystemNode):
        """Asigna un ID único al nodo y lo agrega al índice."""
        node.node_id = self._next_node_id
        self.node_index[self._next_node_id] = node
        self._next_node_id += 1
        # Llamada recursiva para los hijos si es un directorio
        if node.is_directory:
            # No necesitamos ordenar aquí, ya que scan_directory lo hace antes de añadir
            for child in node.children: # Iterar sobre la lista interna, no la ordenada de get_children() para la indexación
                self._assign_id_and_index(child)


    def scan(
        self,
        path: str,
        depth: int = -1,
        read_content: bool = False,
        content_preview_bytes: int = 1024
    ) -> FileSystemNode | None:
        """
        Escanea el directorio especificado y construye el árbol.
        Sobrescribe cualquier árbol escaneado previamente.

        Args:
            path (str): La ruta inicial como cadena.
            depth (int, optional): Profundidad máxima de escaneo. Defaults to -1 (ilimitado).
            read_content (bool, optional): Leer contenido de archivos. Defaults to False.
            content_preview_bytes (int, optional): Bytes para previsualización. Defaults to 1024.

        Returns:
            FileSystemNode | None: El nodo raíz escaneado, o None si falla.
        """
        # Limpiar el estado anterior antes de un nuevo escaneo
        self.root = None
        self.node_index = {}
        self._next_node_id = 0

        start_path_obj = Path(path.strip().strip('"\''))

        print(f"Iniciando escaneo de: {start_path_obj}")
        if depth >= 0:
            print(f"Profundidad máxima de escaneo: {depth}")
        if read_content:
            print(f"Leyendo contenido de archivos (hasta {content_preview_bytes} bytes por archivo).")

        try:
            # Usar la función de escaneo, pasando el método de indexación como callback
            self.root = scan_directory(
                start_path_obj,
                max_depth=depth,
                read_content=read_content,
                content_preview_bytes=content_preview_bytes,
                on_node_created=self._assign_id_and_index # Pasar el método de indexación
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
        """
        Imprime el árbol en la consola con un límite de profundidad.

        Args:
            depth (int, optional): Profundidad máxima de impresión (-1 = ilimitado). Defaults to -1.
            show_metadata (bool, optional): Mostrar metadatos en la impresión. Defaults to True.
        """
        if not self.root:
            print("Árbol vacío. Escanee un directorio primero.")
            return

        print("\n--- Estructura del Directorio ---")
        print(f"Mostrando hasta profundidad: {'Ilimitada' if depth < 0 else depth}")

        # Usar la función de construcción de cadena de impresión
        tree_lines = build_tree_string(self.root, max_depth=depth, show_metadata=show_metadata)

        # Imprimir las líneas generadas
        for line in tree_lines:
            print(line)

        print("--- Fin de la estructura ---")


    def save_tree_printout(self, filename: str, depth: int = -1, show_metadata: bool = True):
        """
        Guarda la representación visual del árbol en un archivo.

        Args:
            filename (str): El nombre del archivo de salida (.txt o .md).
            depth (int, optional): Profundidad máxima a guardar. Defaults to -1 (ilimitado).
            show_metadata (bool, optional): Mostrar metadatos en la salida. Defaults to True.
        """
        if not self.root:
            print("Árbol vacío. Escanee un directorio primero.")
            return

        print(f"Generando representación del árbol para guardar en '{filename}'...")
        print(f"Guardando hasta profundidad: {'Ilimitada' if depth < 0 else depth}")

        try:
            # Usar la función de construcción de cadena de impresión
            tree_lines = build_tree_string(self.root, max_depth=depth, show_metadata=show_metadata)

            # Guardar en archivo
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(tree_lines))

            print(f"Representación del árbol guardada exitosamente en '{filename}'.")

        except IOError as e:
            print(f"Error al guardar el archivo '{filename}': {e}")
        except Exception as e:
            print(f"Ocurrió un error inesperado al guardar: {e}")


    def get_node_by_id(self, node_id: int) -> FileSystemNode | None:
        """Retorna un nodo dado su ID único."""
        return self.node_index.get(node_id)


    def display_node_details(self, node_id: int):
        """
        Muestra la información detallada de un nodo específico y su contenido
        (si fue leído durante el escaneo).
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
        try:
            mod_time = datetime.datetime.fromtimestamp(metadata.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            mod_time = "Fecha de modificación desconocida"
        try:
            creation_time = datetime.datetime.fromtimestamp(metadata.st_ctime).strftime('%Y-%m-%d %H:%M:%S') # st_ctime puede ser creación o cambio (OS dep.)
        except Exception:
             creation_time = "Fecha de creación/cambio desconocida"

        print(f"    Tamaño: {metadata.st_size} bytes")
        print(f"    Modificado: {mod_time}")
        print(f"    Creado/Cambiado: {creation_time}")
        print(f"    Permisos (modo): {stat.filemode(metadata.st_mode)}")
        # Puedes añadir más metadatos si son relevantes (ej: st_uid, st_gid, etc.)


        # Mostrar Contenido (si fue leído)
        if not node.is_directory and node.content is not None:
            print("  Contenido (previsualización):")
            if isinstance(node.content, str) and node.content.startswith('<'): # Indicador de error o binario
                 print(f"    {node.content}")
            else: # Contenido de texto (posiblemente truncado)
                 print("    --------------------")
                 print(node.content)
                 print("    --------------------")
                 if node.metadata.st_size > 0 and node.content == "": # Si el archivo no estaba vacío pero el contenido es vacío
                      print("    (Archivo vacío o no se pudo leer el contenido)")


        elif not node.is_directory and node.content is None:
             print("  Contenido: No se leyó el contenido para este archivo (opción read_content=False).")

        elif node.is_directory:
             print(f"  Contenido: Este es un directorio con {len(node.get_children())} {'hijo' if len(node.get_children()) == 1 else 'hijos'}.")

        print("---------------------------")


    def search_nodes(self, **criteria) -> list[FileSystemNode]:
        """
        Busca nodos en el árbol basándose en varios criterios.

        Args:
            criteria (dict): Diccionario de criterios de búsqueda.
                             Ej: name="*.py", type="file", min_size=1000, max_size=10MB, level=2, content="texto"

        Returns:
            list[FileSystemNode]: Lista de nodos que coinciden con todos los criterios.
        """
        if not self.root:
            print("Árbol vacío. Escanee un directorio primero.")
            return []

        print(f"Buscando nodos con criterios: {criteria}")

        matching_nodes = []

        # Convertir criterios de tamaño si son strings (ej: "10MB", "5KB")
        # Simple parser de tamaño para KB/MB
        def parse_size(size_str):
            if isinstance(size_str, (int, float)):
                return size_str # Ya es un número

            size_str = str(size_str).strip().upper()
            if size_str.endswith("KB"):
                return float(size_str[:-2]) * 1024
            if size_str.endswith("MB"):
                return float(size_str[:-2]) * 1024 * 1024
            if size_str.endswith("GB"):
                return float(size_str[:-2]) * 1024 * 1024 * 1024
            try:
                return float(size_str) # Asumir que es en bytes si no tiene sufijo
            except ValueError:
                return -1 # Valor inválido

        min_size = parse_size(criteria.get('min_size', -1))
        max_size = parse_size(criteria.get('max_size', float('inf')))
        target_level = criteria.get('level', None) # Nivel exacto

        # Criterios para regex
        name_pattern = criteria.get('name', None)
        name_regex = None
        if name_pattern:
            try:
                # Convertir patrón glob (*.py) a regex o usar regex directa
                if '*' in name_pattern or '?' in name_pattern:
                    name_regex = re.compile(re.escape(name_pattern).replace(r'\*', '.*').replace(r'\?', '.'))
                else:
                    # Coincidencia exacta si no hay caracteres especiales de glob
                    name_regex = re.compile(re.escape(name_pattern) + r'$') # Asegurar coincidencia exacta

            except re.error as e:
                print(f"Error en el patrón de nombre (regex): {e}")
                name_regex = None # Invalidar el patrón

        content_text = criteria.get('content', None)
        content_regex = None
        if content_text:
             try:
                  content_regex = re.compile(re.escape(content_text), re.IGNORECASE) # Búsqueda de contenido case-insensitive
             except re.error as e:
                  print(f"Error en el patrón de contenido (regex): {e}")
                  content_regex = None


        # Función recursiva para buscar
        def _search_recursive(node: FileSystemNode):
            # Verificar si el nodo actual coincide con todos los criterios
            matches = True

            # Criterio: Nombre (Regex)
            if name_regex and not name_regex.search(node.name):
                matches = False

            # Criterio: Tipo
            node_type_crit = criteria.get('type', None)
            if node_type_crit:
                if node_type_crit.lower() == 'file' and node.is_directory:
                    matches = False
                elif node_type_crit.lower() == 'dir' and not node.is_directory:
                    matches = False

            # Criterio: Tamaño (solo para archivos)
            if not node.is_directory:
                if node.metadata.st_size < min_size or node.metadata.st_size > max_size:
                    matches = False
            elif 'min_size' in criteria or 'max_size' in criteria: # Si se especifica tamaño pero es un directorio
                 matches = False # Directorios no tienen tamaño de contenido de archivo

            # Criterio: Nivel
            if target_level is not None and node.get_level() != target_level:
                 matches = False

            # Criterio: Contenido (solo para archivos que fueron leídos y no son binarios/error markers)
            if not node.is_directory and content_regex:
                 if not isinstance(node.content, str) or node.content.startswith('<'): # No es texto o es un marcador
                      matches = False
                 elif not content_regex.search(node.content): # No coincide el regex en el contenido de texto
                      matches = False
             # Si es directorio y se busca por contenido
            elif node.is_directory and content_regex:
                 matches = False


            # Criterios adicionales (ej: fechas, permisos, etc.) - puedes añadir más aquí
            # Ej: min_mtime="YYYY-MM-DD", max_mtime="YYYY-MM-DD"
            # try:
            #     min_mtime_ts = datetime.datetime.fromisoformat(criteria['min_mtime']).timestamp() if 'min_mtime' in criteria else 0
            #     if node.metadata.st_mtime < min_mtime_ts: matches = False
            # except (ValueError, KeyError): pass # Ignorar si el formato es incorrecto

            # Si el nodo coincide con todos los criterios, añadirlo a la lista
            if matches:
                matching_nodes.append(node)

            # Continuar buscando en los hijos si es un directorio
            if node.is_directory:
                for child in node.get_children(): # Usar get_children() que ya ordena
                    _search_recursive(child)


        _search_recursive(self.root) # Iniciar la búsqueda desde la raíz

        print(f"Encontrados {len(matching_nodes)} nodos que coinciden.")
        return matching_nodes