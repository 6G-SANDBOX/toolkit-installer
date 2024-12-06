<a name="readme-top"></a>

<div align="center">

  # 6G-SANDBOX TOOLKIT INSTALLER <!-- omit in toc -->

  [![Contributors][contributors-shield]][contributors-url]
  [![Forks][forks-shield]][forks-url]
  [![Stargazers][stars-shield]][stars-url]
  [![Issues][issues-shield]][issues-url]
  [![MIT License][license-shield]][license-url]

  <a href="https://github.com/6G-SANDBOX/toolkit-installer"><img src="./images/logo.png" width="300" title="toolkit-installer"></a>

  [![toolkit-installer][toolkit-installer-badge]][toolkit-installer-url]

  [Report error](https://github.com/6G-SANDBOX/toolkit-installer/issues/new?assignees=&labels=&projects=&template=bug_report.md) · [Feature request](https://github.com/6G-SANDBOX/toolkit-installer/issues/new?assignees=&labels=&projects=&template=feature_request.md) · [Wiki](https://github.com/6G-SANDBOX/toolkit-installer/wiki)
</div>

Create new 6G-SANDBOX site.

<details>
<summary>Table of Contents</summary>

- [:hammer\_and\_wrench: Stack](#hammer_and_wrench-stack)
- [:white\_check\_mark: Requirements](#white_check_mark-requirements)
- [:rocket: Getting Started](#rocket-getting-started)
- [:cyclone: Phases](#cyclone-phases)
  - [Zero phase](#zero-phase)
  - [First phase](#first-phase)
  - [Second phase](#second-phase)
  - [Third phase](#third-phase)
  - [Fourth phase](#fourth-phase)
  - [Fifth phase](#fifth-phase)
- [📚 Documentation](#-documentation)

</details>

## :hammer_and_wrench: Stack
[![Python][python-badge]][python-url] - Programming language.

## :white_check_mark: Requirements

Be part of the [**6G-SANDBOX**](https://github.com/6G-SANDBOX) organization on GitHub.

| Repository       | Release                                                                | Branch                                                            |
| ---------------- | ---------------------------------------------------------------------- | ----------------------------------------------------------------- |
| OpenNebula       | [v6.10](https://github.com/OpenNebula/one/releases/tag/release-6.10.0) | -                                                                 |
| 6G-Library       | -                                                                      | [develop](https://github.com/6G-SANDBOX/6G-Library/tree/develop)  |
| 6G-Sandbox-Sites | -                                                                      | [main](https://github.com/6G-SANDBOX/6G-Sandbox-Sites)            |
| TNLCM            | [v0.4.4](https://github.com/6G-SANDBOX/TNLCM/releases/tag/v0.4.4)      | -                                                                 |

## :rocket: Getting Started

Install Poetry

```bash
POETRY_FOLDER="/opt/poetry"
POETRY_BIN="/opt/poetry/bin/poetry"
curl -sSL https://install.python-poetry.org | POETRY_HOME=${POETRY_FOLDER} python3 -
${POETRY_BIN} config virtualenvs.in-project true
```

Clone the repository

```bash
git clone https://github.com/6G-SANDBOX/toolkit-installer.git
```

Access to the path in which the toolkit-installer repository was cloned 

```bash
cd toolkit-installer
```

Install libraries

```bash
${POETRY_BIN} install --no-root
```

Activate environment

```bash
${POETRY_BIN} shell
```

Create .env file

```bash
cp .env.template .env
```

> [!IMPORTANT]
> The script execution must be performed in the OpenNebula frontend using **root** user.

```bash
python3 installer.py
```

## :cyclone: Phases

### Zero phase

- Update ubuntu packages.
- Check if the script is being executed as root.
- Check if the OpenNebula CLI tools are installed.

### First phase

- Create 6G-SANDBOX group.
- Create jenkins-master user.

### Second phase

- Add the 6G-SANDBOX marketplace to OpenNebula.
- Instantiate the 6G-SANDBOX Toolkit appliance.
- Assign ssh key to jenkins-master user.

### Third phase

- Refresh the list of available appliances in the marketplace.
- Download required appliances from the OpenNebula Public marketplace:
  - Ubuntu 22.04
  - Service oneKE 1.29
- Download required appliances from the 6G-SANDBOX marketplace:
  - Service 6G-Sandbox Toolkit
  - NTP
  - UERANSIM

### Fourth phase

- Integrate with 6G-SANDBOX-Sites repository.
- Create new 6G-SANDBOX sites in 6G-Sandbox-Sites repository.

### Fifth phase

- Integrate with TNLCM repository.
- Run an end-to-end trial network.

## 📚 Documentation

Find the complete documentation and usage guides in our [wiki](https://github.com/6G-SANDBOX/toolkit-installer/wiki).

## Contributors <!-- omit in toc -->

<a href="https://github.com/6G-SANDBOX/toolkit-installer/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=6G-SANDBOX/toolkit-installer" />
</a>

<p align="right"><a href="#readme-top">Back to top&#x1F53C;</a></p>

<!-- Urls, Shields and Badges -->
[toolkit-installer-badge]: https://img.shields.io/badge/toolkit--installer-v0.1.0-blue
[toolkit-installer-url]: https://github.com/6G-SANDBOX/toolkit-installer/releases/tag/v0.1.0
[python-badge]: https://img.shields.io/badge/Python-3.13.0-blue?style=for-the-badge&logo=python&logoColor=white&labelColor=3776AB
[python-url]: https://www.python.org/downloads/release/python-3130/
[contributors-shield]: https://img.shields.io/github/contributors/6G-SANDBOX/toolkit-installer.svg?style=for-the-badge
[contributors-url]: https://github.com/6G-SANDBOX/toolkit-installer/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/6G-SANDBOX/toolkit-installer.svg?style=for-the-badge
[forks-url]: https://github.com/6G-SANDBOX/toolkit-installer/network/members
[stars-shield]: https://img.shields.io/github/stars/6G-SANDBOX/toolkit-installer.svg?style=for-the-badge
[stars-url]: https://github.com/6G-SANDBOX/toolkit-installer/stargazers
[issues-shield]: https://img.shields.io/github/issues/6G-SANDBOX/toolkit-installer.svg?style=for-the-badge
[issues-url]: https://github.com/6G-SANDBOX/toolkit-installer/issues
[license-shield]: https://img.shields.io/badge/License-Apache%202.0-green.svg?style=for-the-badge
[license-url]: https://github.com/6G-SANDBOX/toolkit-installer/blob/main/LICENSE