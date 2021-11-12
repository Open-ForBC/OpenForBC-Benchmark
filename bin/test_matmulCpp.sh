echo "Running matmulCpp benchmark settings with matrix dimensions 57x89"

python3 user_interfaces/cli.py run-benchmark -b matmulCpp_benchmark -s Matrix_57x89.json -v 1

echo ""
echo "list logs"
python3 user_interfaces/cli.py list-logs