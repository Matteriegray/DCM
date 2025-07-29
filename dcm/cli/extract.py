"""
CLI command for extracting audio features from music files.
"""

import click
from pathlib import Path
from typing import Optional

from dcm.core.extract_features import process_directory

@click.command()
@click.argument(
    'input_dir',
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path)
)
@click.option(
    '--output',
    '-o',
    type=click.Path(dir_okay=False, path_type=Path),
    default='audio_features.csv',
    help='Output file path (CSV or JSON)',
    show_default=True
)
@click.option(
    '--force',
    '-f',
    is_flag=True,
    help='Overwrite existing output file',
    default=False
)
@click.option(
    '--verbose',
    '-v',
    is_flag=True,
    help='Enable verbose output',
    default=False
)
def extract(input_dir: Path, output: Path, force: bool, verbose: bool) -> None:
    """
    Extract audio features from music files in the specified directory.
    
    This command processes all supported audio files in the input directory
    and extracts various audio features using librosa. The features are saved
    to the specified output file in CSV or JSON format.
    
    Supported audio formats: .mp3, .wav, .flac, .ogg, .m4a, .aac
    """
    # Set up logging
    import logging
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Process the directory
    try:
        df = process_directory(input_dir, output, force)
        
        if df.empty:
            click.echo("No features were extracted. Check the log for errors.", err=True)
            raise click.Abort()
            
        click.echo(f"\nSuccessfully extracted features for {len(df)} audio files.")
        click.echo(f"Features saved to: {output.absolute()}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()

if __name__ == "__main__":
    extract()
