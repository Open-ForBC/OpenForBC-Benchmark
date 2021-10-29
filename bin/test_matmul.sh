echo "Running matmul benchmark settings with matrix dimensions 57x89 with CPU"
python3 user_interfaces/cli.py run-benchmark -b matmul_benchmark -s Matrix_57x89_CPU.json -v 1 

echo ""
echo "Running matmul benchmark settings with matrix dimensions 57x89 with GPU"
python3 user_interfaces/cli.py run-benchmark -b matmul_benchmark -s Matrix_57x89_GPU.json -v 1 

echo ""
echo "Running matmul benchmark settings with matrix dimensions 557x489 with CPU"
python3 user_interfaces/cli.py run-benchmark -b matmul_benchmark -s Matrix_557x489_CPU.json -v 1

echo ""
echo "Running matmul benchmark settings with matrix dimensions 557x489 with GPU"
python3 user_interfaces/cli.py run-benchmark -b matmul_benchmark -s Matrix_557x489_GPU.json -v 1 

echo ""
echo "Running matmul benchmark settings with matrix dimensions 700x800 with CPU"
python3 user_interfaces/cli.py run-benchmark -b matmul_benchmark -s Matrix_700x800_CPU.json -v 1 

echo ""
echo "Running matmul benchmark settings with matrix dimensions 700x800 with GPU"
python3 user_interfaces/cli.py run-benchmark -b matmul_benchmark -s Matrix_700x800_GPU.json -v 1 

echo ""
echo "list logs"
python3 user_interfaces/cli.py list-logs