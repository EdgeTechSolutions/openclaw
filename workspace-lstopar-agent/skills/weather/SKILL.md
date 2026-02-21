# Weather Skill

Fetch **current weather** and **5-day forecasts** using the [OpenWeatherMap API](https://openweathermap.org/api).

---

## Setup

### 1. Get an API Key
1. Sign up at [OpenWeatherMap](https://openweathermap.org/api).
2. Get your **free API key** from the [API keys page](https://home.openweathermap.org/api_keys).

### 2. Configure the Skill
Add your API key to `.env` in your OpenClaw workspace:
```bash
# /home/lstopar/.openclaw/workspace/.env
OPENWEATHERMAP_API_KEY="your_api_key_here"
```

---

## Usage

### Initialize the Skill
```python
from weather import WeatherSkill

weather = WeatherSkill()
```

### Fetch Current Weather
```python
current = weather.get_current_weather("Ljubljana")
print(f"Temperature: {current['main']['temp']}°C")
print(f"Conditions: {current['weather'][0]['description']}")
```

### Fetch 5-Day Forecast
```python
forecast = weather.get_forecast("Ljubljana")
for day in forecast['list'][:5]:  # First 5 entries (3-hour intervals)
    print(f"Date: {day['dt_txt']}, Temp: {day['main']['temp']}°C")
```

---

## Example Output
```json
{
  "coord": {"lon": 14.5, "lat": 46.05},
  "weather": [{"id": 800, "main": "Clear", "description": "clear sky"}],
  "main": {
    "temp": 12.5,
    "feels_like": 11.8,
    "temp_min": 10.0,
    "temp_max": 15.0,
    "pressure": 1012,
    "humidity": 65
  },
  "wind": {"speed": 3.1, "deg": 180},
  "name": "Ljubljana"
}
```

---

## Error Handling
- **Invalid API Key**: `ValueError` if the key is missing or invalid.
- **City Not Found**: `requests.HTTPError` if the city doesn’t exist.

---

## Rate Limits
- Free tier: **60 calls/minute**, **1,000,000 calls/month**.