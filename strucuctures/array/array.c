#include <stdio.h>

int main(){
int arr[6] = {1, 2, 3, 4, 5};
int i; 

printf("El puntero i esta en la direcci%cn %d", 132, (int) &i);

for (i = 0; i < 5; i++) {
printf("\nEl elemento %d esta guardado en la direcci%cn %d", arr[i], 162, (int) &arr[i]);
}
}