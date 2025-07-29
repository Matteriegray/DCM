"""
Main entry point for the DCM (Desktop/Mobile Music Assistant) CLI.
"""

import click
from pathlib import Path
from typing import Optional

# Import CLI modules
from dcm.cli.extract import extract

@click.group()
@click.version_option()
def cli():
    """
    DCM (Desktop/Mobile Music Assistant)
    
    A privacy-focused, offline music player with AI-powered recommendations.
    """
    pass

# Add commands
cli.add_command(extract, name="extract")

if __name__ == "__main__":
    cli()
