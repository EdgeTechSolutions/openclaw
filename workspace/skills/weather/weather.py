"""
Weather Skill - Fetch weather data using OpenWeatherMap API.
"""

import os
import requests
from typing import Dict, Optional
from dotenv import load_dotenv


class WeatherSkill:
    """Skill to fetch weather data from OpenWeatherMap."""

    BASE_URL = "https://api.openweathermap.org/data/2.5"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the WeatherSkill with an OpenWeatherMap API key.
        
        Args:
            api_key: OpenWeatherMap API key. Defaults to OPENWEATHERMAP_API_KEY.
        """
        load_dotenv()
        self.api_key = api_key or os.getenv("OPENWEATHERMAP_API_KEY")
        if not self.api_key:
            raise ValueError("OpenWeatherMap API key not found. Set OPENWEATHERMAP_API_KEY.")

    def get_current_weather(self, city: str, units: str = "metric") -> Dict:
        """
        Fetch current weather for a city.
        
        Args:
            city: City name (e.g., "Ljubljana").
            units: Units ("metric", "imperial", or "standard"). Defaults to "metric".
            
        Returns:
            Dictionary with weather data (temperature, humidity, conditions, etc.).
        """
        url = f"{self.BASE_URL}/weather"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": units,
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_forecast(self, city: str, units: str = "metric") -> Dict:
        """
        Fetch 5-day weather forecast for a city.
        
        Args:
            city: City name (e.g., "Ljubljana").
            units: Units ("metric", "imperial", or "standard"). Defaults to "metric".
            
        Returns:
            Dictionary with forecast data.
        """
        url = f"{self.BASE_URL}/forecast"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": units,
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()