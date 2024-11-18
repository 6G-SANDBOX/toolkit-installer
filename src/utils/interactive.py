import questionary

from typing import List, Optional

def ask_text(prompt: str, default: Optional[str] = None) -> str:
    """
    Prompt the user for text input

    :param prompt: the question to display, ``str``
    :param default: default value if the user presses Enter, ``Optional[str]``
    :return: user input, ``str``
    """
    return questionary.text(prompt, default=default).ask()

def ask_select(prompt: str, choices: List[str]) -> str:
    """
    Prompt the user to select one option from a list

    :param prompt: the question to display, ``str``
    :param choices: list of options to choose from, ``List[str]``
    :return: selected option, ``str``
    """
    return questionary.select(prompt, choices=choices).ask()

def ask_checkbox(prompt: str, choices: List[str]) -> List[str]:
    """
    Prompt the user to select multiple options from a list

    :param prompt: the question to display, ``str``
    :param choices: list of options to choose from, ``List[str]``
    :return: list of selected options, ``List[str]``
    """
    return questionary.checkbox(prompt, choices=choices).ask()

def ask_confirm(prompt: str, default: bool = True) -> bool:
    """
    Prompt the user for a yes/no confirmation

    :param prompt: the question to display, ``str``
    :param default: default response if the user presses Enter, ``bool``
    :return: user's confirmation, ``bool``
    """
    return questionary.confirm(prompt, default=default).ask()

def ask_password(prompt: str) -> str:
    """
    Prompt the user to enter a password (hidden input)

    :param prompt: the question to display, ``str``
    :return: user input, ``str``
    """
    return questionary.password(prompt).ask()