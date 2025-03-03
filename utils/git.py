from typing import List

from utils.cli import run_command
from utils.file import loads_json
from utils.logs import msg
from utils.os import check_exist_directory

def git_add(path: str) -> None:
    """
    Add files to the staging area

    :param path: the path to the repository, ``str``
    """
    command = f"git -C {path} add ."
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(level="error", message=f"Failed to add files to the staging area in the repository {path}. Command executed: {command}. Error received: {stderr}. Return code: {rc}")
    msg(level="debug", message=f"Files added to the staging area in the repository {path}. Command executed: {command}. Output received: {stdout}. Return code: {rc}")

def git_clone(https_url: str, path: str) -> None:
    """
    Clone a GitHub repository to the specified path

    :param https_url: the URL of the GitHub repository, ``str``
    :param path: the local path to clone the repository into, ``str``
    """
    if not check_exist_directory(path=path):
        command = f"git clone {https_url} {path}"
        stdout, stderr, rc = run_command(command=command)
        if rc != 0:
            msg(level="error", message=f"Failed to clone the GitHub repository at {https_url} to the path {path}. Command executed: {command}. Error received: {stderr}. Return code: {rc}")
    msg(level="debug", message=f"GitHub repository at {https_url} cloned to the path {path}. Command executed: {command}. Output received: {stdout}. Return code: {rc}")

def git_commit(path: str, message: str) -> None:
    """
    Commit the staged files

    :param path: the path to the repository, ``str``
    :param message: the commit message, ``str``
    """
    command = f"git -C {path} commit -m \"{message}\""
    stdout, stderr, rc = run_command(command=command)
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
    stdout, stderr, rc = run_command(command=command)
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
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(level="error", message=f"Failed to get the current branch of the repository {path}. Command executed: {command}. Error received: {stderr}. Return code: {rc}")
    msg(level="debug", message=f"Current branch of the repository {path} found. Command executed: {command}. Output received: {stdout}. Return code: {rc}")
    return stdout

def get_team_id(github_token: str, github_organization_name: str, github_team_name: str) -> str:
    """
    Get the team ID

    :param github_token: the GitHub token, ``str``
    :param github_organization_name: the GitHub organization name, ``str``
    :param github_team_name: the GitHub team name, ``str``
    :return: the team ID, ``str``
    """
    command = f"curl -s -w \"%{{http_code}}\" -H \"Accept: application/vnd.github+json\" -H \"Authorization: Bearer {github_token}\" -H \"X-GitHub-Api-Version: 2022-11-28\" https://api.github.com/orgs/{github_organization_name}/teams"
    stdout, stderr, rc = run_command(command=command)
    teams, status_code = stdout[:-3].strip(), stdout[-3:]
    if status_code != "200":
        msg(level="error", message=f"Failed to get the id of team {github_team_name} in the organization {github_organization_name}. Invalid token provided. Command executed: {command}. Error received: {stderr}. Return code: {rc}")
    teams = loads_json(data=teams)
    for team in teams:
        if team["name"] == github_team_name:
            team_id = team["id"]
            msg(level="debug", message=f"Team {github_team_name} found with id {team_id} in the organization {github_organization_name}. Command executed: {command}. Output received: {stdout}. Return code: {rc}")
            return team_id
    msg(level="error", message=f"Failed to get the id of team {github_team_name} in the organization {github_organization_name}. Team not found. Command executed: {command}. Output received: {stdout}. Return code: {rc}")

def git_team_access(github_token: str, github_organization_name: str, github_team_name: str, github_username: str) -> None:
    """
    Check if the user has access to the team

    :param github_token: the GitHub token, ``str``
    :param github_organization_name: the GitHub organization name, ``str``
    :param github_team_name: the GitHub team name, ``str``
    :param username: the GitHub username, ``str``
    """
    team_id = get_team_id(github_token=github_token, github_organization_name=github_organization_name, github_team_name=github_team_name)
    command = f"curl -s -w \"%{{http_code}}\" -H \"Accept: application/vnd.github+json\" -H \"Authorization: Bearer {github_token}\" -H \"X-GitHub-Api-Version: 2022-11-28\" https://api.github.com/orgs/{github_organization_name}/team/{team_id}/memberships/{github_username}"
    stdout, stderr, rc = run_command(command=command)
    status_code = stdout[-3:]
    if status_code != "200":
        msg(level="error", message=f"Failed to validate if user {github_username} has access to the team {github_team_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}")
    msg(level="debug", message=f"User {github_username} has access to the team {github_team_name}. Command executed: {command}. Output received: {stdout}. Return code: {rc}")

def git_push(path: str) -> None:
    """
    Push the committed changes to the remote repository

    :param path: the path to the repository, ``str``
    """
    command = f"git -C {path} push"
    stdout, stderr, rc = run_command(command=command)
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
    stdout, stderr, rc = run_command(command=command)
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
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(level="error", message=f"Failed to switch to the branch {branch} in the repository {path}. Command executed: {command}. Error received: {stderr}. Return code: {rc}")
    msg(level="debug", message=f"Switched to the branch {branch} in the repository {path}. Command executed: {command}. Output received: {stdout}. Return code: {rc}")
