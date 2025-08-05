#!/usr/bin/env python3
"""
Test script to examine the features file and test song matching.
"""
import pandas as pd
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def examine_features_file(features_file):
    """Examine the structure of the features file."""
    logger.info(f"Examining features file: {features_file}")
    
    # Load just the first few rows to understand the structure
    df = pd.read_csv(features_file, nrows=5)
    
    # Print column information
    logger.info("Columns in features file:")
    for i, col in enumerate(df.columns):
        logger.info(f"  {i}: {col}")
    
    # Print the first few rows of important columns
    if 'file_path' in df.columns and 'file_name' in df.columns:
        logger.info("\nFirst few songs in features file:")
        for _, row in df[['file_path', 'file_name']].head(3).iterrows():
            logger.info(f"- Path: {row['file_path']}")
            logger.info(f"  Name: {row['file_name']}")
    
    # Save a sample song for testing
    if not df.empty:
        sample_song = df.iloc[0]['file_path']
        with open('test_song.txt', 'w') as f:
            f.write(sample_song)
        logger.info(f"\nSample song path saved to test_song.txt")

if __name__ == "__main__":
    features_file = "features/Songs_features.csv"
    examine_features_file(features_file)
