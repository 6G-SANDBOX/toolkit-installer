from typing import List

from utils.cli import run_command
from utils.file import loads_json
from utils.logs import msg
from utils.os import exist_directory


def git_add(path: str) -> None:
    """
    Add files to the staging area

    :param path: the path to the repository, ``str``
    """
    if not exist_directory(path=path):
        msg(
            level="error",
            message=f"Repository {path} does not exist. Cannot add files to the staging area",
        )
    command = f"git -C {path} add -A"
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Failed to add files to the staging area in the repository {path}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"Files added to the staging area in the repository {path}. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )


def git_branches(path: str) -> List[str]:
    """
    Get the list of local and remotes branches in the repository

    :param path: the path to the repository, ``str``
    :return: the list of branches, ``List[str]``
    """
    if not exist_directory(path=path):
        msg(
            level="error",
            message=f"Repository {path} does not exist. Cannot get the list of branches",
        )
    command = f"git -C {path} branch -a"
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Failed to get the list of branches in the repository {path}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"List of branches in the repository {path} found. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )

    branches = set()
    for line in stdout.splitlines():
        line = line.strip().replace("*", "").strip()
        if "HEAD" in line:
            continue
        if line.startswith("remotes/origin/"):
            line = line[len("remotes/origin/") :]
        branches.add(line)

    return sorted(branches)


def git_checkout(path: str, ref: str) -> None:
    """
    Checkout the specified branch, tag or commit

    :param path: the path to the repository, ``str``
    :param ref: the branch or commit to checkout, ``str``
    """
    if not exist_directory(path=path):
        msg(
            level="error",
            message=f"Repository {path} does not exist. Cannot checkout branch, tag or commit {ref}",
        )
    command = f"git -C {path} checkout {ref} --"
    stdout, _, rc = run_command(command=command)
    msg(
        level="debug",
        message=f"Checkout branch, tag or commit {ref} in the repository {path}. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )


def git_clean_fd(path: str) -> None:
    """
    Clean the repository

    :param path: the path to the repository, ``str``
    """
    if not exist_directory(path=path):
        msg(
            level="error",
            message=f"Repository {path} does not exist. Cannot clean the repository",
        )
    command = f"git -C {path} clean -fd"
    run_command(command=command)


def git_clone(https_url: str, path: str, token: str = None) -> None:
    """
    Clone a GitHub repository to the specified path

    :param https_url: the URL of the GitHub repository, ``str``
    :param path: the local path to clone the repository into, ``str``
    :param token: the token to access the repository, ``str``
    """
    if token:
        https_url = https_url.replace("https://", f"https://{token}@")
    if not exist_directory(path=path):
        command = f"git clone {https_url} {path}"
        stdout, stderr, rc = run_command(command=command)
        if rc != 0:
            msg(
                level="error",
                message=f"Failed to clone the GitHub repository at {https_url} to the path {path}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
            )
        msg(
            level="debug",
            message=f"GitHub repository at {https_url} cloned to the path {path}. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
        )


def git_commit(path: str, message: str) -> None:
    """
    Commit the staged files

    :param path: the path to the repository, ``str``
    :param message: the commit message, ``str``
    """
    if not exist_directory(path=path):
        msg(
            level="error",
            message=f"Repository {path} does not exist. Cannot commit the staged files",
        )
    command = f'git -C {path} commit -m "{message}"'
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Failed to commit the staged files in the repository {path}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"Staged files committed in the repository {path}. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )


def git_create_branch(path: str, new_branch: str, base_branch: str) -> None:
    """
    Create a new branch in the repository

    :param path: the path to the repository, ``str``
    :param new_branch: the name of the new branch, ``str``
    :param base_branch: the name of the base branch, ``str``
    """
    if not exist_directory(path=path):
        msg(
            level="error",
            message=f"Repository {path} does not exist. Cannot create a new branch {new_branch}",
        )
    command = f"git -C {path} switch -c {new_branch} {base_branch}"
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Failed to create a new branch {new_branch} in the repository {path}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"New branch {new_branch} created in the repository {path}. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )


def git_current_branch(path: str) -> str:
    """
    Get the current branch of the repository

    :param path: the path to the repository, ``str``
    :return: the current branch, ``str``
    """
    if not exist_directory(path=path):
        msg(
            level="error",
            message=f"Repository {path} does not exist. Cannot get the current branch",
        )
    command = f"git -C {path} branch --show-current"
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Failed to get the current branch of the repository {path}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"Current branch of the repository {path} found. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )
    return stdout


def git_detect_changes(path: str) -> bool:
    """
    Detect changes in the repository

    :param path: the path to the repository, ``str``
    :return: ``True`` if changes detected, ``False`` otherwise
    """
    if not exist_directory(path=path):
        msg(
            level="error",
            message=f"Repository {path} does not exist. Cannot detect changes",
        )
    command = f"git -C {path} status --porcelain"
    stdout, _, rc = run_command(command=command)
    msg(
        level="debug",
        message=f"Changes detected in the repository {path}. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )
    return bool(stdout)


def git_fetch_prune(path: str) -> None:
    """
    Fetch and prune the remote branches

    :param path: the path to the repository, ``str``
    """
    if not exist_directory(path=path):
        msg(
            level="error",
            message=f"Repository {path} does not exist. Cannot fetch and prune the remote branches",
        )
    command = f"git -C {path} fetch --prune"
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Failed to fetch and prune the remote branches in the repository {path}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"Remote branches fetched and pruned in the repository {path}. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )


def git_pull(path: str) -> None:
    """
    Pull the changes from the remote repository

    :param path: the path to the repository, ``str``
    """
    if not exist_directory(path=path):
        msg(
            level="error",
            message=f"Repository {path} does not exist. Cannot pull changes from the remote repository",
        )
    command = f"git -C {path} pull"
    stdout, _, rc = run_command(command=command)
    msg(
        level="debug",
        message=f"Changes pulled from the remote repository {path}. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )


def git_push(path: str) -> None:
    """
    Push the committed changes to the remote repository

    :param path: the path to the repository, ``str``
    """
    if not exist_directory(path=path):
        msg(
            level="error",
            message=f"Repository {path} does not exist. Cannot push the committed changes to the remote repository",
        )
    current_branch = git_current_branch(path=path)
    check_upstream_cmd = (
        f"git -C {path} rev-parse --abbrev-ref --symbolic-full-name @{{u}}"
    )
    stdout, _, rc = run_command(command=check_upstream_cmd)
    if rc != 0:
        command = f"git -C {path} push --set-upstream origin {current_branch}"
    else:
        command = f"git -C {path} push"
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Failed to push the committed changes to the remote repository {path}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"Committed changes pushed to the remote repository {path}. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )


def git_reset_hard(path: str) -> None:
    """
    Reset the repository to the last commit

    :raise GitError:
    """
    if not exist_directory(path=path):
        msg(
            level="error",
            message=f"Repository {path} does not exist. Cannot reset the repository to the last commit",
        )
    command = f"git -C {path} reset --hard"
    run_command(command=command)


def git_switch(
    path: str, branch: str = None, tag: str = None, commit: str = None
) -> None:
    """
    Switch to the specified branch

    :param path: the path to the repository, ``str``
    :param branch: the branch to switch, ``str``
    :param tag: the tag to switch, ``str``
    :param commit: the commit to switch, ``str``
    """
    if not exist_directory(path=path):
        msg(
            level="error",
            message=f"Repository {path} does not exist. Cannot switch to the branch {branch}",
        )
    if branch and tag is None and commit is None:
        command = f"git -C {path} switch {branch}"
    elif tag and branch is None and commit is None:
        command = f"git -C {path} switch --detach {tag}"
    elif commit and branch is None and tag is None:
        command = f"git -C {path} switch --detach {commit}"
    else:
        msg(
            level="error",
            message="Invalid switch command. You must specify either a branch, a tag or a commit",
        )
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Failed to switch to the branch {branch} in the repository {path}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"Switched to the branch {branch} in the repository {path}. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )


def git_sync_branches(path: str) -> None:
    """
    Synchronize the local branches with the remote branches

    :param path: the path to the repository, ``str``
    """
    if not exist_directory(path=path):
        msg(
            level="error",
            message=f"Repository {path} does not exist. Cannot synchronize the local branches with the remote branches",
        )
    command = f"git -C {path} branch -vv | grep ': gone]' | awk '{{print $1}}' | xargs -r git -C {path} branch -D"
    stdout, stderr, rc = run_command(command=command)
    if rc != 0:
        msg(
            level="error",
            message=f"Failed to synchronize the local branches with the remote branches in the repository {path}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"Local branches synchronized with the remote branches in the repository {path}. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )


def git_team_access(
    token: str, organization_name: str, team_name: str, username: str
) -> None:
    """
    Check if the user has access to the team

    :param token: the GitHub token, ``str``
    :param organization_name: the GitHub organization name, ``str``
    :param team_name: the GitHub team name, ``str``
    :param username: the GitHub username, ``str``
    """
    team_id = git_team_id(
        token=token, organization_name=organization_name, team_name=team_name
    )
    command = f'curl -s -w "%{{http_code}}" -H "Accept: application/vnd.github+json" -H "Authorization: Bearer {token}" -H "X-GitHub-Api-Version: 2022-11-28" https://api.github.com/orgs/{organization_name}/team/{team_id}/memberships/{username}'
    stdout, stderr, rc = run_command(command=command)
    status_code = stdout[-3:]
    if status_code != "200":
        msg(
            level="error",
            message=f"Failed to validate if user {username} has access to the team {team_name}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"User {username} has access to the team {team_name}. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )


def git_team_id(token: str, organization_name: str, team_name: str) -> str:
    """
    Get the team id

    :param token: the GitHub token, ``str``
    :param organization_name: the GitHub organization name, ``str``
    :param team_name: the GitHub team name, ``str``
    :return: the id of the team, ``str``
    """
    command = f'curl -s -w "%{{http_code}}" -H "Accept: application/vnd.github+json" -H "Authorization: Bearer {token}" -H "X-GitHub-Api-Version: 2022-11-28" https://api.github.com/orgs/{organization_name}/teams'
    stdout, stderr, rc = run_command(command=command)
    teams, status_code = stdout[:-3].strip(), stdout[-3:]
    if status_code != "200":
        msg(
            level="error",
            message=f"Failed to get the id of team {team_name} in the organization {organization_name}. Invalid token provided. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    teams = loads_json(data=teams)
    for team in teams:
        if team["name"] == team_name:
            team_id = team["id"]
            msg(
                level="debug",
                message=f"Team {team_name} found with id {team_id} in the organization {organization_name}. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
            )
            return team_id
    msg(
        level="error",
        message=f"Failed to get the id of team {team_name} in the organization {organization_name}. Team not found. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )


def git_validate_token(
    token: str, organization_name: str, repository_name: str, username: str
) -> None:
    """
    Validate the GitHub token

    :param token: the GitHub token, ``str``
    :param organization_name: the GitHub organization name, ``str``
    :param repository_name: the GitHub repository name, ``str``
    :param username: the GitHub username, ``str``
    """
    command = f'curl -s -w "%{{http_code}}" -H "Accept: application/vnd.github+json" -H "Authorization: Bearer {token}" -H "X-GitHub-Api-Version: 2022-11-28" https://api.github.com/repos/{organization_name}/{repository_name}/collaborators/{username}/permission'
    stdout, stderr, rc = run_command(command=command)
    permission, status_code = stdout[:-3].strip(), stdout[-3:]
    if status_code != "200":
        msg(
            level="error",
            message=f"Failed to validate the GitHub token provided by user {username}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    permission = loads_json(data=permission)
    if "permission" not in permission:
        msg(
            level="error",
            message=f"permission key not found in the response when try to validate the GitHub token provided by user {username}. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
        )
    if permission["permission"] != "admin":
        msg(
            level="error",
            message=f"User {username} does not have admin permission in the repository {repository_name}. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"GitHub token provided by user {username} is valid. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )
