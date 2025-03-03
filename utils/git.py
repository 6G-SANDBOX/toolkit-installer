from typing import List

from utils.cli import run_command
from utils.logs import msg
from utils.os import check_exist_directory, remove_directory

def git_add(path: str) -> None:
    """
    Add files to the staging area

    :param path: the path to the repository, ``str``
    """
    command = f"git -C {path} add ."
    stdout, stderr, rc = run_command(command)
    if rc != 0:
        msg(level="error", message=f"Failed to add files to the staging area in the repository {path}. Command executed: {command}. Error received: {stderr}. Return code: {rc}")
    msg(level="debug", message=f"Files added to the staging area in the repository {path}. Command executed: {command}. Output received: {stdout}. Return code: {rc}")

def git_clone(https_url: str, path: str, token: str = None) -> None:
    """
    Clone a GitHub repository to the specified path

    :param https_url: the URL of the GitHub repository, ``str``
    :param path: the local path to clone the repository into, ``str``
    :param token: the token to access the repository, ``str``
    """
    if token:
        https_url = https_url.replace("https://", f"https://{token}@")
    git_validate_token(github_token=token)
    if check_exist_directory(path=path):
        msg(level="warning", message=f"Directory {path} already exists. Skipping cloning the GitHub repository at {https_url}")
    else:
        command = f"git clone {https_url} {path}"
        stdout, stderr, rc = run_command(command)
        if rc != 0:
            msg(level="error", message=f"Failed to clone the GitHub repository at {https_url} to the path {path}. Command executed: {command}. Error received: {stderr}. Return code: {rc}")
    msg(level="debug", message=f"GitHub repository at {https_url} cloned to the path {path}. Command executed: {command}. Output received: {stdout}. Return code: {rc}")

def git_commit(path: str, message: str) -> None:
    """
    Commit the staged files

    :param path: the path to the repository, ``str``
    :param message: the commit message, ``str``
    """
    command = f"git -C {path} commit -m '{message}'"
    stdout, stderr, rc = run_command(command)
    if rc != 0:
        msg(level="error", message=f"Failed to commit the staged files in the repository {path}. Command executed: {command}. Error received: {stderr}. Return code: {rc}")
    msg(level="debug", message=f"Staged files committed in the repository {path}. Command executed: {command}. Output received: {stdout}. Return code: {rc}")

def git_create_branch(path: str, branch: str) -> None:
    """
    Create a new branch in the repository

    :param path: the path to the repository, ``str``
    :param branch: the branch to create, ``str``
    """
    command = f"git -C {path} branch {branch}"
    stdout, stderr, rc = run_command(command)
    if rc != 0:
        msg(level="error", message=f"Failed to create a new branch {branch} in the repository {path}. Command executed: {command}. Error received: {stderr}. Return code: {rc}")
    msg(level="debug", message=f"New branch {branch} created in the repository {path}. Command executed: {command}. Output received: {stdout}. Return code: {rc}")

def git_current_branch(path: str) -> str:
    """
    Get the current branch of the repository

    :param path: the path to the repository, ``str``
    :return: the current branch, ``str``
    """
    command = f"git -C {path} branch --show-current"
    stdout, stderr, rc = run_command(command)
    if rc != 0:
        msg(level="error", message=f"Failed to get the current branch of the repository {path}. Command executed: {command}. Error received: {stderr}. Return code: {rc}")
    msg(level="debug", message=f"Current branch of the repository {path} found. Command executed: {command}. Output received: {stdout}. Return code: {rc}")
    return stdout

def git_push(path: str) -> None:
    """
    Push the committed changes to the remote repository

    :param path: the path to the repository, ``str``
    """
    command = f"git -C {path} push"
    stdout, stderr, rc = run_command(command)
    if rc != 0:
        msg(level="error", message=f"Failed to push the committed changes to the remote repository {path}. Command executed: {command}. Error received: {stderr}. Return code: {rc}")
    msg(level="debug", message=f"Committed changes pushed to the remote repository {path}. Command executed: {command}. Output received: {stdout}. Return code: {rc}")

def git_remotes_branches(path: str) -> List[str]:
    """
    Get the list of branches in the remote repository

    :param path: the path to the repository, ``str``
    :return: the list of branches, ``List[str]``
    """
    command = f"git -C {path} branch -r"
    stdout, stderr, rc = run_command(command)
    if rc != 0:
        msg(level="error", message=f"Failed to get the list of branches in the remote repository {path}. Command executed: {command}. Error received: {stderr}. Return code: {rc}")
    msg(level="debug", message=f"List of branches in the remote repository {path} found. Command executed: {command}. Output received: {stdout}. Return code: {rc}")
    
    branches = []
    for line in stdout.splitlines():
        line = line.strip()
        if "HEAD" in line:
            continue
        branches.append(line.replace("origin/", ""))
    return branches

def git_switch(path: str, branch: str = None, tag: str = None, commit: str = None) -> None:
    """
    Switch to the specified branch

    :param path: the path to the repository, ``str``
    :param branch: the branch to switch, ``str``
    :param tag: the tag to switch, ``str``
    :param commit: the commit to switch, ``str``
    """
    if branch and tag is None and commit is None:
        command = f"git -C {path} switch {branch}"
    elif tag and branch is None and commit is None:
        command = f"git -C {path} switch --detach {tag}"
    elif commit and branch is None and tag is None:
        command = f"git -C {path} switch --detach {commit}"
    else:
        msg(level="error", message="Invalid switch command. You must specify either a branch, a tag or a commit")
    stdout, stderr, rc = run_command(command)
    if rc != 0:
        msg(level="error", message=f"Failed to switch to the branch {branch} in the repository {path}. Command executed: {command}. Error received: {stderr}. Return code: {rc}")
    msg(level="debug", message=f"Switched to the branch {branch} in the repository {path}. Command executed: {command}. Output received: {stdout}. Return code: {rc}")

def git_validate_token(github_token: str) -> None:
    """
    Validate the GitHub token

    :param github_token: the GitHub token, ``str``
    """
    command = f"curl -s -o /dev/null -w \"%{{http_code}}\" -H \"Authorization: token {github_token}\" -H \"Accept: application/vnd.github.v3+json\" https://api.github.com/user"
    stdout, stderr, rc = run_command(command)
    if rc != 0 or stdout.strip() != "200":
        msg(level="error", message=f"Failed to validate the GitHub token. Command executed: {command}. Error received: {stderr}. Return code: {rc}")
    
    msg(level="debug", message=f"GitHub token validated successfully. Command executed: {command}. Output received: {stdout}. Return code: {rc}")
