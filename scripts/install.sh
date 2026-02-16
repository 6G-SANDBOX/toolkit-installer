#!/usr/bin/env bash

set -e

export DEBIAN_FRONTEND=noninteractive

PYTHON_VERSION="3.13"
PYTHON_BIN="python${PYTHON_VERSION}"
UV_PATH="/opt/uv"
UV_BIN="${UV_PATH}/uv"
TOOLKIT_INSTALLER_DIRECTORY="/opt/toolkit-installer"
TOOLKIT_INSTALLER_VERSION="v1.0.0"

if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root. Please use sudo or switch to the root user"
    exit 1
else
    echo "Script is running as root"
fi

UBUNTU_VERSION=$(lsb_release -rs)
echo "Detected Ubuntu version: ${UBUNTU_VERSION}"
if [[ "${UBUNTU_VERSION}" != "22.04" && "${UBUNTU_VERSION}" != "24.04" ]]; then
    echo "Unsupported Ubuntu version: ${UBUNTU_VERSION}. This script only supports Ubuntu 22.04 LTS and 24.04 LTS"
    exit 1
else
    echo "Ubuntu version ${UBUNTU_VERSION} is supported"
fi

apt-get update

PACKAGES=("figlet" "ansible-core" "curl" "git")

for package in "${PACKAGES[@]}"; do
    if dpkg -l | grep -qw "$package"; then
        echo "$package is already installed"
    else
        echo "Installing $package"
        apt install -y "$package"
    fi
done

if python${PYTHON_VERSION} --version &>/dev/null; then
    echo "Python ${PYTHON_VERSION} is already installed"
else
    echo "Adding deadsnakes PPA and installing Python ${PYTHON_VERSION}"
    add-apt-repository ppa:deadsnakes/ppa -y
    apt-get install -y ${PYTHON_BIN}-full
    apt install -y ${PYTHON_BIN}-venv
fi

if [[ -f ${UV_BIN} ]]; then
    echo "UV is already installed"
else
    echo "Installing uv"
    curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=${UV_PATH} sh
fi

if [[ -d ${TOOLKIT_INSTALLER_DIRECTORY} ]]; then
    echo "Toolkit installer repository already cloned"
    rm -rf ${TOOLKIT_INSTALLER_DIRECTORY}
fi

echo "Cloning toolkit installer repository"
git clone --depth 1 --branch ${TOOLKIT_INSTALLER_VERSION} -c advice.detachedHead=false https://github.com/6G-SANDBOX/toolkit-installer.git ${TOOLKIT_INSTALLER_DIRECTORY}

echo "Installing toolkit installer dependencies"
${UV_BIN} --directory ${TOOLKIT_INSTALLER_DIRECTORY} sync
cd ${TOOLKIT_INSTALLER_DIRECTORY}
figlet -c "[6G-SANDBOX] TOOLKIT INSTALLER"
${UV_BIN} run python installer.py
