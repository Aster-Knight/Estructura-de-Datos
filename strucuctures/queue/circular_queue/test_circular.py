'''
Circular Queue testing.
'''


from circular_queue import CircularQueue


# Queue instance
queue = CircularQueue(5)
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

# Dequeues
queue.dequeue()
print(queue)
queue.dequeue()
print(queue)

# Enqueues
queue.enqueue('F')
print(queue)
queue.enqueue('G')
print(queue)
queue.enqueue('H')
print(queue)
