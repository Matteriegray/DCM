import os
import sys
import platform
import random
from pathlib import Path
from functools import partial

# Kivy imports
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import (
    ListProperty, StringProperty, ObjectProperty, 
    NumericProperty, BooleanProperty, DictProperty
)
from kivy.clock import Clock
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

# Import our modules
from dcm.database import db
from dcm.player import player as music_player

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
    
    # Player state properties
    current_song = StringProperty('No song selected')
    current_artist = StringProperty('')
    current_album = StringProperty('')
    is_playing = BooleanProperty(False)
    current_time = NumericProperty(0)
    total_time = NumericProperty(0)
    volume = NumericProperty(0.8)  # Default volume (0.0 to 1.0)
    
    def __init__(self, **kwargs):
        super(DCMApp, self).__init__(**kwargs)
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primaryColor = [0.13, 0.59, 0.95, 1]  # RGB for #2196F3 (Blue 500)
        # Force text color to be visible on buttons
        self.theme_cls.text_color = [0, 0, 0, 1]  # Black text
        self.theme_cls.primary_text_color = [0, 0, 0, 1]  # Black primary text
        self.theme_cls.accent_text_color = [1, 1, 1, 1]  # White accent text
        
        # Initialize player state
        self.selected_song = None
        self.current_playlist = []
        self.current_index = -1
        
        # Setup player callbacks
        music_player.bind(
            current_position=self.update_time_display,
            duration=self.update_duration,
            is_playing=self.update_play_button_state
        )
        
        # Set initial volume
        music_player.volume = self.volume

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

    def switch_screen(self, screen_name):
        """Switch between different screens"""
        if hasattr(self, 'root') and hasattr(self.root, 'ids'):
            if 'screen_manager' in self.root.ids:
                self.root.ids.screen_manager.current = screen_name
                # Update navigation button states
                self.update_nav_buttons(screen_name)
                return True
        return False
        
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
                        # Update navigation button states
                        self.update_nav_buttons('recommend_screen')
                        return
                    
                    # Try to find the screen manager by walking the widget tree
                    for widget in self.root.walk():
                        if hasattr(widget, 'id') and widget.id == 'screen_manager':
                            widget.current = 'recommend_screen'
                            self.update_nav_buttons('recommend_screen')
                            return
                
                print("Warning: Could not find or access screen manager")
                
                # As a fallback, try to switch screens using the MainScreen method
                if hasattr(self.root, 'switch_screen'):
                    self.root.switch_screen('recommend_screen')
                    
            except Exception as e:
                print(f"Error in set_initial_screen: {str(e)}")
        
        # Schedule the screen change to happen after the UI is fully loaded
        Clock.schedule_once(set_initial_screen, 0.5)  # Slightly longer delay to ensure UI is ready
        
    def update_nav_buttons(self, active_screen):
        """Update the navigation buttons to show which screen is active"""
        if not hasattr(self, 'root') or not hasattr(self.root, 'ids'):
            return
            
        # Default button colors
        active_color = [0.07, 0.45, 0.85, 1]  # Darker blue for active
        inactive_color = [0.13, 0.59, 0.95, 1]  # Lighter blue for inactive
        
        # Update button colors based on active screen
        if 'recommend_btn_nav' in self.root.ids:
            self.root.ids.recommend_btn_nav.background_color = active_color if active_screen == 'recommend_screen' else inactive_color
        if 'generate_btn_nav' in self.root.ids:
            self.root.ids.generate_btn_nav.background_color = active_color if active_screen == 'generate_screen' else inactive_color
        
    def generate_playlist(self):
        """Handle the generate playlist button click"""
        print("Generate playlist button clicked")
        
        # Check if we're in song-based or genre-based mode
        if hasattr(self, 'root') and 'screen_manager' in self.root.ids:
            current_screen = self.root.ids.screen_manager.current
            
            if current_screen == 'recommend_screen':
                # Song-based recommendations (Spotify-like)
                if not self.selected_song:
                    self.show_error_dialog("No Song Selected", "Please select a song to get recommendations.")
                    return
                
                # Clear previous recommendations
                if 'recommended_songs_list' in self.root.ids:
                    self.root.ids.recommended_songs_list.clear_widgets()
                
                # Add the selected song to the database if it's not already there
                song_id = db.add_song(
                    file_path=self.selected_song,
                    title=os.path.splitext(os.path.basename(self.selected_song))[0],
                    # In a real app, you would extract metadata from the audio file here
                    genre="Unknown",
                    mood="Unknown"
                )
                
                # Get similar songs from the database
                similar_songs = db.get_similar_songs(song_id, limit=5)
                
                if similar_songs:
                    # Display the recommendations
                    self.display_recommendations(similar_songs)
                else:
                    # Fallback to simulated recommendations if no similar songs found
                    self.simulate_recommendations()
                
            elif current_screen == 'generate_screen':
                # Genre/mood-based playlist generation
                mood = self.get_selected_mood()
                
                # Check if we have selected files
                if not self.selected_files:
                    self.show_error_dialog("No Files Selected", "Please select at least one music file.")
                    return
                
                # Clear previous playlist items
                if 'playlist_items' in self.root.ids:
                    self.root.ids.playlist_items.clear_widgets()
                
                # Add files to database and create a playlist
                song_ids = []
                for file_path in self.selected_files:
                    song_id = db.add_song(
                        file_path=file_path,
                        title=os.path.splitext(os.path.basename(file_path))[0],
                        mood=mood
                    )
                    song_ids.append(song_id)
                
                # Create a playlist with these songs
                playlist_name = f"{mood.capitalize()} Mix - {len(song_ids)} songs"
                playlist_id = db.add_playlist(playlist_name, song_ids)
                
                # Get the playlist songs with full metadata
                playlist_songs = db.get_playlist_songs(playlist_id)
                
                # Display the playlist
                self.display_playlist(playlist_songs)
                
                # Update the current playlist for playback
                self.current_playlist = [song['file_path'] for song in playlist_songs]
                
                # Auto-play the first song if there are any
                if self.current_playlist:
                    self.play_song(0)
        
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
    
    def simulate_recommendations(self):
        """Simulate getting recommendations for the selected song.
        
        Handles both string (file path) and dictionary (song object) types for self.selected_song.
        Generates diverse recommendations instead of variations of the same song.
        """
        if not hasattr(self, 'selected_song') or not self.selected_song:
            self.show_error_dialog("Error", "No song selected for recommendations.")
            return
            
        try:
            # Sample data for generating diverse recommendations
            sample_artists = ["A.R. Rahman", "Taylor Swift", "The Weeknd", "BTS", "Adele", "Ed Sheeran", "Billie Eilish"]
            sample_albums = ["Midnight Memories", "After Hours", "30", "BE", "Folklore", "Happier Than Ever", "="]
            sample_genres = ["Pop", "Rock", "Hip Hop", "Electronic", "R&B", "Classical", "Jazz"]
            
            # Get some information about the selected song for context
            if isinstance(self.selected_song, dict):
                # If it's a song object, use its genre if available
                song_title = self.selected_song.get('title', 'Unknown Song')
                song_genre = self.selected_song.get('genre', random.choice(sample_genres))
                
                # If we have a file path in the song object, use that as the base
                if 'file_path' in self.selected_song and self.selected_song['file_path']:
                    base_name = os.path.basename(self.selected_song['file_path'])
                    name, _ = os.path.splitext(base_name)
            else:
                # If it's a string, treat it as a file path
                base_name = os.path.basename(self.selected_song)
                name, _ = os.path.splitext(base_name)
                song_title = name
                song_genre = random.choice(sample_genres)
            
            # Generate diverse recommendations (not just variations of the same song)
            recommended_songs = []
            for i in range(5):  # Generate 5 diverse recommendations
                # Select a different artist for each recommendation
                artist = random.choice(sample_artists)
                while artist == self.selected_song.get('artist', ''):
                    artist = random.choice(sample_artists)
                
                # Select a different album
                album = random.choice(sample_albums)
                
                # Create a unique song title
                title = f"{random.choice(['Echoes', 'Midnight', 'Dreams', 'Horizon', 'Starlight'])} " \
                       f"{random.choice(['of', 'in', 'beyond', 'across'])} " \
                       f"{random.choice(['Time', 'Space', 'Love', 'Life', 'You'])}"
                
                # Ensure we don't recommend the same song
                if title == song_title:
                    title = f"{title} (Remix)"
                
                # Add to recommendations
                recommended_songs.append({
                    'title': title,
                    'artist': artist,
                    'album': album,
                    'genre': song_genre,  # Keep the same genre for relevance
                    'duration': random.randint(150, 300),  # 2.5 to 5 minutes
                    'file_path': f"/path/to/music/{artist.replace(' ', '_')}/{album.replace(' ', '_')}/{title.replace(' ', '_')}.mp3"
                })
            
            # Store the recommended songs
            self.recommended_songs = recommended_songs
            
            # Update the UI with the recommendations
            self.update_recommendations_ui()
            
            # Switch to the recommend screen
            self.switch_screen('recommend_screen')
            
        except Exception as e:
            error_msg = f"Failed to generate recommendations: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            # Show a user-friendly error message
            self.show_error_dialog("Recommendation Error", 
                                 "We couldn't generate recommendations right now. Please try again later.")
    
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
        
        if not hasattr(self, 'recommended_songs') or not self.recommended_songs:
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
            # Ensure we have a dictionary with the required keys
            if not isinstance(song, dict):
                song = {'title': str(song), 'artist': 'Unknown Artist', 'album': 'Unknown Album'}
            
            # Create a container for the song info
            content = BoxLayout(orientation='vertical', padding=["16dp", "8dp", "8dp", "8dp"])
            
            # Add song title
            title_label = MDLabel(
                text=str(song.get('title', 'Unknown Song')),
                theme_text_color="Custom",
                text_color=[0, 0, 0, 1],  # Black text
                font_size='14sp',
                size_hint_y=None,
                height=dp(24)
            )
            
            # Add artist and album info
            info_label = MDLabel(
                text=f"{song.get('artist', 'Unknown Artist')} • {song.get('album', 'Unknown Album')}",
                theme_text_color="Secondary",
                font_size='12sp',
                size_hint_y=None,
                height=dp(20)
            )
            
            content.add_widget(title_label)
            content.add_widget(info_label)
            
            # Create the list item with an icon and the content
            item = MDListItem(
                MDListItemLeadingIcon(
                    icon="music-note",
                    theme_icon_color="Custom",
                    icon_color=[0.13, 0.59, 0.95, 1],  # Blue color for the icon
                    size_hint_x=None,
                    width=dp(48)
                ),
                content,
                on_release=lambda x, s=song: self.on_song_selected(s),
                size_hint_y=None,
                height=dp(72)
            )
            recommended_list.add_widget(item)
    
    def on_song_selected(self, song):
        """Handle when a recommended song is selected.
        
        Args:
            song: Dictionary containing song information with at least a 'title' key.
                  May also contain 'file_path', 'artist', 'album', etc.
        """
        try:
            if not song or not isinstance(song, dict):
                self.show_error_dialog("Error", "Invalid song data")
                return
                
            song_title = song.get('title', 'Unknown Song')
            self.show_snackbar(f"Selected: {song_title}")
            
            # Play the selected song
            if not self.play_song(song_data=song):
                self.show_error_dialog("Playback Error", f"Could not play: {song_title}")
                return
            
            # Update the selected song and get new recommendations
            self.selected_song = song
            
            # Update the selected song label in the UI
            if hasattr(self, 'root') and hasattr(self.root, 'ids'):
                if 'selected_song_label' in self.root.ids:
                    self.root.ids.selected_song_label.text = song_title
            
            # Show loading dialog for recommendations
            content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
            content.add_widget(Label(
                text="Generating recommendations...",
                color=(0, 0, 0, 1),  # Black text
                font_size='16sp'
            ))
            
            # Create and show the loading popup
            dialog = Popup(
                title='Finding Similar Songs',
                content=content,
                size_hint=(0.8, None),
                height=dp(150),
                separator_color=[0.13, 0.59, 0.95, 1],
                title_color=[0, 0, 0, 1],
                title_size='18sp'
            )
            dialog.open()
            
            def generate_playlist_async(dt):
                """Generate recommendations asynchronously."""
                try:
                    # Simulate network/processing delay
                    import time
                    time.sleep(1.5)
                    
                    # Generate new recommendations based on the selected song
                    self.simulate_recommendations()
                    
                    # Close the dialog
                    if hasattr(dialog, 'parent') and dialog.parent and hasattr(dialog.parent, 'children') and dialog in dialog.parent.children:
                        dialog.dismiss()
                    
                    self.show_snackbar("Recommendations updated!")
                    
                except Exception as e:
                    # Close the dialog on error
                    if hasattr(dialog, 'parent') and dialog.parent and hasattr(dialog.parent, 'children') and dialog in dialog.parent.children:
                        dialog.dismiss()
                    
                    error_msg = f"Error generating recommendations: {str(e)}"
                    print(error_msg)
                    self.show_error_dialog("Error", error_msg)
            
            # Schedule the async generation with a small delay
            Clock.schedule_once(generate_playlist_async, 0.2)
            
        except Exception as e:
            error_msg = f"Error selecting song: {str(e)}"
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
        
    # Music Player Controls
    def play_song(self, index=None, file_path=None, song_data=None):
        """Play a song from the current playlist, a file path, or a song dictionary.
        
        Args:
            index: Index of the song in the current_playlist (optional)
            file_path: Path to an audio file to play (optional)
            song_data: Dictionary containing song data (optional)
                Expected keys: 'file_path', 'title', 'artist', 'album', 'duration'
                
        Returns:
            bool: True if playback started successfully, False otherwise
        """
        try:
            # If song_data is provided, use it
            if song_data and isinstance(song_data, dict):
                if 'file_path' not in song_data or not song_data['file_path']:
                    self.show_error_dialog("Playback Error", "No file path provided in song data")
                    return False
                    
                file_path = song_data['file_path']
                
            # Play from file path if provided
            if file_path:
                if not os.path.exists(file_path):
                    self.show_error_dialog("File Not Found", f"Could not find audio file: {file_path}")
                    return False
                    
                if music_player.play(file_path):
                    # Update UI with song info
                    self.current_song = song_data.get('title', os.path.basename(file_path)) if song_data else os.path.basename(file_path)
                    self.current_artist = song_data.get('artist', 'Unknown Artist') if song_data else 'Unknown Artist'
                    self.current_album = song_data.get('album', 'Unknown Album') if song_data else 'Unknown Album'
                    self.total_time = music_player.duration
                    self.is_playing = True
                    
                    # If this is a recommended song, add it to the recent plays
                    if song_data and hasattr(self, 'recommended_songs') and song_data in self.recommended_songs:
                        # In a real app, you might want to add this to a "recently played" list
                        pass
                        
                    return True
                return False
            
            # Play from playlist by index
            elif index is not None and hasattr(self, 'current_playlist') and 0 <= index < len(self.current_playlist):
                song = self.current_playlist[index]
                if 'file_path' not in song or not song['file_path']:
                    self.show_error_dialog("Playback Error", "No file path available for this song")
                    return False
                    
                if music_player.play(song['file_path']):
                    self.current_index = index
                    self.current_song = song.get('title', os.path.basename(song['file_path']))
                    self.current_artist = song.get('artist', 'Unknown Artist')
                    self.current_album = song.get('album', 'Unknown Album')
                    self.total_time = music_player.duration
                    self.is_playing = True
                    return True
                return False
            
            # No valid input
            self.show_error_dialog("Playback Error", "No song selected or invalid song data")
            return False
            
        except Exception as e:
            error_msg = f"Could not play song: {str(e)}"
            print(error_msg)
            self.show_error_dialog("Playback Error", error_msg)
            return False
    
    def toggle_play_pause(self):
        """Toggle between play and pause."""
        if music_player.is_playing:
            music_player.pause()
            self.is_playing = False
        else:
            if music_player.current_song:
                music_player.play()
                self.is_playing = True
            elif self.current_playlist:
                self.play_song(0)  # Start playing the first song
    
    def stop_playback(self):
        """Stop the current playback."""
        music_player.stop()
        self.is_playing = False
    
    def next_song(self):
        """Play the next song in the playlist."""
        if not self.current_playlist or self.current_index == -1:
            return
            
        next_index = (self.current_index + 1) % len(self.current_playlist)
        self.play_song(next_index)
    
    def previous_song(self):
        """Play the previous song in the playlist."""
        if not self.current_playlist or self.current_index == -1:
            return
            
        prev_index = (self.current_index - 1) % len(self.current_playlist)
        self.play_song(prev_index)
    
    def set_volume(self, volume):
        """Set the player volume (0.0 to 1.0)."""
        volume = max(0.0, min(1.0, float(volume)))
        self.volume = volume
        music_player.volume = volume
    
    def seek(self, position):
        """Seek to a specific position in the current song."""
        music_player.seek(position)
    
    def update_time_display(self, instance, position):
        """Update the current time display."""
        self.current_time = position
    
    def update_duration(self, instance, duration):
        """Update the total duration display."""
        self.total_time = duration
    
    def update_play_button_state(self, instance, is_playing):
        """Update the play/pause button state."""
        self.is_playing = is_playing
    
    def format_duration(self, seconds):
        """Format seconds into MM:SS format."""
        if not isinstance(seconds, (int, float)) or seconds < 0:
            return "00:00"
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def on_stop(self):
        """Clean up when the app is closed."""
        music_player.cleanup()
        return True

if __name__ == '__main__':
    DCMApp().run()