from typing import Any, Dict, Optional

from magetools.spell_registry import register_spell

user_name = """Not currently known. Maybe if you ask, the user will tell
 you their name. You can the ask the grimorium for a spell to save the user's name."""


@register_spell
async def log_out_fb() -> Dict[str, Any]:
    """Logs out the currently authenticated user from Facebook.

    This function will terminate the current Facebook session and require
    re-authentication for subsequent Facebook operations.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - success (bool): Whether the logout was successful
            - data (None): No data returned
            - message (str): Status message indicating the result

    Example:
        >>> log_out_fb()
        {'success': True, 'data': None, 'message': 'You have been logged out of facebook.'}
    """
    return {
        "success": True,
        "data": None,
        "message": "You have been logged out of facebook.",
    }


@register_spell
async def save_user_name(
    first_name: str, last_name: Optional[str] = None
) -> Dict[str, Any]:
    """Saves the name of the currently authenticated user.

    Args:
        first_name (str): The user's first name
        last_name (str): The user's last name

    Returns:
        Dict[str, Any]: A dictionary containing:
            - success (bool): Whether the request was successful
            - data (str): The user's full name
            - message (str): A summary message.

    Example:
        >>> save_user_name("John", "Doe")
        {'success': True, 'data': 'John Doe', 'message': 'User name saved successfully as John Doe'}
    """
    global user_name
    user_name = f"{first_name} {last_name}"
    return {
        "success": True,
        "data": user_name,
        "message": f"User name saved successfully as {user_name}",
    }
