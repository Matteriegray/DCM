"""DCM playlist generator"""
import os
import argparse
import logging
from pathlib import Path
from typing import List, Optional , Dict, Union
import pandas as pd 
from rich.console import Console
from rich.progress import track   # Rich is used to imporve the UI in CLI
# Set up logging 

logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initializing the console
console = Console()


# Implementing the class of Playlist generator
class PlaylistGenerator:
    def __init__(self, features_file: str):
        # Initializes the playlist generator with song features
        # Args : Path to the CSV  file containig song features
        self.features_df = None
        self.load_features(features_file) 
    def load_features(self, features_file : str): 
        # Load the song features from a CSV file 
        # Args : Path to the csv file 
        try : 
            # Checks if the file exists
            if not os.path.exists(features_file):
                raise FileNotFoundError(f"Features file not found: {features_file}")
            
            # Load file
            self.features_df = pd.read_csv(features_file)
            # Check if empty
            
            if self.features_df.empty: 
                raise ValueError("Features file is empty") 
            
            required_columns = ['file_path'] 
            for col in required_columns : 
                if col not in self.features_df.columns:
                    raise ValueError(f"Missing required column in feaures files {col} ") 
            
            logger.info(f"Loaded features fror {len(self.features_df)} songs")
        except pd.errors.EmptyDataError:
            raise ValueError("Features file is empty") 
        except Exception as e:
            logger.error(f"Error loading features file : {e} ") 
            raise  
        
    def save_as_m3u(
        self, 
        song_paths: List[str],
        output_file:str, 
        playlist_name:Optional[str] = None 
    ) -> bool:
        # Saves the playlist as a M3U playlist   # Why M3U - is a Universal format and accepts all others like .mp3 , .m3a etc
        """Args : song_paths: List of paths to songs
           output_file : Path to save the playlist 
           playlist_name 
           
           Returns : bool - True if successful , False otherwise"""
        
        try:
            # Create a output directory 
            output_path = Path(output_file) 
            output_path.parent.mkdir(parents = True, exist_ok = True)  
            
            # Conversts all path to absolute paths 
            abs_paths = [str(Path(path).resolve()) for path in song_paths] 
            
            # Write the playlist to a file 
            with open(output_file, 'w', ecoding = 'utf-8') as f:
                # Write M3U header 
                f.write("#EXTM3U\n") 
                
                # Write the playlist name ( if provided) 
                if playlist_name:
                    f.write(f"#PLAYLIST: {playlist_name}") 
                
                # Write the song path 
                for song_path in abs_paths:
                    f.write(f"#EXTINF: 0, {Path(song_path).stem}\n") 
                    f.write(f"{song_path}\n")
            logger.info(f"Playlist saved to {output_file}") 
            return True 
        except Exception as e:
            logger.error(f"Error saving playlist: {e}") 
            return False 