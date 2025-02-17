class Navegador:
    def __init__(self):
        #Inicializa el navegador con pilas vacías para el historial hacia atrás y hacia adelante.
        
        self.historial_atras = []
        self.historial_adelante = []
        self.pagina_actual = None

    def visitar_pagina(self, url):
        #Visita una nueva página, agregando la página actual al historial hacia atrás.
        
        if self.pagina_actual:
            self.historial_atras.append(self.pagina_actual)
        self.pagina_actual = url
        self.historial_adelante = []  # Limpiar historial al visitar nueva página. 
        self.mostrar_pagina_actual()

    def ir_atras(self):
        #Mueve la página actual al historial hacia adelante.
        
        if self.historial_atras:
            self.historial_adelante.append(self.pagina_actual)
            self.pagina_actual = self.historial_atras.pop()
            self.mostrar_pagina_actual()
        else:
            print("No hay páginas anteriores en el historial.")

    def ir_adelante(self):
       #Mueve la página actual al historial hacia atrás.
       
        if self.historial_adelante:
            self.historial_atras.append(self.pagina_actual)
            self.pagina_actual = self.historial_adelante.pop()
            self.mostrar_pagina_actual()
        else:
            print("No hay páginas siguientes en el historial.")

    def mostrar_pagina_actual(self):
       #Muestra la página actual en la consola.
      
        print(f"Página actual: {self.pagina_actual}")

    def mostrar_historial(self):
        #Muestra el historial de navegación en la consola.
        print("Historial hacia atrás:", self.historial_atras)
        print("Historial hacia adelante:", self.historial_adelante)

        


