#!/bin/bash

echo "🔧 Running MysteryMM Setup Install..."

# Install Python packages
echo "📦 Installing Python dependencies..."
pip install pillow pyperclip requests
if [ $? -eq 0 ]; then
    echo "✅ Python dependencies installed."
else
    echo "❌ Failed to install Python packages."
fi

# Check for solana-keygen
if ! command -v solana-keygen &> /dev/null
then
    echo "🔍 solana-keygen not found. Installing Solana CLI..."

    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
    elif [[ "$OSTYPE" == "msys" ]]; then
        echo "➡️ Windows detected. Please run this in PowerShell manually:"
        echo 'iwr https://release.solana.com/stable/solana-install-init.exe -OutFile solana-install.exe; ./solana-install.exe'
    fi

    echo "✅ Solana CLI installation initiated. Please restart your terminal after install."
else
    echo "✅ solana-keygen is already installed."
fi
