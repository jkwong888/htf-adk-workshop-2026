from datetime import datetime
from google.adk.agents.readonly_context import ReadonlyContext
import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel

# We use the Agent class which allows using the OpenAPIToolset toolset
from google.adk.agents.llm_agent import Agent
from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset

# Load environment variables
load_dotenv()

OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY", "")

openapi_spec_dict = {
    "openapi": "3.0.0",
    "info": {
        "title": "OpenWeatherMap API",
        "version": "1.0.0",
        "description": "API for fetching current, future, and historical weather data."
    },
    "servers": [
        {
            "url": "https://api.openweathermap.org",
            "description": "OpenWeatherMap API server"
        }
    ],
    "paths": {
        "/geo/1.0/direct": {
            "get": {
                "operationId": "geocodeLocation",
                "summary": "Get latitude and longitude for a city name",
                "parameters": [
                    {
                        "name": "q",
                        "in": "query",
                        "description": "City name, state code, and country code divided by comma",
                        "required": True,
                        "schema": {"type": "string"}
                    },
                    {
                        "name": "limit",
                        "in": "query",
                        "description": "Number of locations to return",
                        "required": False,
                        "schema": {"type": "integer"}
                    },
                    {
                        "name": "appid",
                        "in": "query",
                        "description": "API key",
                        "required": True,
                        "schema": {"type": "string"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Geocoding response",
                        "content": {"application/json": {"schema": {"type": "array"}}}
                    }
                }
            }
        },
        "/data/3.0/onecall": {
            "get": {
                "operationId": "getOneCallWeather",
                "summary": "Get current and future weather data",
                "parameters": [
                    {
                        "name": "lat",
                        "in": "query",
                        "required": True,
                        "schema": {"type": "number"}
                    },
                    {
                        "name": "lon",
                        "in": "query",
                        "required": True,
                        "schema": {"type": "number"}
                    },
                    {
                        "name": "exclude",
                        "in": "query",
                        "description": "Parts of the response to exclude (e.g., current,minutely,hourly,daily,alerts)",
                        "required": False,
                        "schema": {"type": "string"}
                    },
                    {
                        "name": "units",
                        "in": "query",
                        "description": "Units of measurement (standard, metric, imperial)",
                        "required": False,
                        "schema": {"type": "string"}
                    },
                    {
                        "name": "appid",
                        "in": "query",
                        "description": "API key",
                        "required": True,
                        "schema": {"type": "string"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Weather data response",
                        "content": {"application/json": {"schema": {"type": "object"}}}
                    }
                }
            }
        },
        "/data/3.0/onecall/timemachine": {
            "get": {
                "operationId": "getHistoricalWeather",
                "summary": "Get historical weather data",
                "parameters": [
                    {
                        "name": "lat",
                        "in": "query",
                        "required": True,
                        "schema": {"type": "number"}
                    },
                    {
                        "name": "lon",
                        "in": "query",
                        "required": True,
                        "schema": {"type": "number"}
                    },
                    {
                        "name": "dt",
                        "in": "query",
                        "description": "Unix timestamp in seconds for historical data",
                        "required": True,
                        "schema": {"type": "integer"}
                    },
                    {
                        "name": "units",
                        "in": "query",
                        "description": "Units of measurement (standard, metric, imperial)",
                        "required": False,
                        "schema": {"type": "string"}
                    },
                    {
                        "name": "appid",
                        "in": "query",
                        "description": "API key",
                        "required": True,
                        "schema": {"type": "string"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Historical weather data response",
                        "content": {"application/json": {"schema": {"type": "object"}}}
                    }
                }
            }
        }
    }
}

weather_toolset = OpenAPIToolset(
    spec_str=json.dumps(openapi_spec_dict),
    spec_str_type="json"
)


# return a custom templated instruction using the agent context
def weather_instruction_provider(context: ReadonlyContext) -> str:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")
    instruction = f"""You are a helpful weather assistant. You provide current, future, and historical weather information.

    Current date and time is {current_time}.

    To fulfill requests:
    1. Always translate the location name into latitude and longitude by using the `geocodeLocation` tool.
    2. Given the coordinates, use `getOneCallWeather` for current or future weather. For historical weather, use `getHistoricalWeather`.
    
    If the user doesn't provide a date, use the current date.
    If the user doesn't provide units, use metric.
    If the user doesn't specify the timeframe for the weather, use the current weather. 
    Always include today's high temperature, low temperature,and weather conditions in the response.

    For EVERY OpenWeatherMap API call you make, you must include the `appid` query parameter with the following exact API key value: '{OPENWEATHERMAP_API_KEY}'.
    If this API key is missing or empty, ask the user to configure OPENWEATHERMAP_API_KEY in the .env file.
    Do not print the API key in the response to the user.
    """

    return instruction


# structured output

class WeatherItem(BaseModel):
    date: str
    high_temp: float
    low_temp: float
    weather_conditions: str 

class WeatherResponse(BaseModel):
    location: str
    weather_items: list[WeatherItem]

class WeatherAgent(Agent):
    def __init__(self):
        super().__init__(
            model='gemini-2.5-flash',
            name='weather_agent',
            description='A weather assistant using OpenWeatherMap tools.',
    instruction=weather_instruction_provider,
    tools=[weather_toolset],
    output_schema=WeatherResponse
)



root_agent = WeatherAgent()
