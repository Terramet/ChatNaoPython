import requests
import json
from datetime import datetime

func_desc = {
                "name": "getTime",
                "description": "Get current time for a specific timezone.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "format": {
                            "type": "string",
                            "description": "The format string for the time, for example: %Y-%m-%d %H:%M:%S %Z"
                        }
                    },
                    "required": ["format"],
                },
            }

def command_getTime(arguments):
    args = json.loads(arguments)
    format = args["format"]

    current_time = datetime.now()
    time_str = current_time.strftime(format)
    
    result = {
        "current_time": time_str
    }

    return json.dumps(result)

def register(function_manager):
    function_manager.register_command("getTime", command_getTime)
    function_manager.register_function_with_gpt(func_desc)