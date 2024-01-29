import requests
import json
from datetime import datetime

func_desc = {
                "name": "getWeather",
                "description": "Get weather information for given location using a city ID for openweathermap.org",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city_id": {
                            "type": "string",
                            "description": "ID for location to get weather information for"
                        },
                        "unit": {"type": "string"}
                    },
                    "required": ["city_id"],
                }
            }

# Example command function for opening a URL
def command_getWeather(arguments):
    with open('weather.key', 'r') as file:
        api_key = file.read().strip()
    args = json.loads(arguments)
    api_url = "http://api.openweathermap.org/data/2.5/weather"  
    params = {  
        "id": args["city_id"],  
        "units": "metric",  
        "appid": api_key  
    }  
    response = requests.get(api_url, params=params)  
    data = response.json()
    return json.dumps(data)  

def register(function_manager):
    function_manager.register_command("getWeather", command_getWeather)
    function_manager.register_function_with_gpt(func_desc)