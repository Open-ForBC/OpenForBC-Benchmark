echo "Running dummy benchmark settings 1"

python3 user_interfaces/cli.py run-benchmark -b dummy_benchmark -s settings1.json -v 1 

echo ""
echo "Running dummy benchmark settings 2"
python3 user_interfaces/cli.py run-benchmark -b dummy_benchmark -s settings2.json -v 1 

echo ""
echo "list logs"
python3 user_interfaces/cli.py list-logs

echo ""
echo "Running blender benchmark settings 1"
echo ""
python3 user_interfaces/cli.py run-benchmark -b blender_benchmark -s settings1.json -v 1

echo ""
echo "Running blender benchmark settings 2"
echo ""
python3 user_interfaces/cli.py run-benchmark -b blender_benchmark -s settings2.json -v 1

echo ""
echo "list logs"
python3 user_interfaces/cli.py list-logs
