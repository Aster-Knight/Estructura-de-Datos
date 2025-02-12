from stack import Stack
import time
from memory_profiler import profile



start_time = time.time()

@profile
def invert_list(op_list:list, verbose=False):


    s= Stack(len(op_list))
    new_list = []

    print(f'\nLista original: {op_list}')
    print('\n', s)


    # Llenar el stack con la lista original
    for element in op_list:
        s.push(element)

    print('\n', s)

    
    #poblar nueva lista
    while s.peek() != 'Stack underflow':
        popped = s.pop()
        new_list.append(popped)

    print(f'\nNew list: {new_list}')
    

end_time = time.time()

print(f'\nTiempo de ejecución: {end_time - start_time} segundos')
    
    
trylist = ['A', 'B', 'C', 'D', 'F', 'G']
invert_list(trylist, verbose=True)

