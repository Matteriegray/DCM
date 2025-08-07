# DCM Playlist Generator

A powerful music playlist generator application that helps you create playlists based on your music library and preferences. Built with Python, Kivy, and KivyMD for a cross-platform experience.

## Features

- **Music Library Management**: Organize and browse your music collection
- **Smart Playlist Generation**: Create playlists based on mood and genre
- **Cross-Platform**: Runs on Windows, macOS, Linux, and Android
- **Modern UI**: Clean and intuitive user interface built with KivyMD
- **Audio Analysis**: Advanced audio processing for smart recommendations

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ShashankMk031/DCM.git
   cd DCM
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python -m dcm.ui.main
```

### Navigation
- **Playlists**: View and manage your saved playlists
- **Library**: Browse your music library
- **Generate**: Create new playlists based on your preferences

## Project Structure

```
dcm/
├── ui/                  # User interface components
│   ├── main.py         # Main application entry point
│   ├── main_screen.py  # Main screen implementation
│   └── main.kv         # UI layout and styling
├── core/               # Core functionality
│   ├── __init__.py
│   └── playlist_generator.py
└── assets/             # Static assets (icons, images, etc.)
```

## Dependencies

- Python 3.8+
- Kivy 2.3.1
- KivyMD 2.0.1.dev0
- Librosa 0.11.0
- NumPy 1.26.4
- Pandas 1.5.3

## Contributing

Contributions are welcome! Please read our [contributing guidelines](CONTRIBUTING.md) before submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Kivy](https://kivy.org/) - The cross-platform Python framework
- [KivyMD](https://kivymd.readthedocs.io/) - Material Design widgets for Kivy
- [Librosa](https://librosa.org/) - Audio and music analysis in Python