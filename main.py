# main.py
from kivy.app import App
from kivy.uix.label import Label

class OfflineAIChatApp(App):
    def build(self):
        return Label(text="Offline AI Chat")

if __name__ == "__main__":
    OfflineAIChatApp().run()
