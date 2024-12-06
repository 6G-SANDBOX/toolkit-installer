import base64

from ruamel.yaml import YAML
from io import StringIO

from ansible.parsing.vault import VaultLib, VaultSecret
from ansible.constants import DEFAULT_VAULT_ID_MATCH

from phases.utils.logs import msg

def object_yaml(data: dict) -> str:
    """
    Convert a dictionary to a YAML string

    :param data: the dictionary to be converted, ``dict``
    :return: the YAML string, ``str``
    """
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.preserve_quotes = True
    buffer = StringIO()
    yaml.dump(data, buffer)
    return buffer.getvalue()

def encode_base64(data: str) -> str:
    """
    Encode a string to Base64

    :param data: the string to be encoded, ``str``
    :return: the Base64 encoded string, ``str``
    """
    return base64.b64encode(data.encode("utf-8")).decode("utf-8")

def decode_base64(encoded_data: str) -> str:
    """
    Decode a Base64 encoded string

    :param encoded_data: the Base64 encoded string to be decoded, ``str``
    :return: the decoded data as bytes, ``str``
    """
    return base64.b64decode(encoded_data).decode("utf-8")

def ansible_encrypt(data: str, token_path: str) -> None:
    """
    Encrypt a file using Ansible Vault

    :param encrypted_data: the data to be encrypted, ``str``
    :param token_path: the path to the token file, ``str``
    """
    msg("info", f"Encrypting data using Ansible Vault")
    secret = token_path.encode("utf-8")
    vault = VaultLib([(DEFAULT_VAULT_ID_MATCH, VaultSecret(secret))])
    msg("info", "Data encrypted")
    return vault.encrypt(data)

def ansible_decrypt(encrypted_data: str, password: str) -> None:
    """
    Decrypt a file using Ansible Vault

    :param encrypted_data: the data to be decrypted, ``str``
    :param token_path: the path to the token file, ``str``
    """
    msg("info", "Decrypting data using Ansible Vault")
    secret = password.encode("utf-8")
    vault = VaultLib([(DEFAULT_VAULT_ID_MATCH, VaultSecret(secret))])
    msg("info", "Data decrypted")
    return vault.decrypt(encrypted_data)