#!/bin/bash
echo "Running Project B - Fixed Implementation Tests"
python test_fixed.py > log_fixed.txt 2>&1
python -c "import time; start=time.time(); exec(open('test_fixed.py').read()); print(f'Execution time: {time.time()-start:.4f}s')" > time_fixed.txt 2>&1
echo "Results saved to log_fixed.txt and time_fixed.txt"
cat log_fixed.txt
