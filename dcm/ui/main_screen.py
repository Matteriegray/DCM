from kivymd.uix.screen import MDScreen 

class MainScreen(MDScreen): 
    """ Main application screen with navigation and content """ 
    def __init__(self, **kwargs):
        super().__init__(**kwargs) 
        self.name = 'main_screen' 