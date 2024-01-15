#!/bin/bash

PORT = 8000

echo "Please select your Python version:"
echo "1. Python"
echo "2. Python3"
read -p "Enter the number (1/2): " py_version

case $py_version in
    1) python_cmd="python" ;;
    2) python_cmd="python3" ;;
    *) echo "Invalid option"; exit 1 ;;
esac

$python_cmd -m http.server $PORT