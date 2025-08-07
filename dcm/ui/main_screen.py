from kivymd.uix.screen import MDScreen

class MainScreen(MDScreen):
    """Main application screen with bottom navigation"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'main_screen'
    
    def switch_screen(self, screen_name):
        """Switch between different screens"""
        if hasattr(self.ids, 'screen_manager'):
            self.ids.screen_manager.current = screen_name
            print(f"Switched to screen: {screen_name}")
            
            # Handle any screen-specific initialization
            if screen_name == 'playlists_screen':
                print("Loading playlists...")
            elif screen_name == 'library_screen':
                print("Loading library...")
            elif screen_name == 'generate_screen':
                print("Loading generator...")