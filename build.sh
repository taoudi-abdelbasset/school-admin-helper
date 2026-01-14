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
SPEC_FILE="${APP_NAME}.spec"
FINAL_OUTPUT_DIR="build"           # Where final organized builds will go

# ────────────────────────────────────────────────
# Clean ONLY build artifacts (not .spec!)
# ────────────────────────────────────────────────
echo -e "\n${YELLOW}🧹 Cleaning previous build artifacts...${NC}"
rm -rf dist build

# Check virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${RED}❌ Virtual environment not activated!${NC}"
    echo "Please run: source .venv/bin/activate"
    exit 1
fi

# Install/upgrade PyInstaller
echo -e "\n${YELLOW}📦 Installing/Upgrading PyInstaller...${NC}"
pip install --upgrade pyinstaller

# Generate .spec file (only if it doesn't exist or you want to force)
echo -e "\n${YELLOW}📝 Checking/Generating PyInstaller spec file...${NC}"

if [ ! -f "$SPEC_FILE" ]; then
    echo "→ Creating new $SPEC_FILE"
    cat > "$SPEC_FILE" << 'SPEC_EOF'
# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

datas = [
    ('config', 'config'),
    ('ui', 'ui'),
    ('tools', 'tools'),
    ('core', 'core'),
    ('assets', 'assets'),
]

hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'fitz',  # PyMuPDF
    'openpyxl',
    'qtawesome',
]

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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icons/app_icon.ico'
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

if sys.platform.startswith('darwin'):
    app = BUNDLE(
        coll,
        name='TooHelper.app',
        icon='assets/icons/app_icon.icns',
        bundle_identifier='com.toohelper.app',
        info_plist={
            'NSHighResolutionCapable': 'True',
            'LSBackgroundOnly': 'False',
            'CFBundleShortVersionString': '1.0.0',
        },
    )
SPEC_EOF
    echo -e "${GREEN}→ Spec file created${NC}"
else
    echo -e "${BLUE}→ Using existing $SPEC_FILE${NC}"
fi

# Build
echo -e "\n${YELLOW}🔨 Building application... (may take several minutes)${NC}"
pyinstaller "$SPEC_FILE" --clean --noconfirm

# ────────────────────────────────────────────────
# Organize output
# ────────────────────────────────────────────────
mkdir -p "$FINAL_OUTPUT_DIR"

if [ -d "dist/$APP_NAME" ] || [ -d "dist/$APP_NAME.app" ]; then
    echo -e "\n${GREEN}✅ Build successful!${NC}"

    case "$OS_TYPE" in
        Linux*)
            PLATFORM_DIR="$FINAL_OUTPUT_DIR/linux-x64"
            mkdir -p "$PLATFORM_DIR"
            mv "dist/$APP_NAME" "$PLATFORM_DIR/$APP_NAME"
            tar -czf "$APP_NAME-linux-x64.tar.gz" -C "$PLATFORM_DIR" "$APP_NAME"
            echo -e "${GREEN}→ Created:${NC} $APP_NAME-linux-x64.tar.gz"
            ;;

        Darwin*)
            PLATFORM_DIR="$FINAL_OUTPUT_DIR/macos"
            mkdir -p "$PLATFORM_DIR"
            if [ -d "dist/$APP_NAME.app" ]; then
                mv "dist/$APP_NAME.app" "$PLATFORM_DIR/"
                ditto -c -k --sequesterRsrc --keepParent "$PLATFORM_DIR/$APP_NAME.app" "$APP_NAME-macos.app.zip"
                echo -e "${GREEN}→ Created:${NC} $APP_NAME-macos.app.zip"
            else
                mv "dist/$APP_NAME" "$PLATFORM_DIR/$APP_NAME-macos"
                zip -r "$APP_NAME-macos-folder.zip" "$PLATFORM_DIR/$APP_NAME-macos"
                echo -e "${GREEN}→ Created:${NC} $APP_NAME-macos-folder.zip (no .app bundle)"
            fi
            ;;

        MINGW*|MSYS*|CYGWIN*)
            PLATFORM_DIR="$FINAL_OUTPUT_DIR/windows-x64"
            mkdir -p "$PLATFORM_DIR"
            mv "dist/$APP_NAME" "$PLATFORM_DIR/$APP_NAME"
            if command -v 7z >/dev/null 2>&1; then
                (cd "$FINAL_OUTPUT_DIR" && 7z a "../$APP_NAME-windows-x64.zip" "windows-x64/$APP_NAME")
            elif command -v zip >/dev/null 2>&1; then
                (cd "$PLATFORM_DIR" && zip -r "../../$APP_NAME-windows-x64.zip" "$APP_NAME")
            else
                echo -e "${YELLOW}→ No zip/7z → only folder created${NC}"
            fi
            [ -f "$APP_NAME-windows-x64.zip" ] && echo -e "${GREEN}→ Created:${NC} $APP_NAME-windows-x64.zip"
            ;;
    esac

    echo -e "\n${GREEN}=========================================="
    echo "           BUILD COMPLETE!"
    echo "==========================================${NC}"
    echo -e "Organized builds → ${BLUE}$FINAL_OUTPUT_DIR/${NC}"
    echo "Archives in current directory:"
    ls -lh *.tar.gz *.zip 2>/dev/null || echo "   (no archives created)"
else
    echo -e "\n${RED}❌ Build failed — dist folder not found${NC}"
    echo "Check PyInstaller output above for errors"
    exit 1
fi