# src/filesystem_node.py

import os
import stat
import datetime
from pathlib import Path

class FileSystemNode:
    """
    Representa un archivo o carpeta en el sistema de archivos.
    Incluye metadatos, contenido (opcional/previsualización) y referencias a hijos.
    """
    def __init__(self, node_id: int, name: str, path: str, is_directory: bool, metadata: os.stat_result, content=None):
        """
        Inicializa un nodo del sistema de archivos.

        Args:
            node_id (int): Identificador único del nodo dentro del árbol escaneado.
            name (str): El nombre del archivo o carpeta.
            path (str): La ruta completa (como string) del archivo o carpeta.
            is_directory (bool): True si es una carpeta, False si es un archivo.
            metadata (os.stat_result): Objeto stat con metadatos del archivo/carpeta.
            content (any, optional): Contenido del archivo (bytes, string, o marcador de error/binario/preview). Defaults to None.
        """
        self.node_id = node_id
        self.name = name
        self.path = path
        self.is_directory = is_directory
        self.metadata = metadata # Objeto stat con st_size, st_mtime, st_mode, etc.
        self.content = content  # Almacena la previsualización o un marcador (si no se guarda completo en disco)
        self.saved_content_path: str | None = None # <-- NUEVO ATRIBUTO: Ruta al archivo guardado en disco si se usó --save-content-to-disk
        self.children = []
        self.parent = None

    def add_child(self, child_node: 'FileSystemNode'):
        # ... (igual) ...
         if self.is_directory:
             self.children.append(child_node)
             child_node.parent = self
         else:
             pass

    def get_children(self):
        # ... (igual) ...
         return sorted(self.children, key=lambda child: (not child.is_directory, child.name))


    def get_level(self):
        # ... (igual) ...
        level = 0
        current = self
        while current.parent:
            level += 1
            current = current.parent
        return level


    def __repr__(self):
        # ... (igual) ...
        type_str = "Dir" if self.is_directory else "File"
        return f"Node(ID={self.node_id}, Type={type_str}, Name='{self.name}')"

    def __str__(self):
        # ... (igual) ...
        return f"[{self.node_id}] {self.name} ({'Dir' if self.is_directory else 'File'})"