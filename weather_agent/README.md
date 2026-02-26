# Weather Agent

A specialized AI assistant that provides current, future, and historical weather information by integrating with the OpenWeatherMap API using the Google Agent Development Kit (ADK).

## Features

- **Geocoding:** Resolves city names, state codes, and country codes to geographic coordinates.
- **Current & Forecast Data:** Provides comprehensive weather reports including daily high/low temperatures and conditions.
- **Historical Weather:** Retrieves weather data for specific historical dates and times.
- **Structured Output:** Delivers data in a consistent, machine-readable JSON format.

## Architecture

The agent is built using the following components:
- **Model:** `gemini-2.5-flash`
- **Framework:** Google ADK (`google.adk.agents.llm_agent.Agent`)
- **Toolset:** `OpenAPIToolset` configured with a subset of the OpenWeatherMap One Call API 3.0.
- **Data Validation:** Uses Pydantic models for structured output enforcement.

## Prerequisites

1.  **OpenWeatherMap API Key:** Required for fetching data. Get one at [OpenWeatherMap](https://openweathermap.org/api).
2.  **Google API Key:** Required for the Gemini model.

## Setup

1.  Navigate to the `weather_agent` directory.
2.  Create or update your `.env` file with the following variables:
    ```env
    OPENWEATHERMAP_API_KEY=your_open_weather_map_api_key
    GOOGLE_API_KEY=your_google_api_key
    ```

## Usage

### ADK CLI
You can interact with the agent using the ADK CLI:

```bash
# Query current weather
adk run weather_agent --prompt "What's the weather like in New York today?"
```

### Python Client
A sample Python client is provided in `weather_agent_client.py`. To use it, first start the agent server:

```bash
adk api_server weather_agent/agent.py --port 8000
```

Then, run the client:

```bash
# Using command line prompt
python3 weather_agent/weather_agent_client.py --url http://localhost:8000 --prompt "What is the weather in London?"

# Using stdin
echo "What is the weather in Paris?" | python3 weather_agent/weather_agent_client.py --url http://localhost:8000
```

The client will automatically create a new session for each request. You can also specify a custom user ID:

```bash
python3 weather_agent/weather_agent_client.py --url http://localhost:8000 --prompt "..." --user-id my_custom_user
```

## Response Format

The agent returns a structured JSON object containing:
- `location`: The name of the city/location requested.
- `weather_items`: A list of weather records, each containing:
  - `date`: The date of the weather record (YYYY-MM-DD).
  - `high_temp`: The maximum temperature for that day.
  - `low_temp`: The minimum temperature for that day.
  - `weather_conditions`: A brief description of the weather (e.g., "clear sky", "light rain").

### Sample Output

For the prompt: *"What is the weather in Paris for the next 2 days?"*

```json
{
  "location": "Paris",
  "weather_items": [
    {
      "date": "2024-05-20",
      "high_temp": 22.5,
      "low_temp": 14.2,
      "weather_conditions": "partly cloudy"
    },
    {
      "date": "2024-05-21",
      "high_temp": 19.8,
      "low_temp": 13.5,
      "weather_conditions": "light rain"
    }
  ]
}
```

## Configuration Defaults

- **Units:** Metric (Celsius) by default.
- **Timeframe:** Current weather if not specified.
- **Coordinates:** Automatically handled via the `geocodeLocation` tool.
