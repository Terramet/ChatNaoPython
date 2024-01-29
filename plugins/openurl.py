# import webbrowser
# import json
# func_desc = {
#                 "name": "openurl",
#                 "description": "Open webpage in browser at the given URL",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "url": {
#                             "type": "string",
#                             "description": "The webpage url"
#                         },
#                         "unit": {"type": "string"}
#                     },
#                     "required": ["url"],
#                 },
#             }
# # Example command function for opening a URL
# def command_openurl(arguments):
#     try:
#         args = json.loads(arguments)
#         if "url" in args:
#             url = args["url"]
#             print(f"Opening URL: {url}")
#             webbrowser.open(url)
#             return (f"URL: {url} opened successfully.")
#     except:
#         return (f"Opening URL: {url} failed.")

# def register(function_manager):
#     function_manager.register_command("openurl", command_openurl)
#     function_manager.register_function_with_gpt(func_desc)