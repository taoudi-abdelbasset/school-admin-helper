# TooHelper - Desktop Toolkit Application

[![Build Status](https://github.com/taoudi-abdelbasset/school-admin-helper/workflows/Build%20TooHelper%20for%20Windows/macOS/Linux/badge.svg)](https://github.com/taoudi-abdelbasset/school-admin-helper/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)

A modern, cross-platform desktop application providing essential productivity tools with a focus on PDF generation and data management.

## Features

- **PDF Generator**: Create customized PDF documents from templates and CSV/Excel data
  - Visual template editor with drag-and-drop fields
  - Support for multiple fonts, colors, and text alignment
  - Bulk PDF generation from data tables
  - Import data from CSV or Excel files
  
- **Multi-language Support**: English, French, and Arabic interfaces
- **Theme System**: Dark, Light, and VS Code themes
- **Recent Tools Tracking**: Quick access to frequently used features
- **Favorites System**: Pin your most-used tools for easy access

## Installation

### Pre-built Binaries (Recommended)

Download the latest release for your operating system:

**Windows:**
```bash
# Download TooHelper-windows-x64.zip from releases
# Extract the archive
# Run TooHelper.exe
```

**macOS:**
```bash
# Download TooHelper-macos.app.zip from releases
# Extract and open TooHelper.app
# If blocked by security: Right-click → Open
```

**Linux:**
```bash
# Download TooHelper-linux-x64.tar.gz from releases
tar -xzf TooHelper-linux-x64.tar.gz
cd TooHelper
./TooHelper
```

### From Source

**Prerequisites:**
- Python 3.12 or higher
- pip package manager

**Installation Steps:**

1. Clone the repository:
```bash
git clone https://github.com/taoudi-abdelbasset/school-admin-helper.git
cd school-admin-helper
```

2. Create and activate virtual environment:
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python main.py
```

## Quick Start

### PDF Generator Tool

1. **Create a Project**
   - Click "New Project" from the Projects dashboard
   - Enter project name and description
   - Upload a PDF template file

2. **Design Your Template**
   - Add data nodes (variables like `firstname`, `lastname`, etc.)
   - Place fields on the template by clicking "Add Field"
   - Customize font, size, color, and alignment
   - Use resize handles to adjust field dimensions

3. **Import Data**
   - Click "Data Table" to manage your data
   - Import from CSV or Excel files
   - Or add rows manually using the form

4. **Generate PDFs**
   - Click "Generate PDFs" button
   - Choose output location
   - Wait for batch processing to complete

## Building from Source

### Build Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build for current platform
pyinstaller TooHelper.spec --clean --noconfirm

# Executable will be in dist/TooHelper/
```

### Automated Multi-Platform Builds

The project includes GitHub Actions workflow for automated builds:

```bash
# Create a new release tag
git tag v1.0.0
git push origin v1.0.0

# GitHub Actions will automatically build for Windows, macOS, and Linux
```

## Project Structure

```
too-helper/
├── assets/              # Application icons and resources
├── config/              # Configuration and language files
│   └── languages/       # Translation files (en, ar, fr)
├── core/                # Core application logic
│   ├── app_pyqt6.py    # Main application window
│   └── tool_manager.py  # Tool discovery and management
├── tools/               # Individual tool modules
│   └── pdf_generator/   # PDF generation tool
├── ui/                  # UI components
├── data/                # User data storage
├── main.py              # Application entry point
└── requirements.txt     # Python dependencies
```

## Dependencies

- **PyQt6**: Modern UI framework
- **PyMuPDF (fitz)**: PDF manipulation
- **openpyxl**: Excel file support
- **qtawesome**: Icon library

## Language Support

Switch between languages in Settings:
- **English** (en)
- **العربية** (ar) - Arabic
- **Français** (fr) - French

## Themes

Available themes:
- **Dark** - Modern dark interface (default)
- **Light** - Clean light interface
- **VS Code** - Developer-friendly theme

## Configuration

User settings and data are stored in:
- **Windows**: `data/app_data.json`
- **macOS**: `data/app_data.json`
- **Linux**: `data/app_data.json`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Abdelbasset Taoudi**

- GitHub: [@taoudi-abdelbasset](https://github.com/taoudi-abdelbasset)

## Bug Reports

Found a bug? Please open an issue on GitHub with:
- Operating system and version
- Python version (if running from source)
- Steps to reproduce
- Expected vs actual behavior

## Feature Requests

Have an idea? Open an issue with the `enhancement` label and describe:
- The problem you're trying to solve
- Your proposed solution
- Any alternatives you've considered