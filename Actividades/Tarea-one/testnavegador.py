from memory_profiler import profile

@profile
def main():
    
    from navegador import Navegador
    from comando import obtener_comando, ejecutar_comando

    navegador = Navegador()
    continuar = True

    while continuar:
        comando = obtener_comando()
        if comando == "visitar":
            url = input("Ingrese la URL a visitar: ")
            continuar = ejecutar_comando(navegador, comando, url)
        else:
            continuar = ejecutar_comando(navegador, comando)

    print("Estiamdo usuario, gracias por usar nuestro navegador.")

if __name__ == "__main__":
    main()

