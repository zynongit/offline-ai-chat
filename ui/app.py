import os
os.environ["KIVY_NO_MTDEV"] = "1"

from threading import Thread
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty
from kivy.utils import get_color_from_hex as hex

from core.llama_engine import LlamaEngine
from core.memory import load_memory, save_memory


class ChatLayout(BoxLayout):
    chat_text = StringProperty("")
    typing_text = StringProperty("")
    is_typing = BooleanProperty(False)
    cursor = StringProperty("")
    cursor_visible = BooleanProperty(False)
    dark_theme = {
        "bg_window": hex("#1e1e1e"),
        "fg_text": hex("#f0f0f0"),
        "bg_input": hex("#2a2a2a"),
        "fg_input": hex("#ffffff"),
        "bg_button": hex("#333333"),
        "fg_button": hex("#ffffff"),
        "fg_typing": hex("#aaaaaa")
    }

    light_theme = {
        "bg_window": hex("#f5f5f5"),
        "fg_text": hex("#000000"),
        "bg_input": hex("#ffffff"),
        "fg_input": hex("#000000"),
        "bg_button": hex("#dddddd"),
        "fg_button": hex("#000000"),
        "fg_typing": hex("#555555")
    }

    # propriedades Kivy (automatic bind)
    bg_window = dark_theme["bg_window"]
    fg_text = dark_theme["fg_text"]
    bg_input = dark_theme["bg_input"]
    fg_input = dark_theme["fg_input"]
    bg_button = dark_theme["bg_button"]
    fg_button = dark_theme["fg_button"]
    fg_typing = dark_theme["fg_typing"]

    current_theme = "dark"

    def toggle_theme(self):
        if self.current_theme == "dark":
            theme = light_theme
            self.current_theme = "light"
        else:
            theme = dark_theme
            self.current_theme = "dark"

        self.bg_window = theme["bg_window"]
        self.fg_text = theme["fg_text"]
        self.bg_input = theme["bg_input"]
        self.fg_input = theme["fg_input"]
        self.bg_button = theme["bg_button"]
        self.fg_button = theme["fg_button"]
        self.fg_typing = theme["fg_typing"]

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
