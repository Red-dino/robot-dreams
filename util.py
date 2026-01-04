import importlib
from google.genai import types

class DiskUtil:

    def read_system_instructions():
        string = ''
        with open("prompt.txt", "r") as f:
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

class LlmUtil:

    def load_default_program():
        module = importlib.import_module("generated.noise")
        return module.Program()

    def load_new_program(chat, prompt, name):
        try:
            response = chat.send_message(prompt)
            DiskUtil.write_program(name, response.text)
            module = importlib.import_module("generated." + name)
            return module.Program()
        except:
            import traceback
            traceback.print_exc()
            return LlmUtil.load_default_program()

    def create_new_chat(client, system_instructions, model="gemini-2.5-flash"):
        return client.chats.create(model=model, config=types.GenerateContentConfig(system_instruction=system_instructions))
