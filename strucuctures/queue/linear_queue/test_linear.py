'''
Linear Queue testing.
'''


from linear_queue import LinearQueue


# Queue instance
queue = LinearQueue(5)
print(queue)

# Enqueues
queue.enqueue('A')
print(queue)
queue.enqueue('B')
print(queue)
queue.enqueue('C')
print(queue)
queue.enqueue('D')
print(queue)
queue.enqueue('E')
print(queue)
queue.enqueue('F') # Queue Overflow
queue.enqueue('G') # Queue Overflow

# Dequeues
returned_val = queue.dequeue()
print(f'Dequeued val: {returned_val}')
print(queue)
queue.dequeue()
print(queue)
queue.dequeue()
print(queue)
queue.dequeue()
print(queue)
queue.dequeue()
print(queue)
queue.dequeue() # Queue Underflow (2nd scenario)

queue.enqueue('L') # Linear queue caveat... 

queue_2 = LinearQueue(3)
print(queue_2)
queue_2.dequeue() # Queue Underflow (1st scenario)
