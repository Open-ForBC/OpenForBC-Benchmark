echo "python3 user_interfaces/cli.py list-benchmarks"
python3 user_interfaces/cli.py list-benchmarks

echo "python3 user_interfaces/cli.py list-suites"
python3 user_interfaces/cli.py list-suites

echo "python3 user_interfaces/cli.py get-settings -b dummy_benchmark -s settings1.json"
python3 user_interfaces/cli.py get-settings -b dummy_benchmark -s settings1.json

echo "python3 user_interfaces/cli.py get-settings -b dummy_benchmark"
python3 user_interfaces/cli.py get-settings -b dummy_benchmark 

echo "python3 user_interfaces/cli.py run-benchmark -b dummy_benchmark -s settings1.json -v 1"
python3 user_interfaces/cli.py run-benchmark -b dummy_benchmark -s settings1.json -v 1 

echo "python3 user_interfaces/cli.py run-benchmark -b dummy_benchmark -s settings2.json -v 1"
python3 user_interfaces/cli.py run-benchmark -b dummy_benchmark -s settings2.json -v 1

echo "python3 user_interfaces/cli.py make-suite --name Mysuite -b dummy_benchmark -s settings1.json -f my_suite -d \"This is demo description.\""  
python3 user_interfaces/cli.py make-suite --name Mysuite -b dummy_benchmark -s settings1.json -f my_suite -d "This is demo description."  

echo "python3 user_interfaces/cli.py run-suite example_suite.json"
python3 user_interfaces/cli.py run-suite example_suite.json

echo "python3 user_interfaces/cli.py list-logs"
python3 user_interfaces/cli.py list-logs
