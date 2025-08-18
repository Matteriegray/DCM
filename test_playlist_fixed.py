#!/usr/bin/env python3
"""
Test script for the fixed playlist generator
"""

import os
import sys
import tempfile
import pandas as pd
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def create_test_features():
    """Create a test features dataset."""
    return pd.DataFrame({
        'file_path': [
            '/music/song1.mp3',
            '/music/song2.mp3',
            '/music/song3.mp3',
            '/music/song4.mp3',
            '/music/song5.mp3',
        ],
        'tempo': [120.0, 125.0, 118.0, 130.0, 140.0],
        'energy': [0.8, 0.7, 0.9, 0.6, 0.5],
        'danceability': [0.7, 0.8, 0.6, 0.5, 0.4],
        'genre': ['pop', 'rock', 'pop', 'jazz', 'classical'],
        'mood': ['happy', 'energetic', 'sad', 'calm', 'romantic']
    })

def test_playlist_generator():
    """Test the fixed playlist generator."""
    print("🚀 Testing Fixed Playlist Generator")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test features file
        features_file = os.path.join(temp_dir, 'test_features.csv')
        features_df = create_test_features()
        features_df.to_csv(features_file, index=False)
        
        print(f"✅ Created test features at: {features_file}")
        
        try:
            # Import the fixed generator
            from dcm.core.generate_playlist_fixed import PlaylistGenerator
            
            # Initialize with test data
            generator = PlaylistGenerator(features_file)
            print("✅ Successfully initialized PlaylistGenerator")
            
            # Test basic playlist generation
            output_file = os.path.join(temp_dir, 'test_playlist.m3u')
            print("\n🔍 Testing basic playlist generation...")
            
            success = generator.generate_playlist(
                song_paths=['/music/song1.mp3'],
                output_file=output_file,
                playlist_name="Test Playlist",
                max_songs=3
            )
            
            if success and os.path.exists(output_file):
                print("\n✅ Playlist generated successfully!")
                print("\n📋 Playlist content:")
                with open(output_file) as f:
                    print(f.read())
                return 0
            else:
                print("\n❌ Failed to generate playlist")
                return 1
                
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return 1

if __name__ == "__main__":
    sys.exit(test_playlist_generator())
