'''
Inciso 2, encontrar con la estructura selecciónada un n que que intancie e inserte elementos. De tal manera que alcance un tiempo de ejecución de 5 segundos.
'''


import time
import cProfile

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
    
    def search(self, key: str) -> int | None:
        """
        Busca la posición de la clave (key) en la pila.
        Retorna la distancia desde la cima (0 si está en la cima) o None si no se encuentra.
        """
        for i in range(self.top, -1, -1):  # Itera desde la cima hacia la base
            if self.elements[i] == key:
                return self.top - i  # Calcula la distancia desde la cima
        return None  # Retorna None si no se encuentra la clave

def llenar_stack_con_ceros(stack):
    """
    Llena la pila con ceros.
    """
    for _ in range(stack.max):
        stack.push("0")

def medir_tiempo_ejecucion(n_try):
    """
    Mide el tiempo de ejecución de llenar la pila con ceros.
    """
    stack = Stack(n_try)

    inicio = time.time()
    llenar_stack_con_ceros(stack)
    fin = time.time()
    tiempo_ejecucion = fin - inicio

    print(f"n_try = {n_try}, Tiempo de ejecución: {tiempo_ejecucion:.4f} segundos")

    return tiempo_ejecucion

if __name__ == "__main__":
    def main():
        n_try = 10999590*2  # Define el valor de n_try aquí

        n1=1*n_try
        n2=2*n_try
        n3=3*n_try
        n4=4*n_try
        n5=5*n_try
        prueba1 = medir_tiempo_ejecucion(n1)
        print(f"\nTiempo de ejecución total 1 con n_try = {n1}: {prueba1:.4f} segundos")
        prueba2 = medir_tiempo_ejecucion(n2)
        print(f"\nTiempo de ejecución total 2 con n_try = {n2}: {prueba2:.4f} segundos")
        prueba3 = medir_tiempo_ejecucion(n3)
        print(f"\nTiempo de ejecución total 3 con n_try = {n3}: {prueba3:.4f} segundos")
        prueba4 = medir_tiempo_ejecucion(n4)
        print(f"\nTiempo de ejecución total 4 con n_try = {n4}: {prueba4:.4f} segundos")
        prueba5 = medir_tiempo_ejecucion(n5)
        print(f"\nTiempo de ejecución total 5 con n_try = {n5}: {prueba5:.4f} segundos")


    cProfile.run('main()')




