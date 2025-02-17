import cv2
import numpy as np
import queue
import os
import argparse
import requests
import imageio  # Necesario: pip install imageio imageio[pyav]
from io import BytesIO

# Constantes
ANCHO = 498
ALTO = 353
NUM_FRAMES_DEFAULT = 30

def crear_frame_bn(ancho, alto, frame_index):
    """
    Crea un frame en blanco y negro con un degradado que varía con el índice del frame.
    """
    frame = np.zeros((alto, ancho), dtype=np.uint8)
    for y in range(alto):
        for x in range(ancho):
            frame[y, x] = (x + y + frame_index) % 256
    return frame

class BufferVideo:
    def __init__(self, carpeta_imagenes=None, url_gif=None, ancho=None, alto=None, num_frames=None):
        """
        Inicializa el buffer de video. Puede cargar imágenes desde una carpeta,
        un GIF desde una URL, o generar frames por defecto. También permite
        especificar el ancho, alto y número de frames.
        """
        self.cola_frames = queue.Queue()
        self.ancho = ancho
        self.alto = alto
        self.num_frames = num_frames

        if url_gif:
            self.cargar_gif_desde_url("https://media1.tenor.com/m/fysPvalDmXcAAAAd/ataque-pokemon-batalla-pokemon.gif")
        elif carpeta_imagenes:
            self.cargar_imagenes_desde_carpeta(carpeta_imagenes)
        else: 
            if not self.ancho:
                self.ancho = ANCHO  # Usa el valor por defecto si no se especifica 
            if not self.alto:
                self.alto = ALTO  # Usa el valor por defecto si no se especifica
            if not self.num_frames:
                self.num_frames = NUM_FRAMES_DEFAULT  # Usa el valor por defecto si no se especifica
            self.generar_frames_default()


    def cargar_gif_desde_url(self, url):
        """
        Descarga un GIF desde una URL y extrae los frames.
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Lanza una excepción para errores HTTP

            gif_data = BytesIO(response.content)
            reader = imageio.get_reader(gif_data, "gif") # Use "gif" explicitly

            # Detecta ancho y alto automáticamente del primer frame
            primer_frame = reader.get_next_data()
            self.alto, self.ancho = primer_frame.shape[:2]

            if not self.num_frames:
                self.num_frames = reader.get_length()

            for i, frame_data in enumerate(reader):
                if i >= self.num_frames:
                    break  # Límite al número de frames especificado
                frame = cv2.cvtColor(frame_data, cv2.COLOR_RGB2GRAY)  # Convierte a escala de grises
                self.cola_frames.put(frame)

            print(f"Se cargaron {self.num_frames} frames desde el GIF en {url}")

            reader.close()

        except requests.exceptions.RequestException as e:
            print(f"Error al descargar el GIF desde {url}: {e}")
        except imageio.core.fetching.NeedDownloadError as e:
            print(f"Error: Necesitas descargar los codecs de video necesarios.  Por favor, sigue las instrucciones en la página web que se muestra.  Error original: {e}")
        except Exception as e:
            print(f"Error al procesar el GIF desde {url}: {e}")

    def cargar_imagenes_desde_carpeta(self, carpeta):
        try:
            lista_imagenes = sorted([f for f in os.listdir(carpeta) if f.endswith(('.png', '.jpg', '.jpeg'))]) # Asegura orden alfabético
            if not lista_imagenes:
                raise ValueError("No se encontraron imágenes en la carpeta.")

            # Detecta ancho y alto automáticamente de la primera imagen
            ruta_primera_imagen = os.path.join(carpeta, lista_imagenes[0])
            primer_frame = cv2.imread(ruta_primera_imagen, cv2.IMREAD_GRAYSCALE)
            if primer_frame is None:
                 raise ValueError(f"No se pudo cargar la primera imagen: {ruta_primera_imagen}")
            self.alto, self.ancho = primer_frame.shape[:2]

            for nombre_archivo in lista_imagenes:
                ruta_completa = os.path.join(carpeta, nombre_archivo)
                frame = cv2.imread(ruta_completa, cv2.IMREAD_GRAYSCALE)  # Carga en escala de grises
                if frame is None:
                    print(f"Error al cargar la imagen: {nombre_archivo}")
                    continue  # Salta a la siguiente imagen si falla la carga
                self.cola_frames.put(frame)

            if not self.num_frames:
                 self.num_frames = len(lista_imagenes) # Toma el numero de imagenes si no se especifica
            print(f"Se cargaron {len(lista_imagenes)} imágenes desde {carpeta}")


        except FileNotFoundError:
            print(f"Error: La carpeta {carpeta} no se encontró.")
        except ValueError as e:
            print(f"Error: {e}")

    def generar_frames_default(self):
        """
        Genera y agrega los frames por defecto al buffer.
        """
        for i in range(self.num_frames):
            frame = crear_frame_bn(self.ancho, self.alto, i)
            self.cola_frames.put(frame)

    def agregar_frame(self, frame):
        self.cola_frames.put(frame)

    def mostrar_frame(self):
        if not self.cola_frames.empty():
            frame = self.cola_frames.get()
            cv2.imshow("Buffer de Video", frame)
            cv2.waitKey(0)
        else:
            print("El buffer está vacío.")

    def esta_vacio(self):
        return self.cola_frames.empty()

    def liberar(self):
          cv2.destroyAllWindows()

def main():
    """
    Función principal que ejecuta el simulador de buffer de video.
    """
    parser = argparse.ArgumentParser(description="Simulador de buffer de video.")
    parser.add_argument("--carpeta", type=str, help="Ruta a la carpeta de imágenes.")
    parser.add_argument("--url_gif", type=str, help="URL del GIF.")
    parser.add_argument("--ancho", type=int, help="Ancho de los frames.")
    parser.add_argument("--alto", type=int, help="Alto de los frames.")
    parser.add_argument("--num_frames", type=int, help="Número de frames a usar.")
    args = parser.parse_args()

    buffer = BufferVideo(
        carpeta_imagenes=args.carpeta,
        url_gif=args.url_gif,
        ancho=args.ancho,
        alto=args.alto,
        num_frames=args.num_frames
    )

    while not buffer.esta_vacio():
        buffer.mostrar_frame()

    print("Fin del buffer de video.")
    buffer.liberar()

if __name__ == "__main__":
    main()


  