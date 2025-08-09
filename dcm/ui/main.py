import os
import sys

# Kivy imports
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.metrics import dp
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.utils import platform
from kivy.properties import ListProperty, StringProperty, ObjectProperty, NumericProperty
from kivy.core.window import Window

# KivyMD imports
from kivymd.app import MDApp
from kivymd.uix.button import MDButton
from kivymd.uix.dialog import MDDialog
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
        
        # Set up the screen manager
        self.sm = ScreenManager()
        from .main_screen import MainScreen
        self.sm.add_widget(MainScreen(name='main_screen'))
        
        # Set window background color
        from kivy.utils import get_color_from_hex
        Window.clearcolor = get_color_from_hex('#f5f5f5')  # Light gray background
        
        return self.sm

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
    
    def file_manager_open(self):
        # Create a popup for file selection
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Create file chooser
        file_chooser = FileChooserListView(
            path=os.path.expanduser('~'),
            filters=['*.mp3', '*.wav', '*.m4a', '*.flac'],
            multiselect=True
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
            title='Select Music Files',
            content=content,
            size_hint=(0.9, 0.9)
        )
        
        # Button actions
        def select_files(instance):
            if file_chooser.selection:
                self.selected_files = file_chooser.selection
                self.show_snackbar(f"Selected {len(self.selected_files)} files")
            popup.dismiss()
            
        btn_select.bind(on_release=select_files)
        btn_cancel.bind(on_release=lambda x: popup.dismiss())
        
        # Open the popup
        popup.open()
    
    def files_selected(self, selection, path):
        """Handle selected files"""
        if self.popup:
            self.popup.dismiss()
        
        if selection:
            self.selected_files = selection
            print(f"Selected files: {self.selected_files}")
            self.show_snackbar(f"Selected {len(self.selected_files)} file(s)")
    
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
        """Get the currently selected mood from checkboxes"""
        try:
            # List of possible mood checkboxes with their display names
            mood_mapping = {
                'happy_check': 'happy',
                'sad_check': 'sad',
                'energetic_check': 'energetic',
                'calm_check': 'calm'
            }
            
            # Get the generate screen
            generate_screen = self.root.get_screen('generate_screen')
            
            # Debug: Print available widget IDs in the generate screen
            print("Available widget IDs in generate_screen:", list(generate_screen.ids.keys()))
            
            # Check each possible mood checkbox
            for checkbox_id, mood_name in mood_mapping.items():
                try:
                    # Try to find the checkbox in the widget tree
                    checkbox = None
                    for widget in generate_screen.walk(restrict=True):
                        if hasattr(widget, 'id') and widget.id == checkbox_id:
                            checkbox = widget
                            break
                    
                    # If we found the checkbox and it's active, return the mood name
                    if checkbox and hasattr(checkbox, 'active') and checkbox.active:
                        print(f"Found active checkbox: {checkbox_id} -> {mood_name}")
                        return mood_name
                        
                except Exception as e:
                    print(f"Error checking {checkbox_id}: {str(e)}")
            
            # If we get here, no mood was selected
            print("No mood selected")
            return None
            
        except Exception as e:
            print(f"Error in get_selected_mood: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_playlist(self):
        """Generate a playlist based on the selected mood and songs"""
        try:
            # Get the selected mood
            mood = self.get_selected_mood()
            print(f"Selected mood: {mood}")
                
            if not mood:
                self.show_error_dialog("Error", "Please select a mood")
                return
                
            # Get playlist name
            generate_screen = self.root.get_screen('generate_screen')
            playlist_name = generate_screen.ids.playlist_name.text.strip()
            if not playlist_name:
                self.show_error_dialog("Error", "Please enter a playlist name")
                return
                
            # Check if files are selected
            if not self.selected_files:
                self.show_error_dialog("Error", "Please select at least one song")
                return
                
            # Create a custom popup for loading
            content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
            content.add_widget(Label(
                text=f"Generating {playlist_name} playlist...",
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
            
            # Schedule the playlist generation to run after a short delay
            # This allows the UI to update before starting the potentially long-running task
            def generate_playlist_async(dt):
                try:
                    # Simulate playlist generation (replace with actual logic)
                    print(f"Generating playlist: {playlist_name} with mood: {mood}")
                    print(f"Selected files: {self.selected_files}")
                    
                    # Simulate a delay for the playlist generation
                    import time
                    time.sleep(2)
                    
                    # Close the dialog
                    dialog.dismiss()
                    
                    # Show success message
                    self.show_snackbar(f"Successfully generated playlist: {playlist_name}")
                    
                except Exception as e:
                    # Close the dialog if it's still open
                    if dialog in dialog.parent.children:
                        dialog.dismiss()
                    # Show error message
                    error_msg = f"Error generating playlist: {str(e)}"
                    print(error_msg)
                    self.show_error_dialog("Error", error_msg)
            
            # Schedule the async generation
            Clock.schedule_once(generate_playlist_async, 0.1)
            
        except Exception as e:
            # Handle any errors that occur during the initial setup
            error_msg = f"Error: {str(e)}"
            print(error_msg)
            self.show_error_dialog("Error", error_msg)
    
    def get_selected_mood(self):
        """Get the currently selected mood from checkboxes"""
        if self.root.ids.happy_check.active:
            return 'happy'
        elif self.root.ids.sad_check.active:
            return 'sad'
        elif self.root.ids.energetic_check.active:
            return 'energetic'
        return ''
    
    def _finish_playlist_generation(self, playlist_name):
        """Finish the playlist generation process"""
        # Close the loading dialog
        if hasattr(self, 'dialog') and self.dialog:
            self.dialog.dismiss()
            
        # Show success message
        self.show_snackbar(f"Playlist '{playlist_name}' generated successfully!")
        
        # Clear the form
        self.root.ids.playlist_name.text = ''
        self.root.ids.happy_check.active = False
        self.root.ids.sad_check.active = False
        self.root.ids.energetic_check.active = False
        self.selected_files = []
        self.root.ids.playlist_items.clear_widgets()
        
        # Add some sample playlist items (replace with actual generated playlist)
        sample_songs = ["Song 1", "Song 2", "Song 3"]
        for song in sample_songs:
            item = Label(text=song,
                       size_hint_y=None,
                       height=dp(40),
                       color=(0, 0, 0, 1),  # Black text
                       font_size='14sp')
            self.root.ids.playlist_items.add_widget(item)
        
        from kivymd.uix.list import OneLineListItem
        for i in range(5):
            item = OneLineListItem(
                text=f"{mood.capitalize()} Song {i+1}",
                theme_text_color='Primary'
            )
            playlist_items.add_widget(item)
        
        self.show_snackbar(f"Generated '{playlist_name}' playlist with {mood} mood!")
    
    def show_error_dialog(self, title, message):
        """Show an error dialog using a custom popup for compatibility"""
        # Create a custom popup
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Add message label
        from kivymd.uix.label import MDLabel
        content.add_widget(MDLabel(
            text=message,
            halign='center',
            theme_text_color='Primary',
            size_hint_y=None,
            height=dp(100)
        ))
        
        # Add button container
        btn_container = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        # Add OK button
        ok_btn = MDButton(
            text="OK",
            size_hint=(0.5, None),
            height=dp(40),
            pos_hint={'center_x': 0.5},
            theme_text_color='Custom',
            text_color=(1, 1, 1, 1),
            md_bg_color=[0.13, 0.59, 0.95, 1],
        )
        
        # Create and show the popup
        self.popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, None),
            height=dp(250),
            auto_dismiss=False
        )
        
        # Bind the button to dismiss the popup
        ok_btn.bind(on_release=lambda x: self.popup.dismiss())
        
        # Add button to container and container to content
        btn_container.add_widget(BoxLayout())  # Left spacer
        btn_container.add_widget(ok_btn)
        btn_container.add_widget(BoxLayout())  # Right spacer
        content.add_widget(btn_container)
        
        # Open the popup
        self.popup.open()

if __name__ == '__main__':
    DCMApp().run()