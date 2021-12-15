#include <chrono>
#include <cstdlib>
#include <ctime>
#include <iostream>

using std::endl;
using std::cout;

void mat_alloc(int dim1, int dim2, double **m1, double **m2) {
  /*dynamic allocation of matrices*/

  if (m1 == nullptr || m2 == nullptr) {
    cout << "error allocating rows" << endl;
  }
  for (int i = 0; i < dim1; i++) {
    m1[i] = new double[dim2];
    if (m1[i] == nullptr) {
      cout << "error allocating col" << endl;
    }
  }

  for (int i = 0; i < dim2; i++) {
    m2[i] = new double[dim1];
    if (m2[i] == nullptr) {
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
  auto **mul = new double *[dim1];
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
  using std::chrono::duration;
  using std::chrono::high_resolution_clock;

  if (argc < 2) {
    cout << "Usage: matmulCpp dim0 dim2" << endl
         << "Arguments:" << endl
         << "\tdim0: First (square) matrix dimension" << endl
         << "\tdim1: Second (square) matrix dimension" << endl;
    exit(0);
  }

  srand(time(nullptr));
  // Matrices dimensions taken from command line
  int dim1 = atoi(argv[1]);
  int dim2 = atoi(argv[2]);
  // Matrices declaration
  auto **m1 = new double *[dim1];
  auto **m2 = new double *[dim2];

  mat_alloc(dim1, dim2, m1, m2);

  auto time_start = high_resolution_clock::now();
  matmul(dim1, dim2, m1, m2);
  auto time_end = high_resolution_clock::now();

  duration<double> time = time_end - time_start;

  cout::fixed << "Matrix multiplication time: " << std::fixed << time.count() << " s" << endl;
 
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
