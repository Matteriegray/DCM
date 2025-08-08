from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.utils import platform
from kivy.properties import ListProperty, StringProperty 
from kivy.uix.popup import Popup 
from kivy.uix.boxlayout import BoxLayout  
from kivymd.uix.button import MDFlatButton 
from kivymd.uix.dialog import MDDialog
import os
import sys

# Add the project root to the path to impor thte core models 
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')) 
if project_root not in sys.path:
    sys.path.append(project_root) 

class FileChoosePopup(BoxLayout):
    # Popup for the file selection 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical' 
        self.size_hint = (0.9, 0.9) 
        
class DCMApp(MDApp):
    selected_files = ListProperty([]) 
    playlist_name = StringProperty('') 
    
    def build(self):
        # Set the theme
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Light"
        
        # Set window size for desktop
        if platform not in ('android', 'ios'):
            Window.size = (400, 700)
        
        # Initialize the file manager
        self.file_manager = None 
        self.popup = None 
        
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
    
    def file_manager_open(self):
        # Opens the file manager to select the music files 
        from kivy.uix.filechooser import FileChooserListView 
        from kivy.uix.popup import Popup 
        
        content = FileChoosePopup() 
        file_chooser = FileChooserListView(
            path = os.path.expanduser('~'),
            filters = ['*.mp3', '*.wav', '*.m4a', '*.flac']
        )
        content.add_widget(file_chooser) 
        
        # Add buttons 
        btn_layout = BoxLayout(size_hint_y = 0.1) 
        btn_cancel = MDFlatButton(text = 'Cancel') 
        btn_select = MDFlatButton(text = 'Select', md_bg_color = self.theme_cls.primary_color)
        
        btn_layout.add_widget(btn_cancel)
        btn_layout.add_widget(btn_select) 
        
        # Creat the Popup 
        self.popup = Popup(
            title = "Select the Music FIles", 
            content = content, 
            size_hint = (0.9, 0.9)
        ) 
        
        #Bind the buttons 
        bin_cancel.bind(on_release = self.popup.dismiss) 
        btn_select.bind(on_release = lambda x: self.files_selected(file_chooser.selection, file_chooser.path)) 
        
        self.popup.open() 
         
        

if __name__ == '__main__':
    DCMApp().run()