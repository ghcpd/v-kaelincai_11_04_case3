#!/bin/bash
echo "Running Project A - Buggy Implementation Tests"
python test_buggy.py > log_buggy.txt 2>&1
python -c "import time; start=time.time(); exec(open('test_buggy.py').read()); print(f'Execution time: {time.time()-start:.4f}s')" > time_buggy.txt 2>&1
echo "Results saved to log_buggy.txt and time_buggy.txt"
cat log_buggy.txt
