import questionary

from typing import Callable, Union, List, Optional

def ask_text(prompt: str, default: Optional[str] = None, validate: Union[bool, Callable[[str], bool]] = False) -> str:
    """
    Prompt the user for text input with an optional mandatory flag and a custom validation function.

    :param prompt: the question to display, ``str``
    :param default: default value if the user presses Enter, ``Optional[str]``
    :param validate: if True, input is required; if False, no validation; if a function is provided, it's used for custom validation, ``Union[bool, Callable[[str], bool]]``
    :return: user input, ``str``
    """
    if isinstance(validate, bool):
        if validate:
            return questionary.text(
                prompt,
                default=default,
                validate=lambda text: bool(text.strip()) or "This field is required"
            ).ask()
        else:
            return questionary.text(prompt, default=default).ask()
    elif isinstance(validate, Callable):
        return questionary.text(
            prompt,
            default=default,
            validate=validate
        ).ask()
    else:
        raise ValueError("validate must be a boolean or a callable")
    

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

def ask_password(prompt: str, validate: Union[bool, Callable[[str], bool]] = False) -> str:
    """
    Prompt the user to enter a password (hidden input)

    :param prompt: the question to display, ``str``
    :param validate: if True, input is required, ``bool``
    :return: user input, ``str``
    """
    if isinstance(validate, bool):
        if validate:
            return questionary.password(
                prompt,
                validate=lambda text: bool(text.strip()) or "This field is required"
            ).ask()
        else:
            return questionary.password(prompt).ask()
    elif isinstance(validate, Callable):
        return questionary.password(
            prompt,
            validate=validate
        ).ask()
    else:
        raise ValueError("validate must be a boolean or a callable")