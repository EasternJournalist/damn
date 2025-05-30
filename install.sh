#!/bin/bash

set -e

DEST="$HOME/.local/bin"
SCRIPT_URL="https://raw.githubusercontent.com/EasternJournalist/damn/refs/heads/master/damn.py"
TARGET="$DEST/damn"

mkdir -p "$DEST"

curl -fsSL "$SCRIPT_URL" -o "$TARGET"

chmod +x "$TARGET"

# Check shell version
if [[ "$SHELL" == */zsh ]]; then
    # SHELL_RC="$HOME/.zshrc"
    echo "zsh is not supported yet. Please use bash."
    exit 1
elif [[ "$SHELL" == */bash ]]; then
    SHELL_RC="$HOME/.bashrc"
else
    echo "Unknown shell: $SHELL"
    exit 1
fi

# Add ~/.local/bin to PATH in ~/.bashrc
if ! grep -q 'export PATH=.*\.local/bin' $SHELL_RC 2>/dev/null; then
    echo -n "~/.local/bin is not in PATH in ~/.bashrc. Do you want to add it? [y/n] "
    read answer
    if [[ "$answer" == "y" ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> $SHELL_RC
        echo "✅ Added ~/.local/bin to PATH in $SHELL_RC"
    else
        echo "Nevermind. It still works without ~/.local/bin in PATH."
    fi
fi

# Initialize the key binding
$TARGET --init

# Source the rc file to enable the key binding
echo -e "🎉 damn installed! Try typing any instruction and pressing \033[33mAlt+d\033[0m. in your terminal."
