#!/usr/bin/env bash

apt-get update

# Check if a token argument was provided
if [ -z "$1" ]; then
    echo "Error: No GitHub token provided."
    exit 1
fi

echo "Usage: $0 with token $1"
GITHUB_TOKEN=$1

# Check if Python is installed
PYTHON_VERSION="3.12.6"
PYTHON_BIN="/usr/local/bin/python${PYTHON_VERSION%.*}"

if python3 --version &>/dev/null; then
    echo "Python is already installed."
else
    echo "Python not found. Installing Python..."
    wget "https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz"
    tar xvf Python-${PYTHON_VERSION}.tgz
    cd Python-${PYTHON_VERSION}/
    ./configure --enable-optimizations
    make altinstall
    ${PYTHON_BIN} -m ensurepip --default-pip
    ${PYTHON_BIN} -m pip install --upgrade pip setuptools wheel
    cd ..
    rm -rf Python-${PYTHON_VERSION}*
fi

# Check if Git is installed
if git --version &>/dev/null; then
    echo "Git is already installed."
else
    echo "Git not found. Installing Git..."
    apt-get install -y git
fi

# Check if Ansible is installed
if ansible --version &>/dev/null; then
    echo "Ansible is already installed."
else
    echo "Ansible not found. Installing Ansible Core..."
    apt-get install -y software-properties-common
    add-apt-repository --yes --update ppa:ansible/ansible
    apt-get install -y ansible-core
fi

# Clone toolkit-installer repository using the provided token
echo "Cloning toolkit-installer repository..."
git clone https://${GITHUB_TOKEN}@github.com/6G-SANDBOX/toolkit-installer.git

cd toolkit-installer || { echo "Repository not found"; exit 1; }

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install required libraries
echo "Installing libraries..."
pip install -r requirements.txt

# Start toolkit-installer
echo "Starting toolkit-installer..."
python3 src/toolkit_installer.py

# Deactivate virtual environment
deactivate