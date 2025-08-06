from kivymd.app import MDApp 
from kivy.lang import Builder 
from kivy.core.window import Window 

class DCMApp(MDApp): 
    def build(self):
        self.theme_cls.primary_palette = "Text" 
        self.theme_cls.theme_style = 'Dark' 
        self.title = 'DCM Playlist generator' 
        return Builder.load_file('dcm/ui/main.kv') 

if __name__ == '__main__':
    DCMApp().run() 
    