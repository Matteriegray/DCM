import os
import sys
import platform

# Kivy imports
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ListProperty, StringProperty, ObjectProperty
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.filechooser import FileChooserListView

# KivyMD imports
from kivymd.app import MDApp
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText, MDListItemLeadingIcon
from kivymd.uix.label import MDLabel
from kivymd.uix.filemanager import MDFileManager

# Add the project root to the path to import the core models 
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
    
    def __init__(self, **kwargs):
        super(DCMApp, self).__init__(**kwargs)
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primaryColor = [0.13, 0.59, 0.95, 1]  # RGB for #2196F3 (Blue 500)
        # Force text color to be visible on buttons
        self.theme_cls.text_color = [0, 0, 0, 1]  # Black text
        self.theme_cls.primary_text_color = [0, 0, 0, 1]  # Black primary text
        self.theme_cls.accent_text_color = [1, 1, 1, 1]  # White accent text
        
        # Initialize selected song
        self.selected_song = None
        self.recommended_songs = []

    def build(self):
        # Set window size for desktop
        if platform not in ('android', 'ios'):
            Window.size = (450, 800)  # Slightly larger window
            Window.minimum_width, Window.minimum_height = 400, 700
        
        # Load the KV file
        kv_path = os.path.join(os.path.dirname(__file__), 'main.kv')
        if os.path.exists(kv_path):
            Builder.load_file(kv_path)
        else:
            print(f"Error: KV file not found at {kv_path}")
        
        # Set window background color
        from kivy.utils import get_color_from_hex
        Window.clearcolor = get_color_from_hex('#f5f5f5')  # Light gray background
        
        # Create and return the main screen
        # The MainScreen is defined in the KV file and will be automatically instantiated
        return Builder.load_string('''
#:import MainScreen dcm.ui.main_screen.MainScreen

MainScreen:
    id: main_screen
    name: 'main_screen'
''')

    def exit_manager(self, *args):
        """Called when the file manager is closed"""
        self.file_manager.close()

    def select_path(self, path):
        """Handle the selected file path"""
        self.exit_manager()
        if path:
            if isinstance(path, list):
                self.selected_files.extend(path)
            else:
                self.selected_files.append(path)
            self.show_snackbar(f"Selected {len(self.selected_files)} files")

    def on_start(self):
        """Called when the application is starting up"""
        print("DCM Playlist Generator started")
        
        def set_initial_screen(dt):
            """Set the initial screen after the UI is fully loaded"""
            try:
                # Access the screen manager through the root widget
                if hasattr(self, 'root') and hasattr(self.root, 'ids'):
                    if 'screen_manager' in self.root.ids:
                        self.root.ids.screen_manager.current = 'recommend_screen'
                        return
                    
                    # Try to find the screen manager by walking the widget tree
                    for widget in self.root.walk():
                        if hasattr(widget, 'id') and widget.id == 'screen_manager':
                            widget.current = 'recommend_screen'
                            return
                
                print("Warning: Could not find or access screen manager")
                
                # As a fallback, try to switch screens using the MainScreen method
                if hasattr(self.root, 'switch_screen'):
                    self.root.switch_screen('recommend_screen')
                    
            except Exception as e:
                print(f"Error in set_initial_screen: {str(e)}")
        
        # Schedule the screen change to happen after the UI is fully loaded
        Clock.schedule_once(set_initial_screen, 0.5)  # Slightly longer delay to ensure UI is ready
        
    def generate_playlist(self):
        """Handle the generate playlist button click"""
        print("Generate playlist button clicked")
        
        # Check if we're in song-based or genre-based mode
        if hasattr(self.root, 'ids') and 'screen_manager' in self.root.ids:
            current_screen = self.root.ids.screen_manager.current
            
            if current_screen == 'recommend_screen':
                # Song-based recommendations (Spotify-like)
                if not self.selected_song:
                    self.show_error_dialog("No Song Selected", "Please select a song to get recommendations.")
                    return
                
                # Show a message that recommendations are being generated
                self.show_snackbar(f"Finding songs similar to {os.path.basename(self.selected_song)}...")
                
                # Here you would call your model to get similar songs
                # For now, we'll simulate it with a delay
                Clock.schedule_once(lambda dt: self.simulate_recommendations(), 2.0)
                
            elif current_screen == 'generate_screen':
                # Genre/mood-based playlist generation
                # Get the selected mood (for genre-based playlists)
                mood = self.get_selected_mood()
                
                # Check if we have selected files
                if not self.selected_files:
                    self.show_error_dialog("No Files Selected", "Please select at least one music file.")
                    return
                    
                # Show a message that playlist generation is in progress
                self.show_snackbar(f"Generating {mood} playlist with {len(self.selected_files)} files...")
                
                # Here you would call your playlist generation logic
                # For now, we'll just simulate it with a delay
                Clock.schedule_once(lambda dt: self.on_playlist_generated(), 2.0)
        
    def on_playlist_generated(self):
        """Callback when playlist generation is complete"""
        self.show_snackbar("Playlist generated successfully!")
        # Here you would update the UI with the generated playlist
        # For now, we'll just print a message
        print("Playlist generated successfully!")

    def file_manager_open(self):
        # Create a popup for file selection
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Set a default directory that should exist
        default_dir = os.path.expanduser('~')
        music_dir = os.path.join(default_dir, 'Music')
        
        # Use Music directory if it exists, otherwise use home directory
        start_path = music_dir if os.path.exists(music_dir) else default_dir
        
        # Create file chooser
        file_chooser = FileChooserListView(
            path=start_path,
            filters=['*.mp3', '*.wav', '*.m4a', '*.flac'],
            multiselect=False
        )
        
        # Create buttons
        btn_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        btn_select = Button(
            text='Select',
            background_color=(0.13, 0.59, 0.95, 1),
            color=(1, 1, 1, 1),
            bold=True
        )
        
        btn_cancel = Button(
            text='Cancel',
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            bold=True
        )
        
        # Add widgets to layout
        content.add_widget(file_chooser)
        btn_box.add_widget(btn_select)
        btn_box.add_widget(btn_cancel)
        content.add_widget(btn_box)
        
        # Create and configure popup
        popup = Popup(
            title='Select Music File',
            content=content,
            size_hint=(0.9, 0.9)
        )
        
        # Button actions
        def select_files(instance):
            if file_chooser.selection:
                self.selected_song = file_chooser.selection[0]
                song_name = os.path.basename(self.selected_song)
                
                # Update the selected song label
                if hasattr(self, 'root') and hasattr(self.root, 'ids'):
                    if 'selected_song_label' in self.root.ids:
                        self.root.ids.selected_song_label.text = song_name
                
                # In a real app, you would call your recommendation engine here
                # For now, we'll simulate some recommendations
                self.simulate_recommendations()
                
                self.show_snackbar(f"Selected: {song_name}")
            popup.dismiss()
            
        btn_select.bind(on_release=select_files)
        btn_cancel.bind(on_release=lambda x: popup.dismiss())
        
        # Open the popup
        popup.open()
    
    def files_selected(self, selection, path):
        """Handle selected song file"""
        if selection:
            # For now, just take the first selected file
            self.selected_song = selection[0]
            song_name = os.path.basename(self.selected_song)
            
            # Update the selected song label
            if hasattr(self, 'root') and hasattr(self.root, 'ids'):
                if 'selected_song_label' in self.root.ids:
                    self.root.ids.selected_song_label.text = song_name
            
            # In a real app, you would call your recommendation engine here
            # For now, we'll simulate some recommendations
            self.simulate_recommendations()
            
            self.show_snackbar(f"Selected: {song_name}")
        else:
            self.show_snackbar("No file selected")

    def show_snackbar(self, text, duration=2.0):
        """Show a notification popup with the given text"""
        try:
            # Create a popup with the message
            content = BoxLayout(orientation='vertical', padding='8dp', spacing='8dp')
            content.add_widget(Label(
                text=text, 
                size_hint_y=None, 
                height='40dp',
                color=(0, 0, 0, 1)  # Black text
            ))
            
            # Create a close button
            btn_close = Button(
                text='OK',
                size_hint=(None, None),
                size=('100dp', '40dp'),
                pos_hint={'center_x': 0.5},
                background_color=(0.13, 0.59, 0.95, 1),  # Blue button
                color=(1, 1, 1, 1)  # White text
            )
            
            # Create the popup
            popup = Popup(
                title='Notification',
                content=content,
                size_hint=(0.8, None),
                height='150dp',
                auto_dismiss=True,
                background_color=(0.9, 0.9, 0.9, 1)  # Light gray background
            )
            
            # Bind close button
            btn_close.bind(on_release=popup.dismiss)
            content.add_widget(btn_close)
            
            # Show the popup
            popup.open()
            
            # Auto-dismiss after duration if specified
            if duration > 0:
                Clock.schedule_once(lambda dt: popup.dismiss(), duration)
                
        except Exception as e:
            print(f"Error showing snackbar: {str(e)}")
            import traceback
            traceback.print_exc()
            
    def get_selected_mood(self):
        """Get the currently selected mood from checkboxes (for genre-based playlists)
        
        Returns:
            str: The selected mood, or None if in song-based recommendation mode
        """
        # Check if we're in song-based recommendation mode
        if hasattr(self, 'root') and hasattr(self.root, 'ids') and 'screen_manager' in self.root.ids:
            if self.root.ids.screen_manager.current == 'recommend_screen':
                # In song-based mode, we don't need mood selection
                return 'auto'  # Indicate automatic mood detection from song
        
        # For genre/mood-based playlist generation
        try:
            # List of possible mood checkboxes with their display names
            mood_mapping = {
                'happy_check': 'happy',
                'sad_check': 'sad',
                'energetic_check': 'energetic',
                'calm_check': 'calm'
            }
            
            # Safely get the screen manager and current screen
            if not hasattr(self, 'root') or not hasattr(self.root, 'ids'):
                print("Warning: Root or root.ids not available")
                return None
                
            # Try to get the screen manager from root.ids
            screen_manager = None
            if 'screen_manager' in self.root.ids:
                screen_manager = self.root.ids.screen_manager
            
            if not screen_manager:
                # Try an alternative approach to find the screen manager
                for widget in self.root.walk():
                    if hasattr(widget, 'id') and widget.id == 'screen_manager':
                        screen_manager = widget
                        break
            
            if not screen_manager:
                print("Warning: Could not find screen manager in the widget tree")
                return None
            
            # Get the current screen
            current_screen = None
            if hasattr(screen_manager, 'current_screen'):
                current_screen = screen_manager.current_screen
            elif hasattr(screen_manager, 'current'):
                # Try to get the screen by name if current_screen is not available
                current_screen = screen_manager.get_screen(screen_manager.current) if hasattr(screen_manager, 'get_screen') else None
            
            if not current_screen:
                print("Warning: Could not get current screen")
                return None
            
            # Find all checkboxes in the current screen
            for widget in current_screen.walk(restrict=True):
                if hasattr(widget, 'id') and widget.id in mood_mapping:
                    if hasattr(widget, 'active') and widget.active:
                        print(f"Found active mood: {mood_mapping[widget.id]}")
                        return mood_mapping[widget.id]
            
            print("No mood selected")
            return None
            
        except Exception as e:
            print(f"Error in get_selected_mood: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def simulate_recommendations(self):
        """Simulate getting recommended songs (for demo purposes)"""
        # In a real app, this would call your recommendation engine
        # For now, we'll just return some dummy data
        self.recommended_songs = [
            "Recommended Song 1 - Artist 1",
            "Recommended Song 2 - Artist 2",
            "Recommended Song 3 - Artist 3",
            "Recommended Song 4 - Artist 4",
            "Recommended Song 5 - Artist 5"
        ]
        
        # Update the UI with the recommended songs
        self.update_recommendations_ui()
    
    def update_recommendations_ui(self):
        """Update the UI with the recommended songs"""
        if not hasattr(self, 'root') or not hasattr(self.root, 'ids'):
            return
            
        # Get the recommended songs list widget
        recommended_list = self.root.ids.get('recommended_songs_list')
        if not recommended_list:
            return
            
        # Clear the current list
        recommended_list.clear_widgets()
        
        if not self.recommended_songs:
            # Show a message if no recommendations are available
            label = MDLabel(
                text='No recommendations available',
                halign='center',
                theme_text_color='Secondary',
                size_hint_y=None,
                height='40dp'
            )
            recommended_list.add_widget(label)
            return
            
        # Add each recommended song to the list
        for song in self.recommended_songs:
            # Create a list item for each recommended song with an icon and text
            item = MDListItem(
                MDListItemLeadingIcon(
                    icon="music-note",
                    theme_icon_color="Custom",
                    icon_color=[0.13, 0.59, 0.95, 1]  # Blue color for the icon
                ),
                MDListItemHeadlineText(
                    text=song,
                    theme_text_color="Custom",
                    text_color=[0, 0, 0, 1],  # Black text
                    padding=["16dp", 0, 0, 0]  # Add some padding between icon and text
                ),
                on_release=lambda x, s=song: self.on_song_selected(s)
            )
            recommended_list.add_widget(item)
    
    def on_song_selected(self, song):
        """Handle when a recommended song is selected"""
        try:
            # In a real app, this would play the song or add it to a queue
            self.show_snackbar(f"Selected: {song}")
            
            # Update the selected song and get new recommendations
            # based on the newly selected song
            self.selected_song = song
            self.simulate_recommendations()
            
            # Update the selected song label
            if hasattr(self, 'root') and hasattr(self.root, 'ids'):
                if 'selected_song_label' in self.root.ids:
                    self.root.ids.selected_song_label.text = song
                    
                # Create a custom popup for loading
                content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
                content.add_widget(Label(
                    text="Generating recommendations...",
                    color=(0, 0, 0, 1),  # Black text
                    font_size='16sp'
                ))
                
                # Create and show the loading popup
                dialog = Popup(
                    title='Please Wait',
                    content=content,
                    size_hint=(0.8, None),
                    height=dp(150),
                    separator_color=[0.13, 0.59, 0.95, 1],
                    title_color=[0, 0, 0, 1],
                    title_size='18sp'
                )
                dialog.open()
                
                # Define the async generation function
                def generate_playlist_async(dt):
                    try:
                        # Simulate playlist generation (replace with actual logic)
                        print(f"Generating playlist with selected song: {self.selected_song}")
                        
                        # Simulate a delay for the playlist generation
                        import time
                        time.sleep(2)
                        
                        # Close the dialog if it's still open
                        if hasattr(dialog, 'parent') and dialog.parent and hasattr(dialog.parent, 'children') and dialog in dialog.parent.children:
                            dialog.dismiss()
                        
                        # Show success message
                        self.show_snackbar("Recommendations generated successfully!")
                        
                        # Simulate getting recommended songs
                        self.simulate_recommendations()
                        
                    except Exception as e:
                        # Close the dialog if it's still open
                        if hasattr(dialog, 'parent') and dialog.parent and hasattr(dialog.parent, 'children') and dialog in dialog.parent.children:
                            dialog.dismiss()
                        # Show error message
                        error_msg = f"Error generating recommendations: {str(e)}"
                        print(error_msg)
                        self.show_error_dialog("Error", error_msg)
                
                # Schedule the async generation
                Clock.schedule_once(generate_playlist_async, 0.1)
                
        except Exception as e:
            # Handle any errors that occur during the initial setup
            error_msg = f"Error: {str(e)}"
            print(error_msg)
            self.show_error_dialog("Error", error_msg)
    
    def show_error_dialog(self, title, message):
        """Show an error dialog using a custom popup with standard Kivy Button"""
        # Create a custom popup
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # Add message label
        from kivy.uix.label import Label
        content.add_widget(Label(
            text=message,
            halign='center',
            valign='middle',
            size_hint_y=0.8,
            text_size=(Window.width * 0.7, None),
            color=(0, 0, 0, 1)  # Black text
        ))
        
        # Add OK button with custom styling
        ok_btn = Button(
            text="OK",
            size_hint=(0.5, None),
            height=dp(48),
            pos_hint={'center_x': 0.5},
            background_color=[0.13, 0.59, 0.95, 1],  # Blue background
            color=(1, 1, 1, 1),  # White text
            background_normal='',
            background_down='',
            font_size='16sp',
            bold=True
        )
        
        # Create and show the popup
        self.popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.4),
            title_size='18sp',
            title_align='center',
            title_color=(0, 0, 0, 1),  # Black title
            separator_color=[0.13, 0.59, 0.95, 1],  # Blue separator
            auto_dismiss=False
        )
        
        # Bind the button to dismiss the popup
        ok_btn.bind(on_release=lambda x: self.popup.dismiss())
        
        # Add button to content
        content.add_widget(ok_btn)
        
        # Open the popup
        self.popup.open()

if __name__ == '__main__':
    DCMApp().run()