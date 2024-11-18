import re

from git import Repo

def _is_github_repo(url: str) -> bool:
    """
    Check if the repository url is a git repository

    :param url: url to be checked, ``str``
    :return: True if the URL is a valid GitHub repository. Otherwise False, ``bool``
    """
    github_url_patterns = [
        r"^https://github.com/.+/.+\.git$",
        r"^git@github.com:.+/.+\.git$"
    ]
    return any(re.match(pattern, url) for pattern in github_url_patterns)

def get_repo(path: str) -> Repo:
    """
    Get the repository object from the specified path

    :param path: the path to the repository, ``str``
    :return: the repository object, ``Repo``
    """
    return Repo(path)

def git_branches(path: str) -> list[str]:
    """
    Get the branches of the repository

    :param path: the path to the repository, ``str``
    :return: the list of branches, ``list[str]``
    """
    repo = get_repo(path)
    return [ref.remote_head for ref in repo.remotes.origin.refs if ref.remote_head != "HEAD"]

def git_clone(https_url: str, path: str) -> Repo:
    """
    Clone a GitHub repository to the specified path

    :param https_url: the URL of the GitHub repository, ``str``
    :param path: the local path to clone the repository into, ``str``
    :return: the cloned repository, ``Repo``
    """
    if _is_github_repo(https_url): return Repo.clone_from(https_url, path)

def git_switch(path: str, branch: str) -> None:
    """
    Switch to the specified branch

    :param path: the path to the repository, ``str``
    :param branch: the branch to switch to, ``str``
    """
    repo = get_repo(path)
    repo.git.switch("-c", branch)

def git_add(path: str, *args: str) -> None:
    """
    Add files to the staging area

    :param path: the path to the repository, ``str``
    :param args: the files to add, ``str``
    """
    repo = get_repo(path)
    repo.index.add(args)

def git_commit(path: str, message: str) -> None:
    """
    Commit the staged files

    :param path: the path to the repository, ``str``
    :param message: the commit message, ``str``
    """
    repo = get_repo(path)
    repo.index.commit(message)

def git_push(path: str, branch: str) -> None:
    """
    Push the committed changes to the remote repository

    :param path: the path to the repository, ``str``
    :param branch: the branch to push to, ``str``
    """
    repo = get_repo(path)
    repo.remotes.origin.push(branch)