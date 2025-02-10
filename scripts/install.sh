#!/usr/bin/env bash

export DEBIAN_FRONTEND=noninteractive

echo "============================================="
echo "              GLOBAL VARIABLES               "
echo "============================================="
PYTHON_VERSION="3.13"
PYTHON_BIN="python${PYTHON_VERSION}"
UV_PATH="/opt/uv"
UV_BIN="${UV_PATH}/uv"
TOOLKIT_INSTALLER_FOLDER="/opt/toolkit-installer"

echo "========== Starting Pre-Checks for Script Execution =========="

echo "Checking if the script is being executed as root..."
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root. Please use 'sudo' or switch to the root user."
    exit 1
else
    echo "Script is running as root."
fi

echo "Detecting Ubuntu version..."
echo "Detected Ubuntu version: ${UBUNTU_VERSION}"
if [[ "${UBUNTU_VERSION}" != "22.04" && "${UBUNTU_VERSION}" != "24.04" ]]; then
    echo "Unsupported Ubuntu version: ${UBUNTU_VERSION}. This script only supports Ubuntu 22.04 LTS and 24.04 LTS."
    exit 1
else
    echo "Ubuntu version ${UBUNTU_VERSION} is supported."
fi

echo "Running as root. Ubuntu version detected: ${UBUNTU_VERSION}."

echo "========== Pre-Checks Completed Successfully =========="

echo "========== Starting Toolkit Installation =========="

echo "Updating package lists..."
apt-get update

echo "--------------- Installing Git ---------------"
if git --version &>/dev/null; then
    echo "Git is already installed."
else
    echo "Installing Git..."
    apt-get install -y git
fi

echo "--------------- Installing Python ---------------"
if python3 --version | awk '{print $2}' | grep -qE '^3\.1[3-9]|^[4-9]'; then
    echo "Python ${PYTHON_VERSION} is already installed."
else
    echo "Adding deadsnakes PPA and installing Python ${PYTHON_VERSION}..."
    add-apt-repository ppa:deadsnakes/ppa -y
    apt-get install -y ${PYTHON_BIN}-full
fi

echo "Installing Python venv module..."
apt install -y ${PYTHON_BIN}-venv

echo "--------------- Installing uv ---------------"
curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=${UV_PATH} sh

echo "--------------- Cloning toolkit installer repository ---------------"
if [[ -d ${TOOLKIT_INSTALLER_FOLDER} ]]; then
    echo "Toolkit installer repository already cloned."
else
    echo "Cloning toolkit installer repository..."
    git clone https://github.com/6G-SANDBOX/toolkit-installer.git ${TOOLKIT_INSTALLER_FOLDER}
fi

echo "Installing toolkit installer dependencies using uv..."
${UV_BIN} --directory ${TOOLKIT_INSTALLER_FOLDER} sync
cd ${TOOLKIT_INSTALLER_FOLDER}
${UV_BIN} run python installer.py