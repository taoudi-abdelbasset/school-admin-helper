#!/bin/bash

###########################################
# Build Script for Too-Helper Desktop App
# Generates executables for Windows/Mac/Linux
###########################################

set -e  # Exit on error

echo "=========================================="
echo "🚀 Too-Helper Desktop - Build Script"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Detect OS
OS_TYPE=$(uname -s)
echo -e "${BLUE}📟 Detected OS: $OS_TYPE${NC}"

# App info
APP_NAME="TooHelper"
VERSION="1.0.0"
BUILD_DIR="dist"
SPEC_FILE="$APP_NAME.spec"

# Clean previous builds
echo -e "\n${YELLOW}🧹 Cleaning previous builds...${NC}"
rm -rf build dist "$SPEC_FILE"

# Check if virtual environment is active
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${RED}❌ Virtual environment not activated!${NC}"
    echo "Please run: source .venv/bin/activate"
    exit 1
fi

# Install/upgrade PyInstaller
echo -e "\n${YELLOW}📦 Installing PyInstaller...${NC}"
pip install --upgrade pyinstaller

# Create build directory
mkdir -p "$BUILD_DIR"

# Generate .spec file
echo -e "\n${YELLOW}📝 Generating PyInstaller spec file...${NC}"

cat > "$SPEC_FILE" << 'SPEC_EOF'
# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all data files
datas = [
    ('config', 'config'),
    ('ui', 'ui'),
    ('tools', 'tools'),
    ('core', 'core'),
    ('assets', 'assets'),
]

# Collect hidden imports
hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'fitz',  # PyMuPDF
    'openpyxl',
    'qtawesome',
]

# Collect all submodules
hiddenimports += collect_submodules('PyQt6')
hiddenimports += collect_submodules('fitz')
hiddenimports += collect_submodules('openpyxl')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'tkinter',
        'customtkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TooHelper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icons/app_icon.ico'           # ← Windows & Linux icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TooHelper',
)

# macOS app bundle
import sys
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='TooHelper.app',
        icon='assets/icons/app_icon.icns', # ← macOS icon
        icon=None,
        bundle_identifier='com.toohelper.app',
        info_plist={
            'NSHighResolutionCapable': 'True',
            'LSBackgroundOnly': 'False',
        },
    )
SPEC_EOF

echo -e "${GREEN}✅ Spec file created${NC}"

# Build the application
echo -e "\n${YELLOW}🔨 Building application...${NC}"
echo "This may take a few minutes..."

pyinstaller "$SPEC_FILE" --clean --noconfirm

# Check if build was successful
if [ -d "dist/TooHelper" ]; then
    echo -e "\n${GREEN}✅ Build successful!${NC}"
    
    # Get size
    BUILD_SIZE=$(du -sh dist/TooHelper | cut -f1)
    echo -e "${BLUE}📦 Build size: $BUILD_SIZE${NC}"
    
    # Create platform-specific package
    case "$OS_TYPE" in
        Linux*)
            echo -e "\n${YELLOW}📦 Linux (folder + tar.gz)${NC}"
            cd dist
            mv TooHelper "TooHelper-linux"
            tar -czf "../TooHelper-linux-x64.tar.gz" "TooHelper-linux"
            echo -e "${GREEN}→ TooHelper-linux-x64.tar.gz${NC}"
            cd ..
            ;;

        Darwin*)
            if [ -d "dist/TooHelper.app" ]; then
                echo -e "\n${YELLOW}📦 macOS .app bundle${NC}"
                cd dist
                zip -r "../TooHelper-macos.app.zip" "TooHelper.app"
                echo -e "${GREEN}→ TooHelper-macos.app.zip${NC}"
                cd ..
            else
                echo -e "${RED}No .app bundle created! Check .spec file${NC}"
            fi
            ;;

        MINGW*|MSYS*|CYGWIN*)
            echo -e "\n${YELLOW}📦 Windows${NC}"
            cd dist
            mv TooHelper "TooHelper-windows"
            if command -v 7z &> /dev/null; then
                7z a -tzip "../TooHelper-windows-x64.zip" "TooHelper-windows"
            elif command -v zip &> /dev/null; then
                zip -r "../TooHelper-windows-x64.zip" "TooHelper-windows"
            else
                echo "No zip/7z → leaving folder only"
            fi
            echo -e "${GREEN}→ TooHelper-windows-x64.zip${NC}"
            cd ..
            ;;
    esac
    
    # Show output location
    echo -e "\n${GREEN}=========================================="
    echo "✅ BUILD COMPLETE!"
    echo "==========================================${NC}"
    echo -e "${BLUE}Output location:${NC} $(pwd)/dist/"
    echo ""
    echo "To run the application:"
    case "$OS_TYPE" in
        Linux*)
            echo "  ./dist/TooHelper/TooHelper"
            ;;
        Darwin*)
            if [ -d "dist/TooHelper.app" ]; then
                echo "  open dist/TooHelper.app"
            else
                echo "  ./dist/TooHelper/TooHelper"
            fi
            ;;
        MINGW*|MSYS*|CYGWIN*)
            echo "  dist\\TooHelper\\TooHelper.exe"
            ;;
    esac
    echo ""
    
else
    echo -e "\n${RED}❌ Build failed!${NC}"
    echo "Check the output above for errors."
    exit 1
fi