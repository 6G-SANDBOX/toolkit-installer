import subprocess

def run_command(command: str) -> dict:
    """
    Run a command in the shell and return the result
    
    :param command: the command to run, ``str``
    :return: a tuple containing stdout, stderr, and return code, ``dict``
    
    Example use:
    res = run_command("echo hello!")
    if res["rc"] == 0:
        print("it worked")
    """
    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        return_code = result.returncode
        return {"rc": return_code, "stdout": stdout, "stderr": stderr}
    except Exception as e:
        return {"rc": -1, "stdout": None, "stderr": str(e)}