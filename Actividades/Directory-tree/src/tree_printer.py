# src/tree_printer.py

from .filesystem_node import FileSystemNode # Importar la clase FileSystemNode
import datetime

def build_tree_string(node: FileSystemNode, max_depth: int = -1, indent: str = "", is_last: bool = True, show_metadata: bool = True) -> list[str]:
    """
    Construye una lista de cadenas representando visualmente la estructura del árbol
    de directorios de forma recursiva, respetando un límite de profundidad.

    Args:
        node (FileSystemNode): El nodo actual a procesar.
        max_depth (int, optional): La profundidad máxima a imprimir (-1 = ilimitado, 0 = solo nodo actual, 1 = actual + hijos, etc.). Defaults to -1.
        indent (str, optional): La cadena de indentación acumulada. Defaults to "".
        is_last (bool, optional): Indica si este nodo es el último hijo de su padre. Defaults to True.
        show_metadata (bool, optional): Si es True, muestra metadatos básicos (tamaño y fecha). Defaults to True.

    Returns:
        list[str]: Una lista de cadenas, donde cada cadena es una línea de la salida visual.
    """
    lines = []
    node_level = node.get_level() # Obtener el nivel del nodo

    # Detener la recursión si excede la profundidad máxima (excepto si es el nodo raíz y max_depth es 0)
    # Si max_depth es 0, solo imprimimos la raíz y detenemos.
    if max_depth >= 0 and node_level > max_depth:
         return [] # No añadir líneas y detener la recursión para esta rama

    # Símbolos para dibujar el árbol
    if node_level == 0: # El nodo raíz (nivel 0) no tiene prefijo de rama
        branch_prefix = ""
        # Ajustar la indentación base para los hijos de la raíz
        child_indent_base = ""
    else:
        branch_prefix = '└── ' if is_last else '├── '
        # La indentación para los hijos se basa en la indentación actual y el prefijo del padre
        child_indent_base = indent + ('    ' if is_last else '│   ')


    print_str = f"{indent}{branch_prefix}[{node.node_id}] {node.name}" # Incluir ID del nodo

    if show_metadata:
        # Formatear metadatos básicos
        size_kb = node.metadata.st_size / 1024
        try:
             mod_time = datetime.datetime.fromtimestamp(node.metadata.st_mtime).strftime('%Y-%m-%d %H:%M')
        except Exception:
             mod_time = "Fecha desconocida"

        meta_info = f" ({'Dir' if node.is_directory else f'{size_kb:.2f} KB'}, Mod: {mod_time})"
        print_str += meta_info

    lines.append(print_str)

    # Si es un directorio y no hemos alcanzado la profundidad máxima de impresión (o si es ilimitada)
    if node.is_directory and (max_depth < 0 or node_level < max_depth):
        # Obtener hijos ordenados
        sorted_children = node.get_children() # get_children ya ordena

        for i, child in enumerate(sorted_children):
            child_is_last = (i == len(sorted_children) - 1)
            # Llamada recursiva para los hijos, incrementando la indentación
            child_lines = build_tree_string(child, max_depth, child_indent_base, child_is_last, show_metadata)
            lines.extend(child_lines) # Usa extend para añadir todas las líneas de los hijos

    return lines