import base64

from ansible.parsing.vault import VaultLib, VaultSecret
from ansible.constants import DEFAULT_VAULT_ID_MATCH

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
    secret = token_path.encode("utf-8")
    vault = VaultLib([(DEFAULT_VAULT_ID_MATCH, VaultSecret(secret))])
    return vault.encrypt(data)

def ansible_decrypt(encrypted_data: str, password: str) -> None:
    """
    Decrypt a file using Ansible Vault

    :param encrypted_data: the data to be decrypted, ``str``
    :param token_path: the path to the token file, ``str``
    """
    secret = password.encode("utf-8")
    vault = VaultLib([(DEFAULT_VAULT_ID_MATCH, VaultSecret(secret))])
    return vault.decrypt(encrypted_data)