from questionary import checkbox, confirm, password, select, text, Style
from typing import Any, List

style = Style(
    [
        ("qmark", "fg:#ff7700 bold"),
        ("question", "fg:#00ffcc bold"),
        ("answer", "fg:#ffff00 bold"),
        ("pointer", "fg:#ff7700 bold"),
        ("highlighted", "fg:#ff7700 bold underline"),
    ]
)

# def ask_checkbox(prompt: str, choices: Any) -> Any:
#     """
#     Prompt the user to select multiple options from a list

#     :param prompt: the question to display, ``str``
#     :param choices: list of options to choose from, ``List[str]``
#     :return: list of selected options, ``List[str]``
#     """
#     try:
#         return checkbox(prompt, choices=choices).unsafe_ask()
#     except KeyboardInterrupt:
#         print("\nOperation interrupted by user")


def ask_confirm(message: str, default: str = "") -> bool:
    """
    Prompt the user to confirm an action

    :param message: the question to display, ``str``
    :param default: default value if the user presses Enter, ``bool``
    :return: user input, ``bool``
    """
    return confirm(
        message=message, default=default, qmark="🔹", style=style
    ).unsafe_ask()


def ask_password(message: str, default: str = "", validate: Any = None) -> str:
    """
    Prompt the user to enter a password (hidden input)

    :param message: the question to display, ``str``
    :param default: default value if the user presses Enter, ``str``
    :param validate: custom validation function, ``Any``
    :return: user input, ``str``
    """
    return password(
        message=message, default=default, validate=validate, qmark="🔹", style=style
    ).unsafe_ask()


def ask_select(message: str, choices: List[str]) -> str:
    """
    Prompt the user to select one option from a list

    :param prompt: the question to display, ``str``
    :param choices: list of options to choose from, ``List[str]``
    :return: selected option, ``str``
    """
    return select(
        message=message, choices=choices, qmark="🔹", style=style
    ).unsafe_ask()


def ask_text(message: str, default: str = "", validate: Any = None) -> str:
    """
    Prompt the user for text input with an optional mandatory flag and a custom validation function.

    :param message: the question to display, ``str``
    :param default: default value if the user presses Enter, ``str``
    :param validate: custom validation function, ``Any``
    :return: user input, ``str``
    """
    return text(
        message=message, default=default, validate=validate, qmark="🔹", style=style
    ).unsafe_ask()
