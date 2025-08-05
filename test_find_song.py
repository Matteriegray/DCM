import pandas as pd
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

try:
    # Load the features file
    logging.info("Loading features file...")
    df = pd.read_csv('features/Songs_features.csv')
    
    # Find the file path column (it's the 3rd to last column)
    file_path_col = df.columns[-3]
    
    # Get the first few file paths
    logging.info("First few songs in the features file:")
    for path in df[file_path_col].head():
        print(f"- {path}")
        
    # Save a sample file path for testing
    sample_path = df[file_path_col].iloc[0]
    with open('test_song_path.txt', 'w') as f:
        f.write(sample_path)
        
    logging.info(f"\nSample song path saved to test_song_path.txt")
    
except Exception as e:
    logging.error(f"Error: {e}")
    sys.exit(1)
