"""DCM playlist generator"""
import os
import argparse
import logging
import random
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
        song_paths: List[str], 
        output_file: str,
        playlist_name: Optional[str] = None,
        max_songs: int = 20, 
        shuffle: bool = True,
        dynamic: bool = True,
        genre: Optional[str] = None,
        mood: Optional[str] = None
    ) -> bool:
        """Generate a playlist with optional genre and mood filters."""
        try:
            # Validate and convert paths
            valid_songs = []
            for song_path in song_paths:
                abs_path = str(Path(song_path).resolve())
                if not (self.features_df['file_path'] == abs_path).any():
                    logger.warning(f"Song not found: {song_path}")
                    continue
                valid_songs.append(abs_path)
                
            if not valid_songs:
                logger.error("No valid songs found")
                return False
                
            playlist = valid_songs.copy()
            
            # Add similar songs if dynamic
            if dynamic:
                while len(playlist) < max_songs and len(playlist) < len(self.features_df):
                    last_songs = playlist[-min(3, len(playlist)):]
                    new_songs = []
                    
                    for song in last_songs:
                        similar = self.find_similar_songs(
                            song, 
                            n=3,
                            genre_filter=genre,
                            mood_filter=mood
                        )
                        new_songs.extend([s for s in similar 
                                       if s not in playlist and s not in new_songs])
                        if len(playlist) + len(new_songs) >= max_songs:
                            break
                    
                    if not new_songs:
                        break
                        
                    playlist.extend(new_songs[:max_songs - len(playlist)])
            
            # Shuffle if requested
            if shuffle:
                if dynamic:
                    initial_songs = valid_songs.copy()
                    random.shuffle(initial_songs)
                    playlist = initial_songs + playlist[len(initial_songs):]
                else:
                    random.shuffle(playlist)
            
            return self.save_as_m3u(playlist[:max_songs], output_file, playlist_name)
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return False
    
    def find_similar_songs(
        self, 
        song_path: str, 
        n: int = 5, 
        genre_filter: Optional[str] = None,
        mood_filter: Optional[str] = None
    ) -> List[str]:
        """Find n songs similar to the given song with optional filters.
        
        Args:
            song_path: Path to the reference song
            n: Number of similar songs to find
            genre_filter: Optional genre to filter by
            mood_filter: Optional mood to filter by
            
        Returns:
            List of paths to similar songs matching the filters
        """
        try:
            logger.debug(f"Finding similar songs for: {song_path}")
            abs_path = str(Path(song_path).resolve())
            song_mask = self.features_df['file_path'] == abs_path
            song_idx = self.features_df[song_mask].index
            
            if len(song_idx) == 0:
                logger.warning(f"Song not found in database: {song_path}")
                return []
                
            features = self.get_feature_vectors()
            
            # Get similarity scores
            from sklearn.metrics.pairwise import cosine_similarity
            similarities = cosine_similarity(
                features[song_idx],
                features
            )[0]
            
            # Get indices sorted by similarity (descending)
            similar_indices = similarities.argsort()[::-1]
            
            # Filter and collect results
            results = []
            for idx in similar_indices:
                if idx == song_idx[0]:  # Skip the song itself
                    continue
                    
                current_path = self.features_df.iloc[idx]['file_path']
                
                # Apply genre filter if specified
                if genre_filter:
                    song_genre = self.get_genre(current_path)
                    logger.debug(f"Checking genre for {current_path}: {song_genre}")
                    if song_genre.lower() != genre_filter.lower():
                        logger.debug(f"Skipping due to genre mismatch: {song_genre} != {genre_filter}")
                        continue
                
                # Apply mood filter if specified
                if mood_filter:
                    song_features = features[idx]
                    song_mood = self.classify_mood(song_features)
                    logger.debug(f"Checking mood for {current_path}: {song_mood}")
                    if song_mood.lower() != mood_filter.lower():
                        logger.debug(f"Skipping due to mood mismatch: {song_mood} != {mood_filter}")
                        continue
                
                results.append(current_path)
                logger.info(f"Added to results: {current_path}")
                if len(results) >= n:
                    break
            
            logger.info(f"Found {len(results)} similar songs for {os.path.basename(song_path)}")
            return results
            
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
    
    def classify_mood(self, features: np.ndarray) -> str:
        """Classify the mood of an Indian music song based on its features.
    
    Args:
        features: Normalized feature vector of the song
        
    Returns:
        str: Mood classification ('romantic', 'dance', 'devotional', 'melancholic', 'peppy')
    """
    # Energy (RMS) and Valence (Chroma) based classification
    # More lenient thresholds for Indian film music
        energy = features[8]  # RMS mean
        valence = features[50]  # Chroma mean
        
        # Print feature values for debugging
        logger.debug(f"Energy: {energy}, Valence: {valence}")
        
        # Special case for devotional music (check filename first)
        file_path = self.features_df.iloc[0]['file_path'].lower()
        if any(term in file_path for term in ['bhajan', 'devotional', 'suprabhata']):
            return "devotional"
            
        # Special case for sad songs (check filename)
        if "sad" in file_path or "heartbreak" in file_path:
            return "melancholic"
            
        # Classify based on energy and valence with more lenient thresholds
        if energy > 0.7:  # High energy
            if valence > 0.6:
                return "dance"     # High energy, positive (dance/party songs)
            elif valence > 0.4:
                return "peppy"     # High energy, neutral (mass songs)
            else:
                return "mass"      # High energy, low valence (intense songs)
        elif energy > 0.5:  # Medium energy
            if valence > 0.6:
                return "romantic"  # Medium energy, positive (romantic songs)
            elif valence > 0.4:
                return "melodic"   # Medium energy, neutral (melodic songs)
            else:
                return "melancholic"  # Medium energy, negative (sad songs)
        else:  # Low energy
            if valence > 0.6:
                return "romantic"  # Low energy, positive (soft romantic)
            else:
                return "melancholic"  # Low energy, negative (sad songs)
    
    def get_genre(self, file_path: str) -> str:
        """Extract genre from file path or metadata for Indian music.
    
        Args:
            file_path: Path to the audio file
        
        Returns:
            str: Genre of the song (e.g., 'film', 'devotional', 'classical', 'folk', 'ghazal', 'item_song')
        """
        path = Path(file_path).name.lower()
    
        # Common Indian music genres
        if any(term in path for term in ['item', 'remix', 'dj', 'party']):
            return 'party'
        elif any(term in path for term in ['bhakti', 'devotional', 'bhajan', 'suprabhata']):
            return 'devotional'
        elif any(term in path for term in ['carnatic', 'karnatak', 'hindustani', 'classical']):
            return 'classical'
        elif any(term in path for term in ['folk', 'janapada', 'lavani', 'dandiya', 'garba']):
            return 'folk'
        elif any(term in path for term in ['ghazal', 'sufi', 'qawwali']):
            return 'ghazal'
        elif any(term in path for term in ['melody', 'romantic', 'love']):
            return 'melody'
        elif any(term in path for term in ['sad', 'heartbreak']):
            return 'sad'
        elif any(term in path for term in ['mass', 'peppy', 'dance']):
            return 'dance'
        else:
            return 'film'  # Default to film music (most common in Indian music)
    
def main():
    """Command-line interface for playlist generation."""
    parser = argparse.ArgumentParser(
        description="🎵 Generate playlists with similar song recommendations"
    )
    parser.add_argument("features_file", help="Path to features CSV file")
    parser.add_argument("output_file", help="Path to save the playlist")
    parser.add_argument("songs", nargs="+", help="Seed song paths")
    parser.add_argument("--name", help="Playlist name")
    parser.add_argument("--max-songs", type=int, default=20, 
                       help="Maximum songs in playlist")
    parser.add_argument("--no-shuffle", action="store_false", dest="shuffle",
                       help="Don't shuffle the playlist")
    parser.add_argument("--static", action="store_false", dest="dynamic",
                       help="Disable dynamic song addition")
    parser.add_argument("--genre", help="Filter by genre (e.g., 'rock', 'pop')")
    parser.add_argument("--mood", help="Filter by mood (e.g., 'energetic', 'chill')")
    parser.add_argument("--debug", action="store_true", 
                       help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        generator = PlaylistGenerator(args.features_file)
        success = generator.generate_playlist(
            args.songs,
            args.output_file,
            playlist_name=args.name,
            max_songs=args.max_songs,
            shuffle=args.shuffle,
            dynamic=args.dynamic,
            genre=args.genre,
            mood=args.mood
        )
        return 0 if success else 1
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1