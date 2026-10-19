#!/bin/bash

python3 marriage.py marriage_smalln.txt
python3 marriage.py marriage_largen.txt
python3 marriage.py marriage_repeatpref.txt
python3 marriage.py marriage_non.txt
python3 marriage.py marriage_badline.txt
python3 marriage.py marriage_inputs_1.txt
echo "----------10 inputs----------"
python3 marriage.py marriage_inputs_10.txt 1>/dev/null
echo "----------100 inputs----------"
python3 marriage.py marriage_inputs_100.txt 1>/dev/null
echo "----------1000 inputs----------"
python3 marriage.py marriage_inputs_1000.txt 1>/dev/null