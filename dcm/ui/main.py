import sys 
from pathlib import Path 
sys.path.append(str(Path(__file__).parent.parent.parent)) 
from kivymd.app import MDApp 
from kivy.lang import Builder 
from kivy.core.window import Window 
import os  

# Import the MainScreen class 
from dcm.ui.main_screen import MainScreen  

from kivy.utils import platform 
# Setting the window size based on platform 
if platform in ['win', 'linux', 'macosx', 'unknown']:
    Window.size = (800, 600) 
    
    Window.mininum_width, Window.mininum_height = Window.size 
else:
    # App will take full screen on Mobile 
    from kivy.config import Config 
    Config.set('kivy', 'exit_on_escape', '0') 
    from kivy.core.window import Window 
    Window.maximize() 
    
class DCMApp(MDApp): 
    def build(self):
        self.theme_cls.primary_palette = "Teal" 
        self.theme_cls.theme_style = 'Dark' 
        self.title = 'DCM Playlist Generator' 
        
        # Load the KV file 
        kv_path = os.path.join(os.path.dirname(__file__), 'main.kv')
        Builder.load_file(kv_path) 
        
        # Create and return mai screen 
        return MainScreen() 

if __name__ == '__main__':
    DCMApp().run() 
    
