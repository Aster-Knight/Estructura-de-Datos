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
            print('Underflow')
            return None
        
        val = self.elements[self.top]
        self.elements[self.top] = None 
        self.top -= 1
        return val
    
    def peek(self) -> any:
        if self.top == -1:
            return 'Stack underflow'

        return self.elements[self.top]