# 6G-SANDBOX TOOLKIT INSTALLER

Python3 script that configures an OpenNebula cluster as a 6G-SANDBOX site. 

<details>
<summary>Table of Contents</summary>

- [6G-SANDBOX TOOLKIT INSTALLER](#6g-sandbox-toolkit-installer)
  - [:white\_check\_mark: Requirements](#white_check_mark-requirements)
  - [:rocket: Getting Stared](#rocket-getting-stared)
  - [:cyclone: Phases](#cyclone-phases)
    - [Zero phase](#zero-phase)
    - [First phase](#first-phase)
    - [Second phase](#second-phase)
    - [Third phase](#third-phase)
    - [Fourth phase](#fourth-phase)
    - [Fifth phase](#fifth-phase)

</details>

## :white_check_mark: Requirements

- An OpenNebula cluster with VMs internet access.
- Python3 and pip3 packages installed in the OpenNebula Frontend VMs.
- Token for the 6G-Sandbox-Sites repository (privileges: **Contents** - **Read and write**). Specify the token in the `.env` file.

## :rocket: Getting Stared

Install Poetry

```bash
POETRY_FOLDER="/opt/poetry"
POETRY_BIN="/opt/poetry/bin/poetry"
curl -sSL https://install.python-poetry.org | POETRY_HOME=${POETRY_FOLDER} python3 -
${POETRY_BIN} config virtualenvs.in-project true
```

Access to the path in which the toolkit-installer repository was cloned 

```bash
cd <toolkit-installer-directory>
```

Install libraries

```bash
${POETRY_BIN} install --no-root
```

Activate environment
```bash
${POETRY_BIN} shell
```

> [!IMPORTANT]
> The script execution must be performed in the OpenNebula Frontend using **root** user. This is due to the necessity of using the OpenNebula CLI tools and modifying core OpenNebula configurations. In future versions the possibility to use this tool remotely could be added.

```bash
python3 main.py
```

## :cyclone: Phases

### Zero phase

- Update ubuntu packages.
- Check if ansible-core is installed.
- Check if the script is being executed as root.
- Check if the OpenNebula CLI tools are installed.

### First phase

- Integrate with 6G-SANDBOX-Sites repository.
- Create new 6G-SANDBOX sites in 6G-Sandbox-Sites repository.

### Second phase

- Create 6G-SANDBOX group.
- Create jenkins-master user.

### Third phase

- Add the 6G-SANDBOX marketplace to OpenNebula.
- Refresh the list of available appliances in the marketplace.
- Download required appliances from the OpenNebula Public marketplace:
  - Ubuntu 22.04
  - Service oneKE 1.29
- Download required appliances from the 6G-SANDBOX marketplace:
  - Service 6G-Sandbox Toolkit
  - NTP
  - UERAMSIM

### Fourth phase

- Integrate with 6G-Library repository.
- Download appliance from components selected in 6G-Sandbox-Sites repository using 6G-Library repository.

### Fifth phase

- Integrate with TNLCM repository.
- Launch an end-to-end trial network.

## Contributors <!-- omit in toc -->

<a href="https://github.com/6G-SANDBOX/toolkit-installer/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=6G-SANDBOX/toolkit-installer" />
</a>