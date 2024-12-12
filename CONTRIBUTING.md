# Contribute to Toolkit Installer

## Welcome to the toolkit installer project!

This project allows you to install MinIO, Jenkins, and TNLCM on OpenNebula. We are excited that you're interested in contributing to this project. Before you get started, please read this guide to understand how you can contribute.

### :rocket: Getting Started

1. **Familiarize yourself with Python**
2. **Set up your development environment**

### :hammer_and_wrench: How to contribute

#### 1. Set up your environment

- **Fork the repository**: fork the project to your GitHub account to have your own copy. To do this, click the "Fork" button at the top right of the repository page on GitHub. This will create a copy of the repository in your GitHub account.
- **Clone your fork**: after forking, clone the repository to your local machine. To do this, copy the URL of your fork by clicking the green "Code" button, then run `git clone <URL of your fork>` in your terminal.
- **Add the original repository as a remote**: to keep your fork updated with changes from the original repository, add the original repository as a remote. You can do this by running `git remote add upstream <URL of the original repository>`.
- **Make sure to use the correct Python version**: to check, run `python3 --version` and ensure you download the version specified in `pyproject.toml`.
- **Install dependencies**: navigate to the directory of the cloned project and run `poetry install --no-root` to install all the necessary dependencies.

#### 2. Work on your changes

- **Sync the fork**: you can do this from `github.com/your-username/your-toolkit-installer-repository` by clicking on `Sync fork`. Alternatively, you can do it from the terminal with `gh repo sync -b main` or `git switch main && git fetch upstream && git merge upstream/main`. More information is available in the [official GitHub documentation](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork).
- **Create a new branch**: before you start working on your changes, create a new branch using `git switch -c your-branch-name`. Your branch name should start with one of the following prefixes:
  - `feature/` for new features
  - `bugfix/` for bug fixes
  - `release/` for preparing a new release
  - `hotfix/` for urgent fixes to the main branch
  - `experiment/` for experimental changes
- **Develop your changes**: implement your changes or improvements in your local branch. Make sure to follow the project's coding practices and standards.
- **Test your changes**: run `python3 installer.py` to start running the script. Make sure your changes work correctly and don't break anything.

#### 3. Submit your changes

- **Commit your changes**: once you're happy with your changes, commit them with a clear and descriptive message.
- **Push to your fork**: push your branch with the changes to your fork on GitHub using `git push origin your-branch-name`.
- **Create a Pull Request (PR)**: on GitHub, go to your fork of the toolkit installer and click "Pull request" to start one. Make sure to clearly describe the changes you've made and why they are necessary or useful for the project.

### :star2: Best practices

- **Review open issues** before opening a PR. If you think you can solve an issue and no other PR is open, use `#issue-number` in your commit to link it to the issue. It is also helpful to leave a comment so that it's clear which PR is being used for the issue.
- **Review open PRs** to ensure you're not working on something that is already in progress. You can always help on open PRs by contributing changes, comments, reviews, etc.
- **Keep your commits clean and descriptive**.
- **Follow the project's coding conventions**.
- **Update your branch regularly** to keep it up to date with the main branch of the project.

Thank you for contributing to the toolkit installer! Together, we're building something amazing.