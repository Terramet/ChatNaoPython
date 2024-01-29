import subprocess
import json
from threading import Timer

server_url = ''
func_desc = {
                "name": "openAppViaURL",
                "description": "Open application on connected tablet",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "Android will decide which app best suits this url"
                        },
                        "unit": {"type": "string"}
                    },
                    "required": ["url"],
                },
            }

def time_to_seconds(time_str):
    minutes, seconds = map(int, time_str.split(':'))
    total_seconds = minutes * 60 + seconds
    return total_seconds

def reopen_website():
    subprocess.Popen(['adb', 'shell', 'am', 'start', '-a', 'android.intent.action.VIEW', server_url], stdout=subprocess.PIPE)

def run_scheduled_task(time):
    timer = Timer(time, reopen_website)
    timer.start()

# Example command function for opening a URL
def command_openAppViaURL(arguments):
    try:
        args = json.loads(arguments)
        if "url" in args:
            url = args["url"]
            print(f"Opening app using: {url}")
            if url.contains('youtube'):
                ytv = subprocess.Popen(['youtube-dlc', '--skip-download', '--get-duration', url], stdout=subprocess.PIPE)
                out, _ = ytv.communicate()
                # run_scheduled_task(time_to_seconds(out)+10)

            # adb shell am start -a android.intent.action.VIEW "http://www.youtube.com/watch?v=YRhFSWz_J3I"
            result = subprocess.Popen(['adb', 'shell', 'am', 'start', '-a', 'android.intent.action.VIEW', url], stdout=subprocess.PIPE)
            out, _ = result.communicate()
            return (f"App return result: {out}.")
    except:
        return (f"Opening App through {url} failed.")

def register(function_manager):
    function_manager.register_command("openAppViaURL", command_openAppViaURL)
    function_manager.register_function_with_gpt(func_desc)
    # function_manager.register_additional_system_roles(sys_roles)