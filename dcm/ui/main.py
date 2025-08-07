from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.utils import platform
import os

class DCMApp(MDApp):
    def build(self):
        # Set the theme
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Light"
        
        # Set window size for desktop
        if platform not in ('android', 'ios'):
            Window.size = (400, 700)
        
        # Load the KV file
        kv_path = os.path.join(os.path.dirname(__file__), 'main.kv')
        if os.path.exists(kv_path):
            Builder.load_file(kv_path)
        else:
            print(f"Error: KV file not found at {kv_path}")
        
        # Import and return the main screen
        from .main_screen import MainScreen
        return MainScreen()

    def on_start(self):
        """Called when the application is starting up"""
        print("DCM Playlist Generator started")

if __name__ == '__main__':
    DCMApp().run()