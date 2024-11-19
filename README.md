# 6G-SANDBOX TOOLKIT INSTALLER

Python3 script that configures an OpenNebula cluster as a 6G-SANDBOX site. 

<details>
<summary>Table of Contents</summary>

- [6G-SANDBOX TOOLKIT INSTALLER](#6g-sandbox-toolkit-installer)
  - [:white\_check\_mark: Requirements](#white_check_mark-requirements)
  - [:rocket: Getting Stared](#rocket-getting-stared)
  - [:cyclone: Phases](#cyclone-phases)
    - [Phase 0](#phase-0)
    - [Phase 1 -\> PENDING](#phase-1---pending)
    - [Phase 2](#phase-2)
    - [Phase 3](#phase-3)
    - [Phase 4](#phase-4)
    - [Phase 5](#phase-5)

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

### Phase 0

- Update ubuntu packages.
- Check if ansible-core is installed.
- Check if the script is being executed as root.
- Check if the OpenNebula CLI tools are installed.

### Phase 1 -> PENDING

- Create new 6G-SANDBOX sites in 6G-Sandbox-Sites repository.

### Phase 2

- Add the 6G-SANDBOX marketplace to OpenNebula if not present.
- Refresh the list of available appliances in the marketplace.

### Phase 3

- Download base required appliances for the 6G-SANDBOX-core: Ubuntu and OneKE v1.2.9. The user is able to select version and datastore for each one.
- Instantiate of the 6G-SANDBOX service. The user will be prompted for the required parameters. Pending to add further healthchecks.

### Phase 4

- Donwloading and scanning the 6G Library repository for appliances.
- Matching the found appliances with the ones present in the 6G-SANDBOX Marketplace.
- Console dialog, asking the installer which component appliances  wants to import into the datastore. The appliances shown are the ones matching.

### Phase 5

- Launching a basic TN. A pipeline can be created in Jenkins, for the operator to enter and execute.
- Validation and certification. Some testing.

## Contributors <!-- omit in toc -->

<a href="https://github.com/6G-SANDBOX/toolkit-installer/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=6G-SANDBOX/toolkit-installer" />
</a>