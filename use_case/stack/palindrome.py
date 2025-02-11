'''
Varificar sin un texto es palíndromo utilizando stacks
'''

from stack import Stack
from memory_profiler import profile

@profile
def is_palindrome(text) -> bool:
    stack_size = len(text) //2
    print("\n stack size:", stack_size)

    s = Stack(stack_size)
    #print(s)

    first_half = text[:stack_size]
    #print(first_half)

    #Llenar el stack con la primera mitad del texto
    for char in first_half:
        s.push(char)
    print(s)

    #vaciar el stack y comparar con la segunda mitad del texto
    second_half = text[-stack_size:]
    #print(second_half)

    for char in second_half:
        popped = s.pop()
        if char != popped:
            return False
        
    return True






print(is_palindrome('somosonosomos'))
print(is_palindrome('helloworld'))
print(is_palindrome('somos'))
print(is_palindrome(' '))
print(is_palindrome(''))

