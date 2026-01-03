import os
os.environ["KIVY_NO_MTDEV"] = "1"

from threading import Thread
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty

from core.llama_engine import LlamaEngine
from core.memory import load_memory, save_memory


class ChatLayout(BoxLayout):
    chat_text = StringProperty("")
    typing_text = StringProperty("")
    is_typing = BooleanProperty(False)
    cursor = StringProperty("")
    cursor_visible = BooleanProperty(False)


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.engine = LlamaEngine()
        self.memory = load_memory()
        self.stop_flag = False
        self._typing_event = None
        self._typing_dots = 0

        for msg in self.memory:
            self.chat_text += msg + "\n"

    # ---------- UI Actions ----------

    def send_message(self):
        user_input = self.ids.user_input.text.strip()
        if not user_input:
            return

        self.stop_flag = False
        self._start_typing()

        self.chat_text += f"You: {user_input}\nAI: "
        self.ids.user_input.text = ""

        Thread(
            target=self._stream_response,
            args=(user_input,),
            daemon=True
        ).start()

    def stop_generation(self):
        self.stop_flag = True
        self._stop_typing()

    # ---------- Streaming ----------

    def _stream_response(self, user_input):
        prompt = "\n".join(self.memory + [f"User: {user_input}", "AI:"])
        response_text = ""

        for token in self.engine.stream(prompt):
            if self.stop_flag:
                break

            response_text += token
            Clock.schedule_once(
                lambda dt, t=token: self._append_token(t)
            )

        self.memory.append(f"User: {user_input}")
        self.memory.append(f"AI: {response_text}")
        save_memory(self.memory)

        Clock.schedule_once(lambda dt: self._finish_response())

    def _append_token(self, token):
        self.chat_text += token

    def _finish_response(self):
        self.chat_text += "\n\n"
        self._stop_typing()

    # ---------- Typing Indicator ----------

    def _start_typing(self):
        if self._typing_event:
            self._typing_event.cancel()

        self.is_typing = True
        self._typing_dots = 0
        self._typing_event = Clock.schedule_interval(
            self._update_typing_text, 0.4
        )

    def stop_generation(self):
        self.stop_flag = True
        self._stop_typing()


        if self._typing_event:
            self._typing_event.cancel()
            self._typing_event = None

    def _update_typing_text(self, dt):
        self._typing_dots = (self._typing_dots + 1) % 4
        dots = "." * self._typing_dots
        self.typing_text = f"AI is typing{dots}"


class OfflineAIChatApp(App):
    def build(self):
        return ChatLayout()


if __name__ == "__main__":
    OfflineAIChatApp().run()
