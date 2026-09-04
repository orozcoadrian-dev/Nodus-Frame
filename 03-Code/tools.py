"""Safe example tools. Replace or extend these with application capabilities."""


def get_weather(city: str) -> dict[str, str]:
    """Deterministic demo tool; replace with a real provider in production."""
    return {"city": city, "temperature": "18 C", "weather": "sunny"}


WEATHER_TOOL = {
    "name": "get_weather",
    "description": "Obtiene el clima actual de una ciudad.",
    "parameters": {
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"],
    },
    "function": get_weather,
}