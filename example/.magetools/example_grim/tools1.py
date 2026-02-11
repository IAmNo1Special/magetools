from typing import Any, Dict, Optional

from magetools import spell

from ..example_book.tools2 import user_name

@spell
async def get_user_location() -> Dict[str, Any]:
    """Gets the user's current city and country.

    Returns:
        Dict[str, Any]: A dictionary containing location details:
            - success (bool): Whether the request was successful
            - data (dict): A dictionary with location data (city, country, etc.)
            - message (str): A summary message.

    Example:
        >>> await get_user_location()
        {'success': True, 'data': {'city': 'Raleigh', ...}, 'message': 'Your current location is Raleigh, United States.'}
    """

    return {
        "success": True,
        "data": {"city": "Raleigh", "country": "United States"},
        "message": "Your current location is Raleigh, United States.",
    }


@spell
async def weather_forecast(city: Optional[str] = None) -> Dict[str, Any]:
    """Gets the current weather forecast for a specified city.
    If no city is provided, the user's current location will be used.


    Args:
        city (Optional[str]): The city for which to fetch the weather forecast. If not provided, the user's location will be used.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - success (bool): Whether the request was successful
            - data (dict): A dictionary with weather data (city, temperature, description, etc.)
            - message (str): A summary message.

    Example:
        >>> await weather_forecast("Raleigh")
        {'success': True, 'data': {'city': 'Raleigh', ...}, 'message': 'The current weather in Raleigh is sunny with a temperature of 72F.'}
        >>> await weather_forecast()
        {'success': True, 'data': {'city': 'Raleigh', ...}, 'message': 'The current weather in Raleigh is sunny with a temperature of 72F.'}
    """
    if city is None:
        result = await get_user_location()
        city = str(
            result.get("data", {}).get("city", "Unknown")
        )  # ideally use get_user_location to get the user's city
    weather_data = {"city": city, "temperature": 72, "description": "sunny"}
    return {
        "success": True,
        "data": weather_data,
        "message": f"The current weather in {city} is {weather_data.get('description')} with a temperature of {weather_data.get('temperature')}F.",
    }


@spell
async def get_user_name() -> Dict[str, Any]:
    """Retrieves the name of the currently authenticated user.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - success (bool): Whether the request was successful
            - data (str): The user's full name
            - message (str): A summary message.

    Example:
        >>> get_user_name()
        {'success': True, 'data': 'John Doe', 'message': 'User name is John Doe'}
    """
    return {"success": True, "data": user_name, "message": f"User name is {user_name}"}
