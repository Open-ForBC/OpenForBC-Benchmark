
#/bin.bash

echo
echo "INSTALLING DEPENDENCIES"
pip3 install flake8 pytest
if [ -f requirements.txt ]; then pip3 install -r requirements.txt; fi

echo
echo "RUNNING FLAKE8"
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --max-complexity=10 --max-line-length=127 --statistics

echo
echo "RUNNING PYTEST"
pytest

echo
echo "RUNNING CLI TESTS"
bash ./bin/test_cli.sh

echo
echo "RUNNING BENCHMARK TESTS"
bash ./bin/test_benchmarks.sh

echo
echo "RUNNING SUITE TESTS"
bash ./bin/test_suites.sh
