"""DCM playlist generator"""
import os
import argparse
import logging
from pathlib import Path
from typing import List, Optional , Dict, Union
from numpy.random import rand
import pandas as pd 
from rich.console import Console
from rich.progress import track 
import numpy as np # Rich is used to imporve the UI in CLI
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
            with open(output_file, 'w', encoding='utf-8') as f:
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
        
    def generate_playlist(
        self, 
        song_path: List[str], 
        output_file: str,
        playlist_name: Optional[str] = None,
        max_songs : int = 20, 
        shuffle : bool = True, 
        dynamic :bool = True 
    ) -> bool:
        """ Generate a playlist from a list of song paths. 
            
            Args : song_path, output_file, max_songs, shuffle 
            
            returns : bool - True if playlist generation is successfull"""
        try: 
            # Filter the songs that exists in the database
            valid_songs = [] 
            for song_path in song_path:
                # Convert to compare
                abs_path = str(Path(song_path).resolve()) 
                # Checks if path exists in the database 
                if not (self.features_df['file_path'] == abs_path).any():
                    logger.warning(f"Song not found in database: {song_path}") 
                    continue 
                valid_songs.append(abs_path) 
            if not valid_songs:
                logger.error("No valid songs found in feature database") 
                return False 
            
            playlist = valid_songs.copy() 
            
            if dynamic:
                while len(playlist) < max_songs and len(playlist) < len(self.features_df):
                    last_songs = playlist[-min(3, len(playlist)):] 
                    new_songs = [] 
                    
                    for song in last_songs:
                        similar = self.find_similar_songs(song, n = 3)
                        new_songs.extend([s for s in similar if s not in playlist and s not in new_songs]) 
                        if len(playlist) + len(new_songs) >= max_songs:
                            break 
                    
                    if not new_songs:
                        break 
                    playlist.extend(new_songs[:max_songs - len(playlist)]) 
                    
            # Shuffle
            if shuffle :
                if dynamic : 
                    initial_songs = valid_songs.copy() 
                    random.shuffle(initial_songs)
                    playlist = initial_songs + playlist[len(initial_songs)]  
                else:
                    random.shuffle(playlist)            
            return self.save_as_m3u(playlist[:max_songs], output_file, playlist_name)
        except Exception as e:
            logger.error(f"Error generating playlist: {e}") 
            return False 
    
    def find_similar_songs(self, song_path: str, n: int = 5) -> List[str]:
        """Find n songs similar to the given song.
    
        Args:
        song_path: Path to the reference song
        n: Number of similar songs to find (default: 5)
        
        Returns:
            List of paths to similar songs
        """
        try:
            abs_path = str(Path(song_path).resolve())
            song_mask = self.features_df['file_path'] == abs_path
            song_idx = self.features_df[song_mask].index
        
            if len(song_idx) == 0:
                logger.warning(f"Song not found in database: {song_path}")
                return []
            
            features = self.get_feature_vectors()
        
            from sklearn.metrics.pairwise import cosine_similarity
            similarities = cosine_similarity(
                features[song_idx],
                features
            )[0]
        
            # Get top n similar songs (excluding the song itself)
            similar_indices = similarities.argsort()[-n-1:-1][::-1]
            return self.features_df.iloc[similar_indices]['file_path'].tolist()
        
        except Exception as e:
            logger.error(f"Error finding similar songs: {e}")
            return []
        
    def get_feature_vectors(self) -> np.ndarray:
        # Gets the feature vectors from the features dataframe and then normalizes it 
        feature_columns = [col for col in self.features_df.columns 
                           if col not in ['file_path', 'file_name', 'file_extension', 'file_size_mb']] 
        features = self.features_df[feature_columns].values 
        from sklearn.preprocessing import StandardScaler 
        return StandardScaler().fit_transform(features) 
    
    
def main() :
    # CLI for the Playlist generator 
    import argparse 
    import sys 
    
    parser = argparse.ArgumentParser(description = "DCM Playlist Generator") 
    parser.add_argument('features_file', help = 'Path to the features file') 
    parser.add_argument('output_file', help = "Path to save the playlist") 
    parser.add_argument('songs', nargs = "+" , help = 'List of seed songs') 
    parser.add_argument('--max-songs', type = int, default = 20, help = "Maximum number of songs in the playlist") 
    parser.add_argument("--no-shuffle", action = 'store_false', dest = 'shuffle', help = 'Disable shuffling') 
    parser.add_argument('--status', action = 'store_false', dest = 'dynamic', help = "Disable dynamic song addition") 
    
    args = parser.parse_args() 
    
    try :
        generator = PlaylistGenerator(args.features_file) 
        success = generator.generate_playlist(
            args.songs,
            args.output_file, 
            max_songs = args.max_songs, 
            shuffle = args.shuffle, 
            dynamic = args.dynamic 
        )
        sys.exit(0 if success else 1) 
    except Exception as e :
        print(f"Error : {e}", file_sus.stderr) 
        sys.exit(1)
if __name__ == '__main__': 
    main() 