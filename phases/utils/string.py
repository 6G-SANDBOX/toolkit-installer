def validate_length(value: str, max_length: int) -> str | bool:
    """
    Validate the length of the value and return an error message if invalid.

    :param value: the value, ``str``
    :param max_length: the maximum length, ``int``
    :return: error message if invalid, otherwise an empty string, ``str`` or ``bool``
    """
    if len(value) < max_length:
        return f"The value must be at least {max_length} characters long"
    return True