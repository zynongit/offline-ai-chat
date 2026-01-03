import os
os.environ["KIVY_NO_MTDEV"] = "1"

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty

from core.llama_engine import LlamaEngine
from core.memory import load_memory, save_memory


class ChatLayout(BoxLayout):
    chat_text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.engine = LlamaEngine()
        self.memory = load_memory()

        for msg in self.memory:
            self.chat_text += msg + "\n"

    def send_message(self):
        user_input = self.ids.user_input.text.strip()
        if not user_input:
            return

        self.chat_text += f"You: {user_input}\n"
        self.ids.user_input.text = ""

        prompt = "\n".join(self.memory + [f"User: {user_input}", "AI:"])
        response = self.engine.generate(prompt)

        self.chat_text += f"AI: {response}\n\n"

        self.memory.append(f"User: {user_input}")
        self.memory.append(f"AI: {response}")
        save_memory(self.memory)


class OfflineAIChatApp(App):
    def build(self):
        return ChatLayout()


if __name__ == "__main__":
    OfflineAIChatApp().run()
