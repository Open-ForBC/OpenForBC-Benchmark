#include <iostream>
#include <stdlib.h>
#include <time.h>
#include <chrono>

using namespace std;

class Timer
{
public:
    Timer()
    {
        m_StartTimepoint = std::chrono::high_resolution_clock::now(); //gets the current time at a specific time point
    }

    ~Timer() //when the object is destoried the timer stops
    {
        Stop();
    }

    void Stop()
    {
        auto endTimepoint = std::chrono::high_resolution_clock::now();

        auto start = std::chrono::time_point_cast<std::chrono::milliseconds>(m_StartTimepoint).time_since_epoch().count();
        auto stop = std::chrono::time_point_cast<std::chrono::milliseconds>(endTimepoint).time_since_epoch().count();

        auto duration = stop - start;
        double s = duration*0.001;

        std::cout<<duration<<"ms("<<s<<"s)\n";
    }
private:
    std::chrono::time_point<std::chrono::high_resolution_clock>m_StartTimepoint;
};

void MatrixAllocation( double **m1, double **m2, int r1, int c1, int r2, int c2){

}

void matmul(int dim1, int dim2)
{  
    //Matrices definition
    /*double m1[dim1][dim2]; 
    double m2[dim2][dim1];*/

    /*dynamic allocation of matrixes*/
    double **m1 = new double*[dim1];
    double **m2 = new double*[dim2];

    if (m1 == NULL || m2 == NULL) {
        cout <<"error allocating rows"<<endl;
    }
    for (int i = 0; i < dim1; i++) {
        m1[i] = new double[dim2];
        if (m1[i] == NULL){
            cout <<"error allocating col"<<endl;
        }
    }

    for (int i = 0; i < dim2; i++) {
        m2[i] = new double[dim1];
            if (m2[i] == NULL){
                 cout <<"error allocating col"<<endl;
        }
    }
    cout <<"matrixes allocated"<<endl;
    //Matrices filling
    cout <<"sto per riempire la matrice"<<endl;
    for(int i=0; i<dim1; i++)
    {
        for(int j=0; j<dim2; j++)
        {
            m1[i][j] = rand();
            m2[j][i] = rand();
        }
    }

    // double mul[dim2][dim2];
    double **mul = new double*[dim1];
    for (int i = 0; i < dim1; i++) {
        mul[i] = new double[dim1]; 
    }
    cout <<"matrix mul allocated"<<endl;

    //Matrices multiplication

    /*mul initialization to 0*/
    for (int i = 0; i < dim1; i++) {
        for(int j = 0; j < dim1; j++) {
            mul[i][j] = 0;
        }
    }

    cout <<"mul matrix initialization done"<<endl;
    for(int i=0; i<dim1; i++)
    {
        for(int j=0; j<dim1; j++)
        {
            for(int k=0; k<dim2; k++)
            {
                mul[i][j] += m1[i][k]*m2[k][j];
            }
            
        }
    }
    /*free memory*/
    cout <<"tutto ok, ora libero memoria"<<endl;
    if (dim1) {
        delete [] m1[0];
    }
    delete [] m1;
    if (dim2) {
        delete [] m2[0];
    }
    delete [] m2;

    if (dim1) {
        delete [] mul[0];
    }
    delete [] mul;
    
}

int main(int argc, char* argv[])
{
    srand(time(0));
    //Matrices dimensions take from command line
    int dim1 = atoi(argv[1]);
    int dim2 = atoi(argv[2]);

    {
        Timer timer;
        matmul(dim1, dim2);
        std::cout<<"The product has been performed in: ";
    
    }

    return 0;
}