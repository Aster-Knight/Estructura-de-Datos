# inciso 1, selecciónar una clase que hayamos trabajado en clase para el ejercicio

import time
import cProfile
import sys
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import io
import pstats
from tabulate import tabulate 


class Stack:
    def __init__(self, size:int):
        self.max = size
        self.elements = [None] * size
        self.top = -1

    def __repr__(self):
        return f'Current Stack: {self.elements} | Top: {self.top}'
    
    def push(self, val: str) -> None:
        if self.top == self.max - 1:
            print('Stack is full')
            return None
        self.top += 1
        self.elements[self.top] = val

    def pop(self) -> any:
        if self.top == -1:
            print('Stack underflow')
            return None
        
        val = self.elements[self.top]
        self.elements[self.top] = None 
        self.top -= 1
        return val
    
    def peek(self) -> any:
        if self.top == -1:
            print('Stack underflow')
            return None

        return self.elements[self.top]
    

    # inciso 4, implementar el método search. El metodo es una busqueda lineal que recorre la pila desde la cima hacia la base
    def search(self, key: str) -> int | None:
        """
        Busca la posición de la clave (key) en la pila.
        Retorna la distancia desde la cima (0 si está en la cima) o None si no se encuentra.
        """
        for i in range(self.top, -1, -1):  # Itera desde la cima hacia la base
            if self.elements[i] == key:
                return self.top - i  # Calcula la distancia desde la cima
        return None  # Retorna None si no se encuentra la clave
    
    def clear(self) -> None:
        """
        Vacía la pila eliminando todos los elementos.
        """
        while self.top != -1:
            self.pop()

def llenar_stack_con_ceros(stack):
    """
    Llena la pila con ceros.
    """
    for _ in range(stack.max):
        stack.push("0")

def linear_search(n_try, clave_a_buscar):
    """
    Realiza una búsqueda lineal
    de clave_a_buscar, y mide el tiempo de ejecución.
    """

    global instruction_count # Indica que estamos usando la variable global
    instruction_count = 0 # Resetea el contador para esta función

    stack = Stack(n_try)

    llenar_stack_con_ceros(stack)

    inicio = time.time()
    posicion = stack.search(clave_a_buscar)  # Usa el método search existente
    fin = time.time()
    tiempo_ejecucion = fin - inicio

    
    return tiempo_ejecucion, instruction_count

def medir_tiempo_clear(n_try):
    """
    Mide el tiempo que tarda en vaciar una pila de longitud n_try utilizando pop.
    """
    global instruction_count # Indica que estamos usando la variable global
    instruction_count = 0 # Resetea el contador para esta función


    stack = Stack(n_try)
    llenar_stack_con_ceros(stack)  # Llenar la pila con ceros

    inicio = time.time()
    stack.clear()  # Vaciar la pila
    fin = time.time()
    tiempo_ejecucion = fin - inicio

    return tiempo_ejecucion, instruction_count

def trace_calls(frame, event, arg):
    """
    Función de rastreo que se llama en cada línea de código ejecutada.
    """
    global instruction_count
    instruction_count += 1
    return trace_calls

# Variables globales para almacenar los resultados
instruction_count = 0
results = [] # Se inicializa como lista y no como diccionario

if __name__ == "__main__":
    def main():
        global instruction_count, results

        n_try = 5999590  # Define el valor de n
        clave_a_buscar = "5"  # Define la clave a buscar
        n_values = [n_try, 2 * n_try, 3 * n_try, 4 * n_try, 5 * n_try]
        results = []  # Lista para almacenar los resultados

        # Activar el rastreo de instrucciónes
        sys.settrace(trace_calls)

        for n in n_values:
            #linear_search
            tiempo_busqueda, instruction_count_ls = linear_search(n, clave_a_buscar)
            results.append({
                'Algoritmo': 'linear_search',
                'n_try': n,
                'Tiempo': tiempo_busqueda,
                'Instrucciones': instruction_count_ls
            })
            
            #medir_tiempo_clear
            tiempo_clear, instruction_count_mc = medir_tiempo_clear(n)
            results.append({
                'Algoritmo': 'medir_tiempo_clear',
                'n_try': n,
                'Tiempo': tiempo_clear,
                'Instrucciones': instruction_count_mc
            })
            
        # Desactivar el rastreo
        sys.settrace(None)

        # Imprimir los resultados (opcional)
        #for result in results:
        #    print(result)

        #Paso 3: Crear un DataFrame de Pandas
        df = pd.DataFrame(results)

        '''
        #Paso 4: Crear las Gráficas con Seaborn
        # Gráfica de Tiempo vs. n_try
        plt.figure(figsize=(10, 6))
        sns.lineplot(x='n_try', y='Tiempo', hue='Algoritmo', data=df)
        plt.title('Tiempo de Ejecución vs. n_try')
        plt.xlabel('n_try')
        plt.ylabel('Tiempo (segundos)')
        plt.grid(True)
        plt.savefig('tiempo_vs_ntry.png')  # Guardar la gráfica como archivo PNG
        plt.show()
        '''

        # Gráfica de Número de Instrucciones vs. n_try
        plt.figure(figsize=(12, 7))  # Aumentar el tamaño para mejor visualización
        ax = sns.lineplot(x='n_try', y='Instrucciones', hue='Algoritmo', data=df, marker='o') # Agregar marcadores

        # Anotar cada punto con sus coordenadas
        for line in ax.lines:
            for x, y in zip(line.get_xdata(), line.get_ydata()):
                ax.annotate(f'({int(x)}, {int(y)})',  # Formatear las coordenadas
                    xy=(x, y),
                    xytext=(5, 5),  # Desplazamiento del texto
                    textcoords='offset points',
                    ha='left',  # Alineación horizontal
                    va='bottom',  # Alineación vertical
                    fontsize=8)  # Tamaño de la fuente

        plt.title('Número de Instrucciones vs. n_try', fontsize=14)  # Aumentar tamaño del título
        plt.xlabel('tamaño de n_try (* 10 millones)', fontsize=12)  # Aumentar tamaño de la etiqueta
        plt.ylabel('Número de Instrucciones (* 100 millones)', fontsize=12)  # Aumentar tamaño de la etiqueta
        plt.xticks(fontsize=10)  # Aumentar tamaño de los ticks en el eje x
        plt.yticks(fontsize=10)  # Aumentar tamaño de los ticks en el eje y
        plt.grid(True)
        plt.tight_layout()  # Ajustar el diseño para evitar cortes
        plt.savefig('instrucciones_vs_ntry.png')  # Guardar la gráfica como archivo PNG
        plt.show()
        

        # Formatear los datos para la tabla
        table_data = df[['Algoritmo', 'n_try', 'Tiempo', 'Instrucciones']].values.tolist()
        headers = ['Algoritmo', 'n_try', 'Tiempo', 'Instrucciones']

        # Crear la tabla con tabulate
        table = tabulate(table_data, headers=headers, tablefmt='grid')

        # Imprimir la tabla en la terminal
        print(table)


    # Redirigir la salida de cProfile a un archivo
    profiler = cProfile.Profile()
    profiler.enable()
    main()
    profiler.disable()

    # Guardar los resultados en un archivo, para evitar que saturan la terminal
    with open('profile_results.txt', 'w') as f:
        stats = pstats.Stats(profiler, stream=f)
        stats.sort_stats('cumulative')  # Ordenar por tiempo acumulativo
        stats.dump_stats('profile_data.prof') # Guardar los datos del perfil en un archivo

    print("Los resultados de cProfile se han guardado en profile_results.txt y profile_data.prof")
