echo "Running matmul benchmark settings with matrix dimensions 57x89 with GPU"
python3 user_interfaces/cli.py run-benchmark -b matmul_benchmark -s Matrix_57x89_GPU.json -v 1 

echo ""
echo "list logs"
python3 user_interfaces/cli.py list-logs