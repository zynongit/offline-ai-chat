import os
os.environ["KIVY_NO_MTDEV"] = "1"

from threading import Thread
from kivy.app import App
from kivy.clock import Clock
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

        self.chat_text += f"You: {user_input}\nAI: "
        self.ids.user_input.text = ""

        Thread(
            target=self._stream_response,
            args=(user_input,),
            daemon=True
        ).start()

    def _stream_response(self, user_input):
        prompt = "\n".join(self.memory + [f"User: {user_input}", "AI:"])
        response_text = ""

        for token in self.engine.stream(prompt):
            response_text += token
            Clock.schedule_once(
                lambda dt, t=token: self._append_token(t)
            )

        self.memory.append(f"User: {user_input}")
        self.memory.append(f"AI: {response_text}")
        save_memory(self.memory)

        Clock.schedule_once(lambda dt: self._append_token("\n\n"))

    def _append_token(self, token):
        self.chat_text += token


class OfflineAIChatApp(App):
    def build(self):
        return ChatLayout()


if __name__ == "__main__":
    OfflineAIChatApp().run()
