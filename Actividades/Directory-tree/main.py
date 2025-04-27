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
j_scan_parser.add_argument('--read-content', action='store_true', help='Incluir para intentar leer el contenido de los archivos.')
j_scan_parser.add_argument('--preview-bytes', type=int, default=1024, help='Límite de bytes para previsualización de contenido (por defecto 1024).')

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
save_parser.add_argument('--hide-metadata', action='store_false', dest='show_metadata', help='Ocultar metadatos en la salida.')


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
        'j-scan': j_scan_parser, # Ahora el scan flexible es j-scan
        's-scan': s_scan_parser, # Nuevo scan simple
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

            # Usar shlex.split para dividir la línea de forma segura (respeta comillas)
            try:
                parts = shlex.split(command_line)
                if not parts: continue
                command = parts[0].lower()
                args = parts[1:] # Argumentos restantes para el comando específico

            except ValueError as e:
                print(f"Error al parsear la línea de comando: {e}")
                continue # Volver a pedir input


            if command == 'help':
                if args:
                    target_command = args[0].lower()
                    if target_command in command_parsers:
                         print(f"\nAyuda para '{target_command}':")
                         command_parsers[target_command].print_help()
                    elif target_command == 'exit': # help exit
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
                    print("    Escanea con opciones configurables.")
                    print("  s-scan <ruta>")
                    print("    Escanea completamente sin opciones (simple).")
                    print("  print [--opciones...]")
                    print("  search <criterio1=valor1> [...]")
                    print("  open <node_id>")
                    print("  save <filename> [--opciones...]")
                    print("  exit")
                    print("\nEscribe 'help <comando>' para ver ayuda específica.")


            # --- Bloque corregido con indentación y parseo adecuado por comando ---
            elif command in command_parsers:
                # Obtener el parser para el comando
                command_parser = command_parsers[command]

                # Intentar parsear los argumentos usando el parser específico
                # Capturamos SystemExit que argparse lanza en caso de error o --help
                try:
                    parsed_args = command_parser.parse_args(args, namespace=argparse.Namespace())

                    # --- Ejecutar el comando basado en los argumentos parseados ---

                    if command == 'j-scan':
                        scan_path_cleaned = parsed_args.path.strip('<>')
                        directory_tree.scan(
                            scan_path_cleaned,
                            depth=parsed_args.depth,
                            read_content=parsed_args.read_content,
                            content_preview_bytes=parsed_args.preview_bytes
                        )

                    elif command == 's-scan':
                         scan_path_cleaned = parsed_args.path.strip('<>')
                         directory_tree.scan(
                              scan_path_cleaned,
                              depth=-1,
                              read_content=True,
                              content_preview_bytes=1024
                         )

                    elif command == 'print':
                        if not directory_tree.root:
                             print("Árbol vacío. Escanee un directorio primero con 'j-scan' o 's-scan'.")
                             continue
                        # Usar parsed_args directamente
                        directory_tree.print_tree(
                            depth=parsed_args.depth,
                            show_metadata=parsed_args.show_metadata # argparse handled this
                        )

                    elif command == 'search':
                         # Search criteria are handled separately as they are key=value pairs, not standard flags
                         if not directory_tree.root:
                             print("Árbol vacío. Escanee un directorio primero con 'j-scan' o 's-scan'.")
                             continue
                         if not args: # Check if there were any args passed *after* the search command
                             print("Error: El comando search requiere al menos un criterio. Uso: search <criterio1=valor1> ...")
                             continue

                         search_criteria = parse_search_criteria(args) # Parse the original args list from shlex.split
                         if search_criteria:
                              directory_tree.search_nodes(**search_criteria)
                         else:
                             print("No se pudieron parsear criterios de búsqueda válidos.")

                    elif command == 'open':
                         if not directory_tree.root:
                              print("Árbol vacío. Escanee un directorio primero con 'j-scan' o 's-scan'.")
                              continue
                         # Use parsed_args directly
                         directory_tree.display_node_details(parsed_args.node_id)

                    elif command == 'save':
                         if not directory_tree.root:
                              print("Árbol vacío. Escanee un directorio primero con 'j-scan' o 's-scan'.")
                              continue
                         # Use parsed_args directly
                         directory_tree.save_tree_printout(
                            parsed_args.filename,
                            depth=parsed_args.depth,
                            show_metadata=parsed_args.show_metadata # argparse handled this
                         )


                except SystemExit: # argparse called exit (e.g., --help or bad args)
                    # argparse already printed the error/help message
                    pass # Do nothing, just prevent the program from exiting
                except Exception as e: # Catch other potential errors during execution of the command logic
                    print(f"Error al ejecutar el comando '{command}': {e}")
            # --- Fin del Bloque corregido ---


            elif command == 'exit':
                print("Saliendo...")
                break # Salir del bucle

            else:
                print(f"Comando desconocido: '{command}'. Escribe 'help' para ver los comandos.")

        except EOFError:
             print("\nSaliendo (EOF)...")
             break # Salir con Ctrl+D/Ctrl+Z
        except Exception as e:
            print(f"Ocurrió un error inesperado en el bucle principal: {e}")


if __name__ == "__main__":
    main()