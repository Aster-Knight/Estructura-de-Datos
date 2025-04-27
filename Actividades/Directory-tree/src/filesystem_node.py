# src/filesystem_node.py

import os
import stat
import datetime
from pathlib import Path # Aunque el path se almacena como string, Path es útil para ciertas operaciones

class FileSystemNode:
    """
    Representa un archivo o carpeta en el sistema de archivos.
    Incluye metadatos, contenido (opcional) y referencias a hijos.
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
            content (any, optional): Contenido del archivo (bytes, string, o marcador de error/binario). Defaults to None.
        """
        self.node_id = node_id
        self.name = name
        self.path = path
        self.is_directory = is_directory
        self.metadata = metadata # Objeto stat con st_size, st_mtime, st_mode, etc.
        self.content = content  # Almacena el contenido (o una previsualización/marcador)
        self.children = [] # Lista de FileSystemNode para directorios
        self.parent = None # Referencia al nodo padre para navegación

    def add_child(self, child_node: 'FileSystemNode'):
        """Agrega un nodo hijo a este nodo (si es un directorio) y establece el padre del hijo."""
        if self.is_directory:
            self.children.append(child_node)
            child_node.parent = self # Establecer la referencia al padre
        else:
            # No se pueden añadir hijos a archivos
            pass

    def get_children(self):
        """Retorna la lista de nodos hijos (vacía si es un archivo)."""
        # Opcional: ordenar hijos por defecto (directorios primero, luego archivos)
        return sorted(self.children, key=lambda child: (not child.is_directory, child.name))


    def get_level(self):
        """Calcula el nivel de profundidad del nodo en el árbol."""
        level = 0
        current = self
        # Recorrer hacia arriba hasta la raíz (padre es None)
        while current.parent:
            level += 1
            current = current.parent
        return level


    def __repr__(self):
        """Representación amigable del nodo para depuración."""
        type_str = "Dir" if self.is_directory else "File"
        return f"Node(ID={self.node_id}, Type={type_str}, Name='{self.name}')"

    def __str__(self):
        """Representación en cadena básica del nodo."""
        return f"[{self.node_id}] {self.name} ({'Dir' if self.is_directory else 'File'})"