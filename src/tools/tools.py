from tools.calculator.calculator import calculate
from tools.weather.weather import get_weather

DEFAULT_TOOLS = {
    "calculate": calculate,
    "weather": get_weather,
}

ADMIN_TOOL = {
    "calculate": calculate,
    "weather": get_weather,
}
