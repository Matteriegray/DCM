#!/usr/bin/env python3
"""
DCM Playlist Generation Test

This script tests the playlist generation functionality with a simple interface.
"""

import os
import sys
import logging
from pathlib import Path
from dcm.core.generate_playlist import PlaylistGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_progress(progress: float, status: str) -> bool:
    """Simple progress callback that prints to console."""
    print(f"\rProgress: {progress*100:.1f}% - {status}", end="")
    if progress >= 1.0 or progress < 0:
        print()  # New line when done or on error
    return True

def main():
    # Path to features file
    features_file = os.path.expanduser("~/.dcm/features/combined_features.csv")
    
    if not os.path.exists(features_file):
        logger.error(f"Features file not found at {features_file}")
        logger.info("Please run feature extraction first.")
        return
    
    # Initialize playlist generator
    logger.info("Initializing playlist generator...")
    generator = PlaylistGenerator(features_file)
    
    # Get list of available songs
    songs = generator.features_df['file_path'].tolist()
    if not songs:
        logger.error("No songs found in the features database")
        return
    
    # Use first 3 songs as seed
    seed_songs = songs[:3]
    
    # Generate playlist
    output_file = "generated_playlist.m3u"
    logger.info("\nGenerating playlist...")
    
    success = generator.generate_playlist(
        song_paths=seed_songs,
        output_file=output_file,
        playlist_name="My Generated Playlist",
        mood=None,  # Try 'happy', 'sad', 'energetic', etc.
        genre=None,  # Try 'bollywood', 'classical', etc.
        max_songs=10,
        shuffle=True,
        progress_callback=print_progress,
        dynamic=True
    )
    
    if success:
        logger.info(f"\nPlaylist generated successfully at: {os.path.abspath(output_file)}")
    else:
        logger.error("Failed to generate playlist")

if __name__ == "__main__":
    main()
