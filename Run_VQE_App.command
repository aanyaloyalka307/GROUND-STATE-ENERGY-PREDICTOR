#!/bin/bash
# Double-click this file to launch the VQE Experiment app.
# It automatically installs any missing packages the first time you run it.

# Move into the folder this file lives in, no matter where it's double-clicked from.
cd "$(dirname "$0")"

echo "============================================"
echo " VQE Experiment - starting up..."
echo "============================================"
echo ""

# Find a working python3
if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
else
    echo "ERROR: Python 3 was not found on this computer."
    echo "Please install it from https://www.python.org/downloads/ and try again."
    echo ""
    read -p "Press Enter to close this window..."
    exit 1
fi

# Make sure the required packages are installed (fast no-op if already present)
echo "Checking required packages (this only takes time the first run)..."
"$PYTHON" -c "import numpy, scipy, matplotlib, qiskit, qiskit_aer, qiskit_ibm_runtime" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required packages, please wait..."
    "$PYTHON" -m pip install --user numpy scipy matplotlib qiskit qiskit-aer qiskit-ibm-runtime
    if [ $? -ne 0 ]; then
        echo ""
        echo "ERROR: Failed to install required packages."
        echo "Check your internet connection and try again."
        echo ""
        read -p "Press Enter to close this window..."
        exit 1
    fi
fi

echo ""
echo "Launching the app window now..."
"$PYTHON" vqe_code.py

echo ""
echo "The app window was closed."
read -p "Press Enter to close this window..."
