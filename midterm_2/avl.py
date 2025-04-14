class Node:

    def __init__(self, data: int):

        self.data = data
        self.left_child = None
        self.right_child = None
        self.height = 1  # La altura de un nodo hoja es 1


    def __repr__(self):
        return '({})'.format(self.data)


class AVLTree:

    def __init__(self):
        self.root = None


    def get_height(self, node: Node) -> int:
        if not node:
            return 0
        return node.height


    def update_height(self, node: Node):
        node.height = 1 + max(self.get_height(node.left_child), self.get_height(node.right_child))


    def get_balance(self, node: Node) -> int:
        if not node:
            return 0
        return self.get_height(node.left_child) - self.get_height(node.right_child)


    def rotate_right(self, y: Node) -> Node:
        x = y.left_child
        T2 = x.right_child

        # Realizar la rotación
        x.right_child = y
        y.left_child = T2

        # Actualizar alturas después de la rotación
        self.update_height(y)
        self.update_height(x)

        # Devolver la nueva raíz
        return x


    def rotate_left(self, x: Node) -> Node:
        y = x.right_child
        T2 = y.left_child

        # Realizar la rotación
        y.left_child = x
        x.right_child = T2

        # Actualizar alturas después de la rotación
        self.update_height(x)
        self.update_height(y)

        # Devolver la nueva raíz
        return y


    def traverse(self, subtree: Node):
        print(subtree)

        if subtree.left_child is not None:
            self.traverse(subtree.left_child)

        if subtree.right_child is not None:
            self.traverse(subtree.right_child)


    def insert(self, value: int):
        if self.root is None:
            self.root = Node(value)
        else:
            self.root = self._insert(value, self.root)


    def _insert(self, value: int, subtree: Node) -> Node:
        # Paso 1: Inserción BST estándar
        if not subtree:
            return Node(value)
        elif value < subtree.data:
            subtree.left_child = self._insert(value, subtree.left_child)
        elif value > subtree.data:
            subtree.right_child = self._insert(value, subtree.right_child)
        else: # Valores duplicados no permitidos en BST
            print('Value already exists in tree...')
            return subtree

        # Paso 2: Actualizar la altura del nodo actual
        self.update_height(subtree)

        # Paso 3: Obtener el factor de balance para verificar si este nodo se desbalanceó
        balance = self.get_balance(subtree)

        # Paso 4: Si el nodo está desbalanceado, entonces hay 4 casos

        # Caso 1: Izquierda Izquierda
        if balance > 1 and value < subtree.left_child.data:
            return self.rotate_right(subtree)

        # Caso 2: Derecha Derecha
        if balance < -1 and value > subtree.right_child.data:
            return self.rotate_left(subtree)

        # Caso 3: Izquierda Derecha
        if balance > 1 and value > subtree.left_child.data:
            subtree.left_child = self.rotate_left(subtree.left_child)
            return self.rotate_right(subtree)

        # Caso 4: Derecha Izquierda
        if balance < -1 and value < subtree.right_child.data:
            subtree.right_child = self.rotate_right(subtree.right_child)
            return self.rotate_left(subtree)

        # Retornar el nodo (sin cambios si no se requiere balanceo)
        return subtree


    def search(self, key: int) -> bool:
        if self.root is None:
            return False
        else:
            return self._search(key, self.root)


    def _search(self, key: int, subtree: Node) -> bool:
        """
        Realiza la búsqueda de forma recursiva en el subárbol.

        Args:
            key (int): El valor a buscar.
            subtree (Node): La raíz del subárbol donde se buscará.

        Returns:
            bool: True si el valor se encuentra en el subárbol, False de lo contrario.
        """
        if key == subtree.data:
            return True

        elif (key < subtree.data) and (subtree.left_child is not None):
            return self._search(key, subtree.left_child)

        elif (key > subtree.data) and (subtree.right_child is not None):
            return self._search(key, subtree.right_child)

        else:
            return False


    def find_min(self, subtree: Node) -> int:
        """
        Encuentra el nodo con el valor mínimo en el subárbol.

        Args:
            subtree (Node): La raíz del subárbol donde se buscará el mínimo.

        Returns:
            int: El valor mínimo encontrado en el subárbol.
        """
        while subtree.left_child is not None:
            subtree = subtree.left_child
        return subtree


    def find_max(self, subtree: Node) -> int:
        """
        Encuentra el nodo con el valor máximo en el subárbol.

        Args:
            subtree (Node): La raíz del subárbol donde se buscará el máximo.

        Returns:
            int: El valor máximo encontrado en el subárbol.
        """
        while subtree.right_child is not None:
            subtree = subtree.right_child
        return subtree


    def print_pretty(self):
        """
        Imprime el árbol AVL de una manera visualmente atractiva.
        """
        if self.root is not None:
            lines, *_ = self._build_tree_string(self.root)
            print("\n" + "\n".join(line.rstrip() for line in lines))
        else:
            print("\nEmpty tree...")


    def _build_tree_string(self, node: Node):
        """
        Función auxiliar recursiva para construir la representación en cadena del árbol.

        Args:
            node (Node): El nodo actual a procesar.

        Returns:
            tuple: Líneas de la representación del árbol, ancho, alto y punto medio.
        """
        if node.right_child is None and node.left_child is None:
            line = str(node.data)
            width = len(line)
            height = 1
            middle = width // 2
            return [line], width, height, middle

        if node.right_child is None:
            lines, n, p, x = self._build_tree_string(node.left_child)
            s = str(node.data)
            u = len(s)
            first_line = (x + 1) * ' ' + (n - x - 1) * '_' + s
            second_line = x * ' ' + '/' + (n - x - 1 + u) * ' '
            shifted_lines = [line + u * ' ' for line in lines]
            return [first_line, second_line] + shifted_lines, n + u, p + 2, n + u // 2

        if node.left_child is None:
            lines, n, p, x = self._build_tree_string(node.right_child)
            s = str(node.data)
            u = len(s)
            first_line = s + x * '_' + (n - x) * ' '
            second_line = (u + x) * ' ' + '\\' + (n - x - 1) * ' '
            shifted_lines = [u * ' ' + line for line in lines]
            return [first_line, second_line] + shifted_lines, n + u, p + 2, u // 2

        left, n, p, x = self._build_tree_string(node.left_child)
        right, m, q, y = self._build_tree_string(node.right_child)
        s = str(node.data)
        u = len(s)
        first_line = (x + 1) * ' ' + (n - x - 1) * '_' + s + y * '_' + (m - y) * ' '
        second_line = x * ' ' + '/' + (n - x - 1 + u + y) * ' ' + '\\' + (m - y - 1) * ' '
        if p < q:
            left += [n * ' '] * (q - p)
        elif q < p:
            right += [m * ' '] * (p - q)
        zipped_lines = zip(left, right)
        lines = [first_line, second_line] + [a + u * ' ' + b for a, b in zipped_lines]
        return lines, n + m + u, max(p, q) + 2, n + u // 2


    def delete(self, value: int):
        """
        Elimina un valor del árbol AVL.

        Args:
            value (int): El valor a eliminar.
        """
        if self.root is not None:
            self.root = self._delete(value, self.root)
        else:
            return('Tree is empty...')


    def _delete(self, value: int, subtree: Node) -> Node:
        """
        Elimina un valor de forma recursiva del subárbol y balancea el árbol AVL.

        Args:
            value (int): El valor a eliminar.
            subtree (Node): La raíz del subárbol del cual se eliminará el valor.

        Returns:
            Node: La raíz del subárbol modificado (puede cambiar debido al balanceo).
        """
        # Paso 1: Realizar la eliminación BST estándar
        if not subtree:
            return None

        if value < subtree.data:
            subtree.left_child = self._delete(value, subtree.left_child)
        elif value > subtree.data:
            subtree.right_child = self._delete(value, subtree.right_child)
        else:
            # Nodo con el valor a eliminar encontrado
            if subtree.left_child is None:
                return subtree.right_child
            elif subtree.right_child is None:
                return subtree.left_child

            # Nodo con dos hijos: obtener el sucesor inorder (mínimo en el subárbol derecho)
            successor = self.find_min(subtree.right_child)
            subtree.data = successor.data
            subtree.right_child = self._delete(successor.data, subtree.right_child)

        if not subtree: # Nodo fue eliminado y es None
            return None

        # Paso 2: Actualizar la altura del nodo actual
        self.update_height(subtree)

        # Paso 3: Obtener el factor de balance para verificar si este nodo se desbalanceó
        balance = self.get_balance(subtree)

        # Paso 4: Si el nodo está desbalanceado, entonces hay 4 casos

        # Caso 1: Izquierda Izquierda
        if balance > 1 and self.get_balance(subtree.left_child) >= 0:
            return self.rotate_right(subtree)

        # Caso 2: Derecha Derecha
        if balance < -1 and self.get_balance(subtree.right_child) <= 0:
            return self.rotate_left(subtree)

        # Caso 3: Izquierda Derecha
        if balance > 1 and self.get_balance(subtree.left_child) < 0:
            subtree.left_child = self.rotate_left(subtree.left_child)
            return self.rotate_right(subtree)

        # Caso 4: Derecha Izquierda
        if balance < -1 and self.get_balance(subtree.right_child) > 0:
            subtree.right_child = self.rotate_right(subtree.right_child)
            return self.rotate_left(subtree)

        return subtree


# --- Modulo de pruebas ---
if __name__ == '__main__':
    # Paso 1: Crear un árbol AVL
    avl_tree = AVLTree()
    print("Arbol AVL creado.\n")

    # Paso 2: Insertar valores en el árbol AVL
    values_to_insert = [50, 30, 20, 40, 70, 60, 80, 90, 10, 5, 65, 75, 85, 95]
    print("Insertando valores en el arbol AVL:")
    for value in values_to_insert:
        avl_tree.insert(value)
        print(f"Insertado {value}")
        # Paso 3: Imprimir el árbol después de cada inserción para visualizar el balanceo
        avl_tree.print_pretty()
        print("-" * 30)

    print("\nArbol AVL despues de todas las inserciones:")
    avl_tree.print_pretty()

    # Paso 4: Buscar valores en el árbol
    print("\nBuscando valores en el arbol:")
    search_values = [40, 65, 100]
    for value in search_values:
        found = avl_tree.search(value)
        print(f"¿El valor {value} se encuentra en el arbol?: {found}")

    # Paso 5: Encontrar el mínimo y el máximo
    min_val = avl_tree.find_min(avl_tree.root)
    max_val = avl_tree.find_max(avl_tree.root)
    print(f"\nValor minimo en el arbol: {min_val}")
    print(f"Valor maximo en el arbol: {max_val}")

    # Paso 6: Eliminar valores del árbol
    values_to_delete = [30, 80, 50]
    print("\nEliminando valores del arbol AVL:")
    for value in values_to_delete:
        print(f"Eliminando {value}")
        avl_tree.delete(value)
        # Paso 7: Imprimir el árbol después de cada eliminación para visualizar el balanceo
        avl_tree.print_pretty()
        print("-" * 30)

    print("\nArbol AVL despues de todas las eliminaciones:")
    avl_tree.print_pretty()# Espacio para inciso 2.1
