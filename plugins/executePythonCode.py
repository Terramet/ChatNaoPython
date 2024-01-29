import subprocess
import json
import io
import sys

func_desc = {
                "name": "executePythonCode",
                "description": "Execute given python code, function will return any values that were given from print()'s within the function",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Python code to be executed"
                        },
                        "unit": {"type": "string"}
                    },
                    "required": ["code"],
                },
            }

# Example command function for opening a URL
def command_executePythonCode(arguments):
    try:
        args = json.loads(arguments)
        if "code" in args:
            code = args["code"]
            # create file-like string to capture output
            codeOut = io.StringIO()
            codeErr = io.StringIO()

            # capture output and errors
            sys.stdout = codeOut
            sys.stderr = codeErr

            exec(code)

            # restore stdout and stderr
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

            s = codeErr.getvalue()

            print("error:\n%s\n" % s)

            s = codeOut.getvalue()

            print("output:\n%s" % s)
            return (f"App return result: Output: {codeOut.getvalue()}, Errors: {codeErr.getvalue()}.")
    except:
        return (f"Code execution failed.")

def register(function_manager):
    function_manager.register_command("executePythonCode", command_executePythonCode)
    function_manager.register_function_with_gpt(func_desc)
    # function_manager.register_additional_system_roles(sys_roles)