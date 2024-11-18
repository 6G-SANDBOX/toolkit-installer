import base64

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