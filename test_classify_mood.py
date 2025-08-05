import sys
import os
import numpy as np

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dcm.core.generate_playlist import PlaylistGenerator

def test_classify_mood():
    # Create a mock PlaylistGenerator instance
    # We'll use a dummy features file for testing
    test_csv = "test_features.csv"
    
    # Create a simple test features file if it doesn't exist
    if not os.path.exists(test_csv):
        with open(test_csv, 'w') as f:
            f.write("file_path,file_name,file_extension,file_size_mb,feature_1,feature_2,feature_3,feature_4,feature_5,feature_6,feature_7,feature_8,feature_9,feature_10\n")
            f.write("test_song.mp3,test_song,mp3,5.2,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0\n")
    
    # Initialize the PlaylistGenerator
    pg = PlaylistGenerator(test_csv)
    
    # Test case 1: High energy, high valence (should be "dance")
    test_features1 = np.zeros(100)  # Initialize with zeros
    test_features1[8] = 0.9  # High energy
    test_features1[50] = 0.9  # High valence
    print("Test 1 - Expected: dance, Got:", pg.classify_mood(test_features1))
    
    # Test case 2: Low energy, low valence (should be "melancholic")
    test_features2 = np.zeros(100)
    test_features2[8] = -0.9  # Low energy
    test_features2[50] = -0.9  # Low valence
    print("Test 2 - Expected: melancholic, Got:", pg.classify_mood(test_features2))
    
    # Test case 3: Medium energy, medium valence (should be "romantic")
    test_features3 = np.zeros(100)
    test_features3[8] = 0.2  # Medium energy
    test_features3[50] = 0.6  # Medium valence
    print("Test 3 - Expected: romantic, Got:", pg.classify_mood(test_features3))
    
    # Test case 4: Special case - devotional music
    test_features4 = np.zeros(100)
    # This will test the special case for devotional music in the filename
    pg.features_df.iloc[0]['file_path'] = 'bhajan_song.mp3'
    print("Test 4 - Expected: devotional, Got:", pg.classify_mood(test_features4))

if __name__ == "__main__":
    test_classify_mood()
