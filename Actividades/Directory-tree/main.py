# main.py

import sys
import argparse
import shlex
from pathlib import Path

# Importar la clase DirectoryTree desde el paquete src
from src.directory_tree import DirectoryTree

# --- Definición de Parsers para cada comando ---
# Usamos add_help=False para que el main loop maneje la impresión de ayuda
# Subparsers para los comandos

# Parser para el comando 'j-scan' (el configurable)
j_scan_parser = argparse.ArgumentParser(add_help=False)
j_scan_parser.add_argument('path', type=str, help='Ruta inicial del directorio a escanear (j-scan)')
j_scan_parser.add_argument('--depth', type=int, default=-1, help='Profundidad máxima (ej: 2). -1 para ilimitado (por defecto). 0 para solo raíz.')
# Opciones de lectura de contenido: mutuamente excluyentes en cuanto a *qué* se guarda.
# El usuario puede elegir entre: no leer, previsualizar, leer completo en memoria, o leer completo a disco.
# argparse.add_mutually_exclusive_group() podría usarse para forzar esto, pero simplificamos la lógica.
j_scan_parser.add_argument('--read-content', action='store_true', help='Leer previsualización de contenido de archivos (por defecto si no se especifica otra opción de contenido).')
j_scan_parser.add_argument('--read-full-content', action='store_true', help='Leer CONTENIDO COMPLETO de los archivos EN MEMORIA (¡PELIGROSO para directorios grandes!).')
j_scan_parser.add_argument('--save-content-to-disk', type=str, help='Directorio donde guardar copias del CONTENIDO COMPLETO de los archivos en disco.')
j_scan_parser.add_argument('--preview-bytes', type=int, default=1024, help='Límite de bytes para previsualización de contenido si --read-content se usa (por defecto 1024). Este valor se ignora si se usa --read-full-content o --save-content-to-disk.')


# Parser para el comando 's-scan' (el simple y completo)
s_scan_parser = argparse.ArgumentParser(add_help=False)
s_scan_parser.add_argument('path', type=str, help='Ruta inicial del directorio a escanear (s-scan)')


# Parser para el comando 'print'
print_parser = argparse.ArgumentParser(add_help=False)
print_parser.add_argument('--depth', type=int, default=-1, help='Profundidad máxima de impresión (-1 = ilimitado, por defecto).')
print_parser.add_argument('--show-metadata', action='store_true', default=True, help='Mostrar tamaño y fecha en la impresión (por defecto).')
print_parser.add_argument('--hide-metadata', action='store_false', dest='show_metadata', help='Ocultar tamaño y fecha en la impresión.')

# Parser para el comando 'search'
search_parser = argparse.ArgumentParser(add_help=False)
# Los criterios key=value se parsean manualmente después de shlex.split

# Parser para el comando 'open'
open_parser = argparse.ArgumentParser(add_help=False)
open_parser.add_argument('node_id', type=int, help='ID del nodo a abrir/mostrar detalles.')

# Parser para el comando 'save'
save_parser = argparse.ArgumentParser(add_help=False)
save_parser.add_argument('filename', type=str, help='Nombre del archivo de salida.')
save_parser.add_argument('--depth', type=int, default=-1, help='Profundidad máxima a guardar (-1 = ilimitado, por defecto).')
save_parser.add_argument('--show-metadata', action='store_true', default=True, help='Mostrar metadatos en la salida (por defecto).')
save_parser.add_metadata = True # Atributo auxiliar para la ayuda de save

# Función de ayuda para parsear argumentos de búsqueda (key=value)
def parse_search_criteria(criteria_list):
    """Convierte una lista de strings 'key=value' en un diccionario."""
    criteria = {}
    for item in criteria_list:
        if '=' in item:
            key, value = item.split('=', 1)
            criteria[key.lower()] = value # Convertir key a minúsculas
        else:
            print(f"Advertencia: Criterio de búsqueda ignorado por formato incorrecto: '{item}'. Usar 'key=value'.")
    return criteria


def main():
    """Función principal para la interfaz de consola."""

    print("--- Herramienta de Gestión de Estructura de Directorios ---")
    print("Escribe 'help' para ver los comandos disponibles.")

    directory_tree = DirectoryTree() # Instanciar el gestor del árbol

    # Mapeo de comandos a sus parsers
    command_parsers = {
        'j-scan': j_scan_parser,
        's-scan': s_scan_parser,
        'print': print_parser,
        'search': search_parser,
        'open': open_parser,
        'save': save_parser,
    }

    # Bucle principal de comandos
    while True:
        try:
            command_line = input("\n> ").strip()
            if not command_line:
                continue

            try:
                parts = shlex.split(command_line)
                if not parts: continue
                command = parts[0].lower()
                args = parts[1:]

            except ValueError as e:
                print(f"Error al parsear la línea de comando: {e}")
                continue


            if command == 'help':
                if args:
                    target_command = args[0].lower()
                    if target_command in command_parsers:
                         print(f"\nAyuda para '{target_command}':")
                         command_parsers[target_command].print_help()
                    elif target_command == 'exit':
                         print("\nAyuda para 'exit':")
                         print("  exit")
                         print("    Sale de la aplicación.")
                    else:
                         print(f"Comando desconocido para ayuda: '{target_command}'.")
                         print("Comandos disponibles: j-scan, s-scan, print, search, open, save, exit.")
                else:
                    # Ayuda general
                    print("\nComandos disponibles:")
                    print("  j-scan <ruta> [--opciones...]")
                    print("    Escanea con opciones configurables (profundidad, lectura de contenido: preview, full-memory, full-disk).") # Update help
                    print("  s-scan <ruta>")
                    print("    Escanea completamente con previsualización de contenido (simple).")
                    print("  print [--opciones...]")
                    print("  search <criterio1=valor1> [...]")
                    print("  open <node_id>")
                    print("  save <filename> [--opciones...]")
                    print("  exit")
                    print("\nEscribe 'help <comando>' para ver ayuda específica.")


            # --- Bloque de ejecución de comandos ---
            elif command in command_parsers:
                command_parser = command_parsers[command]
                try:
                    parsed_args = command_parser.parse_args(args, namespace=argparse.Namespace())

                    # --- Ejecutar el comando ---
                    if command == 'j-scan':
                        scan_path_cleaned = parsed_args.path.strip('<>')

                        # Lógica para determinar los flags de lectura/guardado
                        should_read_content = False # Por defecto no se lee nada
                        should_read_full_content = False
                        save_content_dir = None # Por defecto no se guarda en disco

                        if parsed_args.save_content_to_disk:
                             # Si se especifica guardar en disco, esto fuerza lectura completa y a disco
                             save_content_dir = parsed_args.save_content_to_disk
                             should_read_content = True
                             should_read_full_content = True
                             print(f"Modo: Guardar contenido completo en disco en '{save_content_dir}'.")
                        elif parsed_args.read_full_content:
                             # Si se pide leer completo en memoria (y no guardar en disco)
                             should_read_content = True
                             should_read_full_content = True
                             print("Modo: Leer contenido completo EN MEMORIA (¡PELIGROSO!).")
                        elif parsed_args.read_content:
                            # Si solo se pide leer contenido (implica previsualización si no se pide full)
                             should_read_content = True
                             should_read_full_content = False # Solo previsualización
                             print(f"Modo: Leer previsualización de contenido (hasta {parsed_args.preview_bytes} bytes).")
                        else:
                             print("Modo: No leer contenido de archivos.")


                        directory_tree.scan(
                            scan_path_cleaned,
                            depth=parsed_args.depth,
                            read_content=should_read_content,
                            read_full_content=should_read_full_content,
                            save_content_to_disk_dir=save_content_dir, # <-- Pasar la ruta de guardado (str o None)
                            content_preview_bytes=parsed_args.preview_bytes
                        )

                    elif command == 's-scan':
                         # S-scan: ilimitado, read_content=True (preview), read_full_content=False, save_content_to_disk_dir=None, preview=1024
                         print("Modo: Escaneo simple (completo, previsualización de contenido).")
                         scan_path_cleaned = parsed_args.path.strip('<>')
                         directory_tree.scan(
                              scan_path_cleaned,
                              depth=-1,
                              read_content=True, # Previsualización activa por defecto para s-scan
                              read_full_content=False, # S-scan NO lee contenido completo
                              save_content_to_disk_dir=None, # S-scan NO guarda en disco
                              content_preview_bytes=1024
                         )

                    elif command == 'print':
                        if not directory_tree.root:
                             print("Árbol vacío. Escanee un directorio primero con 'j-scan' o 's-scan'.")
                             continue
                        directory_tree.print_tree(
                            depth=parsed_args.depth,
                            show_metadata=parsed_args.show_metadata
                        )

                    elif command == 'search':
                         if not directory_tree.root:
                             print("Árbol vacío. Escanee un directorio primero con 'j-scan' o 's-scan'.")
                             continue
                         if not args:
                             print("Error: El comando search requiere al menos un criterio. Uso: search <criterio1=valor1> ...")
                             continue
                         search_criteria = parse_search_criteria(args)
                         if search_criteria:
                              directory_tree.search_nodes(**search_criteria)
                         else:
                             print("No se pudieron parsear criterios de búsqueda válidos.")

                    elif command == 'open':
                         if not directory_tree.root:
                              print("Árbol vacío. Escanee un directorio primero con 'j-scan' o 's-scan'.")
                              continue
                         directory_tree.display_node_details(parsed_args.node_id)

                    elif command == 'save':
                         if not directory_tree.root:
                              print("Árbol vacío. Escanee un directorio primero con 'j-scan' o 's-scan'.")
                              continue
                         directory_tree.save_tree_printout(
                            parsed_args.filename,
                            depth=parsed_args.depth,
                            show_metadata=parsed_args.show_metadata
                         )

                except SystemExit:
                    pass
                except Exception as e:
                    print(f"Error al ejecutar el comando '{command}': {e}")
            # --- Fin del Bloque de ejecución de comandos ---


            elif command == 'exit':
                print("Saliendo...")
                break

            else:
                print(f"Comando desconocido: '{command}'. Escribe 'help' para ver los comandos.")

        except EOFError:
             print("\nSaliendo (EOF)...")
             break
        except Exception as e:
            print(f"Ocurrió un error inesperado en el bucle principal: {e}")


if __name__ == "__main__":
    main()