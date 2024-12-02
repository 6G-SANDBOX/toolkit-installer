from git import Repo

from phases.utils.logs import msg

def get_repo(path: str) -> Repo:
    """
    Get the repository object from the specified path

    :param path: the path to the repository, ``str``
    :return: the repository object, ``Repo``
    """
    return Repo(path)

def git_branch(path: str, branch_name: str) -> str:
    """
    Get the current branch of the repository

    :param path: the path to the repository, ``str``
    :param branch_name: the name of the branch, ``str``
    :return: the current branch, ``str``
    """
    repo = get_repo(path)
    msg("info", f"Creating branch {branch_name}")
    repo.create_head(branch_name)
    msg("info", f"Branch created")

def git_branches(path: str) -> list[str]:
    """
    Get the branches of the repository

    :param path: the path to the repository, ``str``
    :return: the list of branches, ``list[str]``
    """
    repo = get_repo(path)
    return [ref.remote_head for ref in repo.remotes.origin.refs if ref.remote_head != "HEAD"]

def git_clone(https_url: str, path: str) -> None:
    """
    Clone a GitHub repository to the specified path

    :param https_url: the URL of the GitHub repository, ``str``
    :param path: the local path to clone the repository into, ``str``
    """
    msg("info", f"Cloning repository from {https_url} to {path}")
    Repo.clone_from(https_url, path)
    msg("info", "Repository cloned")

def git_switch(path: str, branch: str) -> None:
    """
    Switch to the specified branch

    :param path: the path to the repository, ``str``
    :param branch: the branch to switch to, ``str``
    """
    repo = get_repo(path)
    msg("info", f"Switching to branch {branch}")
    repo.git.switch(branch)
    msg("info", "Switched to branch")

def git_add(path: str, *args: str) -> None:
    """
    Add files to the staging area

    :param path: the path to the repository, ``str``
    :param args: the files to add, ``str``
    """
    repo = get_repo(path)
    msg("info", "Adding files to the staging area")
    if args:
        repo.index.add(args)
    else:
        repo.git.add(".")
    msg("info", "Files added to the staging area")

def git_commit(path: str, message: str) -> None:
    """
    Commit the staged files

    :param path: the path to the repository, ``str``
    :param message: the commit message, ``str``
    """
    repo = get_repo(path)
    msg("info", f"Committing changes with message: {message}")
    repo.index.commit(message)
    msg("info", "Changes committed")

def git_push(path: str, branch: str) -> None:
    """
    Push the committed changes to the remote repository

    :param path: the path to the repository, ``str``
    :param branch: the branch to push to, ``str``
    """
    repo = get_repo(path)
    msg("info", f"Pushing changes to branch {branch}")
    repo.remotes.origin.push(branch)
    msg("info", "Changes pushed")