import cv2
import numpy as np
import queue
from memory_profiler import profile

# Constantes
ANCHO = 256
ALTO = 256
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
    def __init__(self, num_frames=NUM_FRAMES_DEFAULT):
        self.cola_frames = queue.Queue()
        self.num_frames = num_frames
        self.generar_frames_default()

    def generar_frames_default(self):
        for i in range(self.num_frames):
            frame = crear_frame_bn(ANCHO, ALTO, i)  # Pasa el índice del frame
            self.cola_frames.put(frame)

    def agregar_frame(self, frame):
        """
        Agrega un frame al buffer.
        """
        self.cola_frames.put(frame)

    def mostrar_frame(self):
        """
        Muestra un frame del buffer usando OpenCV.  Espera a que el usuario presione una tecla
        para mostrar el siguiente frame.
        """
        if not self.cola_frames.empty():
            frame = self.cola_frames.get()
            cv2.imshow("Buffer de Video", frame)
            cv2.waitKey(0)  # Espera a que el usuario presione una tecla
        else:
            print("El buffer está vacío.")

    def esta_vacio(self):
        """
        Verifica si el buffer está vacío.
        """
        return self.cola_frames.empty()

    def liberar(self):
          cv2.destroyAllWindows()

@profile
def main():
    """
    Función principal que ejecuta el simulador de buffer de video.
    """
    buffer = BufferVideo()

    while not buffer.esta_vacio():
        buffer.mostrar_frame()

    print("Fin del buffer de video.")
    buffer.liberar() # cerrar opencv

if __name__ == "__main__":
    main()

# Preguntas
