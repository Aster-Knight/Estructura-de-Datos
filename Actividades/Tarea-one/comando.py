def obtener_comando():
    #funcion que obtiene el comando del usuario, no es necesario que sea una funcion.
    return input("Ingrese comando (visitar, atras, adelante, historial, salir): ").lower()

def ejecutar_comando(navegador, comando, argumento=None):
    #funcion que ejecuta el comando del usuario, no es necesario que sea una funcion. Solo se hizo por pulcredad. 

    if comando == "visitar":
        navegador.visitar_pagina(argumento)
    elif comando == "atras":
        navegador.ir_atras()
    elif comando == "adelante":
        navegador.ir_adelante()
    elif comando == "historial":
        navegador.mostrar_historial()
    elif comando == "salir":
        return False  # Indica que se debe salir del bucle principal
    else:
        print("Comando no válido.")
    return True  # Indica que se debe continuar en el bucle principal
