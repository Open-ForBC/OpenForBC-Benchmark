echo "Running dummy benchmark settings 1"

python3 user_interfaces/cli.py run-benchmark -b dummy_benchmark -s settings1.json -v 1 

echo ""
echo "Running dummy benchmark settings 2"
python3 user_interfaces/cli.py run-benchmark -b dummy_benchmark -s settings2.json -v 1 

echo ""
echo "list logs"
python3 user_interfaces/cli.py list-logs

echo ""
echo "Installing atscenc benchmark"
echo ""
python3 user_interfaces/cli.py install-phoronix -b astcenc -v 1.2.0

echo ""
echo "Running atscenc benchmark"
echo ""
python3 user_interfaces/cli.py run-benchmark -b phoronix-astcenc-1.2.0

echo ""
echo "list logs"
python3 user_interfaces/cli.py list-logs

