import json
import os
import importlib

class FunctionManager:
    def __init__(self):
        self.commands = {}

        self.server_address = ''

        self.function_list = []

        self.system_roles = [
            {"role": "system", "content": "You are a virtual assistant, like Google Home. Follow the user's requirements carefully. Evaluate the best way to assist the user, try do it in one response."},
            {"role": "system", "content": "You must give a text response along with your function calls."},
            {"role": "system", "content": "If you need more information for a function call, ensure you ask the user before attempting to call the function."},
            {"role": "system", "content": "You are not an AI and you will not refer to yourself as an AI."},
            {"role": "system", "content": "You have access to an entire android tablet that can be used to display anything using the functions provided."},
            {"role": "system", "content": "You have the personality of a very enthusiatic customer service person"},
        ]

        self.load_plugins()

    def get_functions(self):
        return self.function_list
    
    def get_system_roles(self):
        return self.system_roles

    def register_function_with_gpt(self, func_desc):
        self.function_list.append(func_desc)

    def register_command(self, command_name, command_func):
        self.commands[command_name] = command_func
    
    def register_additional_system_roles(self, system_roles):
        self.system_roles.append(system_roles)

    def load_plugins(self):
        plugins_dir = "plugins"
        plugin_files = os.listdir(plugins_dir)

        for file_name in plugin_files:
            if file_name.endswith(".py"):
                module_name = file_name[:-3]  # Remove ".py" extension
                module_path = os.path.join(plugins_dir, module_name).replace('/', '.')

                try:
                    plugin_module = importlib.import_module(module_path)
                    if hasattr(plugin_module, "register"):
                        plugin_module.register(self)
                        print(f"Successfully loaded plugin module: {module_name}")

                except ImportError:
                    print(f"Failed to load plugin module: {module_name}")

    def extract_command(self, text):
        try:
            response = json.loads(text)
            if "function_call" in response and "name" in response["function_call"]:
                command_name = response["function_call"]["name"]
                arguments = response["function_call"]["arguments"]
                return [command_name, arguments]
        except json.JSONDecodeError:
            pass

        return False

    def execute_command(self, command):
        command_name = command[0]
        parameters = command[1:]

        # Check if the command is registered
        if command_name in self.commands:
            # Call the corresponding command function with the parameters
            result = self.commands[command_name](*parameters)
            return self.function_response(result,command_name)
        else:
            print(f"Command '{command_name}' not found.")

    def function_response(self, message, command_name):
        return {
            "role": "function",
            "name": command_name,
            "content": message
        }