#include <stdlib.h>
#include <time.h>

#include <chrono>
#include <iostream>

using namespace std;

class Timer {
 public:
  Timer() {
    m_StartTimepoint =
        std::chrono::high_resolution_clock::now();  // gets the current time at
                                                    // a specific time point
  }

  // when the object is destroied the timer stops
  // ~Timer()
  // {
  //     Stop();
  // }

  void Stop() {
    auto endTimepoint = std::chrono::high_resolution_clock::now();

    auto start = std::chrono::time_point_cast<std::chrono::milliseconds>(
                     m_StartTimepoint)
                     .time_since_epoch()
                     .count();
    auto stop =
        std::chrono::time_point_cast<std::chrono::milliseconds>(endTimepoint)
            .time_since_epoch()
            .count();

    auto duration = stop - start;
    double s = duration * 0.001;

    std::cout << duration << "ms(" << s << "s)\n";
  }

 private:
  std::chrono::time_point<std::chrono::high_resolution_clock> m_StartTimepoint;
};

void mat_alloc(int dim1, int dim2, double **m1, double **m2) {
  /*dynamic allocation of matrices*/

  if (m1 == NULL || m2 == NULL) {
    cout << "error allocating rows" << endl;
  }
  for (int i = 0; i < dim1; i++) {
    m1[i] = new double[dim2];
    if (m1[i] == NULL) {
      cout << "error allocating col" << endl;
    }
  }

  for (int i = 0; i < dim2; i++) {
    m2[i] = new double[dim1];
    if (m2[i] == NULL) {
      cout << "error allocating col" << endl;
    }
  }

  for (int i = 0; i < dim1; i++) {
    for (int j = 0; j < dim2; j++) {
      m1[i][j] = rand();
      m2[j][i] = rand();
    }
  }
}

void matmul(int dim1, int dim2, double **m1, double **m2) {
  double **mul = new double *[dim1];
  for (int i = 0; i < dim1; i++) {
    mul[i] = new double[dim1];
  }

  // Matrices multiplication

  /*mul initialization to 0*/
  for (int i = 0; i < dim1; i++) {
    for (int j = 0; j < dim1; j++) {
      mul[i][j] = 0;
    }
  }

  // This matrix multiplication algorithm is not so efficient
  for (int i = 0; i < dim1; i++) {
    for (int j = 0; j < dim1; j++) {
      for (int k = 0; k < dim2; k++) {
        mul[i][j] += m1[i][k] * m2[k][j];
      }
    }
  }

  // Free memory
  if (dim1) {
    delete[] mul[0];
  }
  delete[] mul;
}

int main(int argc, char *argv[]) {
  srand(time(0));
  // Matrices dimensions taken from command line
  int dim1 = atoi(argv[1]);
  int dim2 = atoi(argv[2]);
  // Matrices declaration
  double **m1 = new double *[dim1];
  double **m2 = new double *[dim2];

  mat_alloc(dim1, dim2, m1, m2);

  Timer timer;
  matmul(dim1, dim2, m1, m2);
  timer.Stop();
  std::cout << "Product computation time: ";

  // Free memory
  if (dim1) {
    delete[] m1[0];
  }
  delete[] m1;
  if (dim2) {
    delete[] m2[0];
  }
  delete[] m2;

  return 0;
}