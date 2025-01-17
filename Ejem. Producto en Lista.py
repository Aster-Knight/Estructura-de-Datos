arr = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
key_product = 200
def find_product(arr, key_product):
    for i in range(len(arr)):
        for j in range(len(arr)):
            if arr[i]*arr[j] == key_product:
                print("Elemento encontrado en la posicion: ", i+1, j+1)
            
            
find_product(arr, key_product)