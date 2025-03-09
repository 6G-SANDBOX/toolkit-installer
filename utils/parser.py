import base64
from typing import Dict

import yaml

from utils.cli import run_command
from utils.logs import msg


def ansible_decrypt(data_path: str, token_path: str) -> None:
    """
    Decrypt a file using Ansible Vault

    :param data_path: the path to the file to be decrypted, ``str``
    :param token_path: the path to the token file, ``str``
    """
    command = f"ansible-vault decrypt {data_path} --vault-password={token_path}"
    stdout, stderr, rc = run_command(command)
    if rc != 0:
        msg(
            level="error",
            message=f"Error decrypting file: {data_path}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"File decrypted successfully: {data_path}. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )


def ansible_encrypt(data_path: str, token_path: str) -> None:
    """
    Encrypt a file using Ansible Vault

    :param data_path: the path to the file to be encrypted, ``str``
    :param token_path: the path to the token file, ``str``
    """
    command = f"ansible-vault encrypt {data_path} --vault-password={token_path}"
    stdout, stderr, rc = run_command(command)
    if rc != 0:
        msg(
            level="error",
            message=f"Error encrypting file: {data_path}. Command executed: {command}. Error received: {stderr}. Return code: {rc}",
        )
    msg(
        level="debug",
        message=f"File encrypted successfully: {data_path}. Command executed: {command}. Output received: {stdout}. Return code: {rc}",
    )


def decode_base64(encoded_data: str) -> str:
    """
    Decode a Base64 encoded string

    :param encoded_data: the Base64 encoded string to be decoded, ``str``
    :return: the decoded data as bytes, ``str``
    """
    return base64.b64decode(encoded_data).decode("utf-8")


def encode_base64(data: str) -> str:
    """
    Encode a string to Base64

    :param data: the string to be encoded, ``str``
    :return: the Base64 encoded string, ``str``
    """
    return base64.b64encode(data.encode("utf-8")).decode("utf-8")


def gb_to_mb(gb: int) -> int:
    """
    Convert gigabytes to megabytes

    :param gb: the value in gigabytes, ``int``
    :return: the value in megabytes, ``int``
    """
    return gb * 1024


def object_to_yaml(data: Dict) -> str:
    """
    Convert a dictionary to a YAML string

    :param data: the dictionary to be converted, ``Dict``
    :return: the YAML string, ``str``
    """
    return yaml.dump(data, default_flow_style=False)
