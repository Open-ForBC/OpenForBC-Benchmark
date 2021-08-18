echo "Running dummy benchmark"

python3 user_interfaces/cli.py run-benchmark -b dummy_benchmark -s settings1.json -v 1 
python3 user_interfaces/cli.py run-benchmark -b dummy_benchmark -s settings2.json -v 1 

echo "list logs"
python3 user_interfaces/cli.py list-logs

echo "Running blender benchmark"

python3 user_interfaces/cli.py run-benchmark -b blender_benchmark -s settings1.json -v 1
python3 user_interfaces/cli.py run-benchmark -b blender_benchmark -s settings2.json -v 1

echo "list logs"
python3 user_interfaces/cli.py list-logs
