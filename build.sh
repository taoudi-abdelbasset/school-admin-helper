#!/bin/bash

set -e

echo "=========================================="
echo "🚀 Too-Helper Desktop - Build Script"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Detect OS
OS_TYPE=$(uname -s)
echo -e "${BLUE}📟 Detected OS: $OS_TYPE${NC}"

APP_NAME="TooHelper"
VERSION="1.0.0"
SPEC_FILE="${APP_NAME}.spec"

FINAL_BUILD_DIR="build"           # ← new main output folder

# Clean previous builds
echo -e "\n${YELLOW}🧹 Cleaning previous builds...${NC}"
rm -rf build dist "$SPEC_FILE"

# ... (virtualenv check, pyinstaller install, spec generation - remains the same)

# Build the application
echo -e "\n${YELLOW}🔨 Building application...${NC}"
pyinstaller "$SPEC_FILE" --clean --noconfirm

# ────────────────────────────────────────────────
# New output organization logic
# ────────────────────────────────────────────────

mkdir -p "$FINAL_BUILD_DIR"

if [ -d "dist/TooHelper" ] || [ -d "dist/${APP_NAME}.app" ]; then
    echo -e "\n${GREEN}✅ Build successful!${NC}"

    case "$OS_TYPE" in
        Linux*)
            PLATFORM_DIR="${FINAL_BUILD_DIR}/linux"
            mkdir -p "$PLATFORM_DIR"
            
            echo -e "\n${YELLOW}→ Preparing Linux build${NC}"
            mv dist/TooHelper "${PLATFORM_DIR}/${APP_NAME}-linux-x64"
            
            echo -e "${YELLOW}→ Creating archive${NC}"
            tar -czf "${APP_NAME}-linux-x64.tar.gz" -C "$PLATFORM_DIR" "${APP_NAME}-linux-x64"
            
            echo -e "${GREEN}→ Created:${NC}"
            echo "   Folder:  ${PLATFORM_DIR}/${APP_NAME}-linux-x64/"
            echo "   Archive: ${APP_NAME}-linux-x64.tar.gz"
            ;;

        Darwin*)
            PLATFORM_DIR="${FINAL_BUILD_DIR}/macos"
            mkdir -p "$PLATFORM_DIR"

            if [ -d "dist/${APP_NAME}.app" ]; then
                echo -e "\n${YELLOW}→ Preparing macOS .app bundle${NC}"
                mv "dist/${APP_NAME}.app" "${PLATFORM_DIR}/${APP_NAME}.app"
                
                echo -e "${YELLOW}→ Creating archive${NC}"
                ditto -c -k --sequesterRsrc --keepParent "${PLATFORM_DIR}/${APP_NAME}.app" "${APP_NAME}-macos.app.zip"
            else
                echo -e "\n${YELLOW}→ Preparing macOS folder (no .app bundle)${NC}"
                mv dist/TooHelper "${PLATFORM_DIR}/${APP_NAME}-macos"
                ditto -c -k --sequesterRsrc --keepParent "${PLATFORM_DIR}/${APP_NAME}-macos" "${APP_NAME}-macos-folder.zip"
            fi

            echo -e "${GREEN}→ Created:${NC}"
            echo "   Folder:  ${PLATFORM_DIR}/${APP_NAME}.app  (or folder)"
            echo "   Archive: ${APP_NAME}-macos.app.zip"
            ;;

        MINGW*|MSYS*|CYGWIN*)
            PLATFORM_DIR="${FINAL_BUILD_DIR}/windows"
            mkdir -p "$PLATFORM_DIR"

            echo -e "\n${YELLOW}→ Preparing Windows build${NC}"
            mv dist/TooHelper "${PLATFORM_DIR}/${APP_NAME}-windows-x64"

            echo -e "${YELLOW}→ Creating archive${NC}"
            if command -v 7z >/dev/null 2>&1; then
                7z a "${APP_NAME}-windows-x64.zip" -r "./${PLATFORM_DIR}/${APP_NAME}-windows-x64"
            elif command -v zip >/dev/null 2>&1; then
                (cd "$PLATFORM_DIR" && zip -r "../../${APP_NAME}-windows-x64.zip" "${APP_NAME}-windows-x64")
            else
                echo -e "${YELLOW}⚠️ No zip/7z found → only folder created${NC}"
            fi

            echo -e "${GREEN}→ Created:${NC}"
            echo "   Folder:  ${PLATFORM_DIR}/${APP_NAME}-windows-x64/"
            echo "   Archive: ${APP_NAME}-windows-x64.zip (if zip tool available)"
            ;;
    esac

    # Final summary
    echo -e "\n${GREEN}=========================================="
    echo "           BUILD COMPLETE!"
    echo "==========================================${NC}"
    echo -e "Final artifacts are in: ${BLUE}${FINAL_BUILD_DIR}/${NC}"
    ls -l "$FINAL_BUILD_DIR"
    echo ""
    echo "Archives created in project root:"
    ls -lh *.tar.gz *.zip 2>/dev/null || true

else
    echo -e "\n${RED}❌ Build failed - dist/TooHelper not found${NC}"
    exit 1
fi