'''
Circular Queue implementation.
'''


class CircularQueue:
    def __init__(self, size: int):
        self.max = size
        self.elements = [None] * size
        self.front = -1
        self.rear = -1

    def __repr__(self) -> str:
        return f'Queue: {self.elements} | F: {self.front} | R: {self.rear}'

    def enqueue(self, val: str) -> None:
        if (self.front == 0 and self.rear == self.max - 1) or (self.rear == self.front - 1):
            print('Queue overflow...')
            return None 
    
        if self.front == -1 and self.rear == -1:
            self.front = 0
            self.rear = 0
        elif self.rear == self.max - 1 and self.front != 0:
            self.rear = 0
        else:
            self.rear += 1

        self.elements[self.rear] = val
        
    def dequeue(self) -> str:
        if self.front == -1:
            print('Queue Underflow...')
            return None

        val = self.elements[self.front]
        self.elements[self.front] = None

        if self.front == self.rear:
            self.front = -1
            self.rear = -1
        else:
            if self.front == self.max - 1:
                self.front = 0
            else:
                self.front += 1

        return val
