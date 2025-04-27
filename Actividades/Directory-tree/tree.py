'''
A simple tree structure for storing a directory snapshot.
'''

class Node():
    def __init__(self, name: str):
        self.name = name


class Tree(): 
    def __init__(self, name: str):
        self.name = name
        self.children = []

    def insert_child(self, object: any):
        self.children.append(object)

    def get_children(self):
        return self.children
