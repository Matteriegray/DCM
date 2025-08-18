#!/usr/bin/env python3
"""
DCM Playlist Generation Test

This script tests the playlist generation functionality.
"""

import os
import sys
import tempfile
import logging
import pandas as pd
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def create_sample_features():
    """Create a sample features DataFrame for testing."""
    data = {
        'file_path': [
            '/music/song1.mp3',
            '/music/song2.mp3',
            '/music/song3.mp3',
            '/music/song4.mp3',
            '/music/song5.mp3',
        ],
        'tempo': [120.5, 125.0, 118.0, 130.0, 115.5],
        'energy': [0.8, 0.7, 0.9, 0.6, 0.75],
        'danceability': [0.7, 0.65, 0.8, 0.5, 0.6],
        'valence': [0.8, 0.6, 0.4, 0.7, 0.5],
        'genre': ['pop', 'rock', 'pop', 'jazz', 'rock'],
        'mood': ['happy', 'energetic', 'sad', 'calm', 'happy']
    }
    return pd.DataFrame(data)

def run_tests():
    """Run the playlist generation tests."""
    print("🚀 Starting DCM Playlist Generation Tests")
    print("=" * 40)
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test features file
        features_file = os.path.join(temp_dir, 'test_features.csv')
        features_df = create_sample_features()
        features_df.to_csv(features_file, index=False)
        
        print(f"✅ Created test features file at: {features_file}")
        
        try:
            from dcm.core.generate_playlist import PlaylistGenerator
            generator = PlaylistGenerator(features_file)
            print("✅ Successfully initialized PlaylistGenerator")
            
            # Test 1: Basic playlist generation
            print("\n🔍 Testing basic playlist generation...")
            output_file = os.path.join(temp_dir, 'basic_playlist.m3u')
            
            success = generator.generate_playlist(
                song_paths=['/music/song1.mp3'],
                output_file=output_file,
                playlist_name="Test Playlist",
                max_songs=3,
                progress_callback=lambda p, s: print(f"\rProgress: {p*100:.1f}% - {s}", end='')
            )
            
            if success and os.path.exists(output_file):
                print("\n✅ Test 1: Basic playlist generation passed!")
                print("\n📋 Playlist content:")
                with open(output_file, 'r') as f:
                    print(f.read())
            else:
                print("\n❌ Test 1: Basic playlist generation failed")
                return 1
            
            # Test 2: Mood-based playlist
            print("\n🔍 Testing mood-based playlist...")
            mood_output = os.path.join(temp_dir, 'mood_playlist.m3u')
            
            success = generator.generate_playlist(
                song_paths=['/music/song1.mp3'],
                output_file=mood_output,
                playlist_name="Mood Playlist",
                mood="happy",
                max_songs=3,
                progress_callback=lambda p, s: print(f"\rProgress: {p*100:.1f}% - {s}", end='')
            )
            
            if success and os.path.exists(mood_output):
                print("\n✅ Test 2: Mood-based playlist passed!")
            else:
                print("\n❌ Test 2: Mood-based playlist failed")
                return 1
            
            print("\n🎉 All tests passed successfully!")
            return 0
            
        except Exception as e:
            print(f"\n❌ Error during testing: {str(e)}")
            import traceback
            traceback.print_exc()
            return 1

if __name__ == "__main__":
    sys.exit(run_tests())
