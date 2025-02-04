arr=[1,2,3,4,5,6,7,8,9,10]
key=7

for i in range(len(arr)):
    if arr[i]==key:
        print("Elemento encontrado en la posicion: ",i)
        break
else:
    print("Elemento no encontrado")
