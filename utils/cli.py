import subprocess

from typing import Tuple

from utils.logs import msg


def run_command(command: str) -> Tuple[str, str, int]:
    """
    Run a command in the shell and return the result

    :param command: the command to run, ``str``
    :return: the stdout, stderr and return code of the command, ``Tuple[str, str, int]``
    """
    result = subprocess.run(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    return_code = result.returncode
    msg(
        level="debug",
        message=f"Command executed: {command}. Command output: {stdout}. Error received: {stderr}. Return code: {return_code}",
    )
    return stdout, stderr, return_code
