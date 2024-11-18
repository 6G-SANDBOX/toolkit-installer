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

def git_clone(https_url: str, path: str) -> None:
    """
    Clone a GitHub repository to the specified path

    :param https_url: the URL of the GitHub repository, ``str``
    :param path: the local path to clone the repository into, ``str``
    """
    if _is_github_repo(https_url): Repo.clone_from(https_url, path)