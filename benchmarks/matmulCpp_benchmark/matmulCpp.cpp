#include <iostream>
#include <stdlib.h>
#include <time.h>

#define dim1 8
#define dim2 10

int main(){

    srand(time(0))

    int m1[dim1][dim2];
    int m2[dim2][dim1];

    for (int i=0; i<dim1; i++){
        for (int j=0; j<dim2; j++){

            m1[i][j] = rand();
            std::cout<<m1[i][j]<<'\t';
        }
        std::cout<<'\n';
    }

    for (int j=0; i<dim1; i++){
        for (int i=0; j<dim2; j++){

            m1[j][i] = rand();
            std::cout<<m1[i][j]<<'\t';
        }
        std::cout<<'\n';
    }

    return 0;
}