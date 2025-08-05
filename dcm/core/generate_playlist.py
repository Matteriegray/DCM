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
    
    def _get_song_index(self, song_path: str) -> Optional[int]:
        """Helper to find a song index by filename or path.
        
        Args:
            song_path: Path or filename of the song
            
        Returns:
            Index of the song in the features dataframe, or None if not found
        """
        # Get just the filename
        song_filename = str(Path(song_path).name)
        
        # First try matching the full path (if provided)
        if Path(song_path).is_absolute():
            matches = self.features_df['file_path'] == song_path
            if matches.any():
                return matches.idxmax()
        
        # Try matching just the filename in the file_path column
        matches = self.features_df['file_path'].str.endswith(song_filename)
        if matches.any():
            return matches.idxmax()
            
        # Try case-insensitive filename match
        matches = self.features_df['file_path'].str.lower().str.endswith(song_filename.lower())
        if matches.any():
            return matches.idxmax()
            
        # Try matching the filename with the file_name column if it exists
        if 'file_name' in self.features_df.columns:
            matches = self.features_df['file_name'] == song_filename
            if matches.any():
                return matches.idxmax()
                
            # Case-insensitive match with file_name
            matches = self.features_df['file_name'].str.lower() == song_filename.lower()
            if matches.any():
                return matches.idxmax()
        
        logger.warning(f"Song not found in database: {song_path}")
        logger.debug(f"Available songs: {self.features_df['file_path'].head().tolist()}")
        return None
        
    def find_similar_songs(
        self, 
        song_path: str, 
        n: int = 5, 
        genre_filter: Optional[str] = None,
        mood_filter: Optional[str] = None,
        mood_similarity_threshold: float = 0.7
    ) -> List[str]:
        """Find n songs similar to the given song with optional filters.
        
        Args:
            song_path: Path or filename of the reference song
            n: Number of similar songs to find
            genre_filter: Optional genre to filter by
            mood_filter: Optional mood to filter by
            mood_similarity_threshold: Threshold for mood similarity (0-1)
            
        Returns:
            List of paths to similar songs matching the filters
        """
        try:
            logger.debug(f"[DEBUG] Finding similar songs for: {song_path}")
            song_idx = self._get_song_index(song_path)
            
            if song_idx is None:
                logger.warning(f"[DEBUG] Song not found in database: {song_path}")
                return []
                
            logger.debug(f"[DEBUG] Found song at index: {song_idx}")
            features = self.get_feature_vectors()
            
            # Debug logging for features
            logger.debug(f"[DEBUG] Features shape: {features.shape if hasattr(features, 'shape') else 'N/A'}")
            logger.debug(f"[DEBUG] Features type: {type(features)}")
            
            # Get similarity scores
            from sklearn.metrics.pairwise import cosine_similarity
            
            # Ensure we have a 2D array for the reference song
            try:
                ref_song_features = features[song_idx:song_idx+1]  # This ensures 2D array with shape (1, n_features)
                logger.debug(f"[DEBUG] Reference song features shape: {ref_song_features.shape if hasattr(ref_song_features, 'shape') else 'N/A'}")
                
                # Calculate similarities between reference song and all other songs
                similarities = cosine_similarity(ref_song_features, features)
                logger.debug(f"[DEBUG] Similarities shape: {similarities.shape if hasattr(similarities, 'shape') else 'N/A'}")
                
                # Flatten the similarities array if needed
                if len(similarities.shape) > 1 and similarities.shape[0] == 1:
                    similarities = similarities[0]
                
                logger.debug(f"[DEBUG] Final similarities shape: {similarities.shape if hasattr(similarities, 'shape') else 'N/A'}")
                
                # Get indices sorted by similarity (descending)
                similar_indices = similarities.argsort()[::-1]
                
                # Filter and collect results
                results = []
                for idx in similar_indices:
                    # Skip the reference song itself
                    if idx == song_idx:
                        continue
                    
                    # Get the song path and metadata
                    song_row = self.features_df.iloc[idx]
                    song_path = song_row['file_path']
                    
                    # Apply genre filter if specified
                    if genre_filter and 'genre' in song_row and song_row['genre'] != genre_filter:
                        logger.debug(f"Skipping {song_path} - genre mismatch")
                        continue
                    
                    # Apply mood filter if specified
                    if mood_filter:
                        song_mood = self.classify_mood(song_row)
                        mood_score = self._get_mood_similarity(mood_filter, song_mood)
                        if mood_score < mood_similarity_threshold:
                            logger.debug(f"Skipping {song_path} - mood mismatch ({song_mood} vs {mood_filter})")
                            continue
                    
                    results.append(song_path)
                    if len(results) >= n:
                        break
                
                return results
                
            except Exception as e:
                logger.error(f"[DEBUG] Error in similarity calculation: {e}", exc_info=True)
                return []
                
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
        """Classify the mood of a song based on its audio features.
        
        This implementation uses a combination of energy, valence, and other features
        to determine the mood in a way that works across different music styles.
        
        Args:
            features: Normalized feature vector of the song
            
        Returns:
            str: Mood classification ('romantic', 'dance', 'devotional', 'melancholic', 'peppy', 'energetic')
        """
        try:
            # Extract relevant features with bounds checking
            energy = min(max(features[8], -1), 1)  # RMS mean (energy)
            valence = min(max(features[50], -1), 1)  # Chroma mean (valence)
            
            # Get additional features if available
            tempo = features[98] if len(features) > 98 else 0  # Tempo feature if available
            
            # Special case for devotional music (check filename first)
            file_path = self.features_df.iloc[0]['file_path'].lower()
            if any(term in file_path for term in ['bhajan', 'devotional', 'bhakti', 'suprabhata']):
                return "devotional"
                
            # Special case for sad songs (check filename)
            if any(term in file_path for term in ['sad', 'heartbreak', 'dukkha']):
                return "melancholic"
            
            # Normalize energy and valence to 0-1 range
            energy_norm = (energy + 1) / 2  # Convert from -1:1 to 0:1
            valence_norm = (valence + 1) / 2  # Convert from -1:1 to 0:1
            
            # Classify based on energy and valence
            if energy_norm > 0.7:
                if valence_norm > 0.7:
                    return "dance"
                elif valence_norm > 0.5:
                    return "peppy"
                elif valence_norm > 0.3:
                    return "energetic"
                else:
                    return "intense"
                    
            elif energy_norm > 0.4:
                if valence_norm > 0.7:
                    return "romantic"
                elif valence_norm > 0.5:
                    return "melodic"
                elif valence_norm > 0.3:
                    return "mellow"
                else:
                    return "melancholic"
                    
            else:  # Low energy
                if valence_norm > 0.7:
                    return "romantic"
                elif valence_norm > 0.5:
                    return "calm"
                elif valence_norm > 0.3:
                    return "mellow"
                else:
                    return "melancholic"
                    
        except Exception as e:
            logger.warning(f"Error in mood classification: {e}")
            return "unknown"  # Default fallback
            
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
            
    def _get_mood_similarity(self, mood1: str, mood2: str) -> float:
        """Calculate similarity between two mood strings.
        
        Args:
            mood1: First mood
            mood2: Second mood
            
        Returns:
            Similarity score between 0 and 1
        """
        # Define mood groups that are considered similar
        mood_groups = {
            'dance': {'dance', 'peppy', 'energetic', 'party'},
            'romantic': {'romantic', 'melodic', 'calm', 'mellow'},
            'melancholic': {'melancholic', 'sad', 'mellow'},
            'energetic': {'energetic', 'dance', 'peppy', 'party'},
            'devotional': {'devotional', 'spiritual'}
        }
        
        mood1 = mood1.lower()
        mood2 = mood2.lower()
        
        # Exact match
        if mood1 == mood2:
            return 1.0
            
        # Check if moods are in the same group
        for group in mood_groups.values():
            if mood1 in group and mood2 in group:
                return 0.8  # High similarity for same group
                
        # No match
        return 0.0
    
def main():
    """Command-line interface for playlist generation"""
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