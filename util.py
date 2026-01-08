import importlib
from concurrent.futures import ThreadPoolExecutor
from google.genai import types
from pathlib import Path

class DiskUtil:

    def read_system_instructions():
        string = ''
        with open("prompt.txt", "r") as f:
            string = f.read()
        return string

    def read_starting_text():
        string = ''
        with open("email.txt", "r") as f:
            string = f.read()
        return string

    def write_program(name, text):
        text = text.replace('```python', '')
        text = text.replace('```', '')
        with open("generated/" + name + ".py", 'w') as f:
            f.write('import math\n')
            f.write('import random\n')
            f.write('from generated.helpers import Render, Input, Sound\n\n')

            f.write(text)

    def get_saved_program_names():
        path = Path("generated")

        files = [f.name[:-3] for f in path.glob('*.py') if f.is_file() and f.name not in {'mesh.py', 'helpers.py', '__init__.py'}]
        return files

class LlmUtil:

    def load_local_program(name):
        module = importlib.import_module("generated." + name)
        return module.Program()

    def load_default_program():
        return LlmUtil.load_local_program("mesh")

    def load_new_program(chat, prompt, name):
        try:
            print("loading program, request: ", prompt)
            response = chat.send_message(prompt)
            print(response)
            DiskUtil.write_program(name, response.text)
            module = importlib.import_module("generated." + name)
            return module.Program()
        except:
            import traceback
            traceback.print_exc()
            return LlmUtil.load_default_program()

    def create_new_chat(client, system_instructions, model="gemini-2.5-flash"):
        return client.chats.create(model=model, config=types.GenerateContentConfig(system_instruction=system_instructions))

    def load_new_program_async(chat, prompt, name):
        executor = ThreadPoolExecutor(max_workers=1)
        return executor.submit(LlmUtil.load_new_program, chat, prompt, name)
        
        
        