#!/bin/bash

# Colors
RED="\033[91m"
GREEN="\033[92m"
YELLOW="\033[93m"
CYAN="\033[96m"
RESET="\033[0m"
BOLD="\033[1m"

REPO_URL="https://github.com/WeAreMS/Lotus.git"
INSTALL_DIR="$HOME/Lotus"

clear

echo -e "${BOLD}${GREEN}[+] Starting Lotus Installation/Update...${RESET}"
sleep 1

echo -e "${BOLD}${CYAN}[*] Updating package lists...${RESET}"
pkg update -y
pkg upgrade -y

echo -e "${BOLD}${CYAN}[*] Installing required packages...${RESET}"
pkg install -y git python

# Clone or update Lotus
if [ -d "$INSTALL_DIR/.git" ]; then
    echo -e "${BOLD}${CYAN}[*] Lotus is already installed. Updating...${RESET}"
    cd "$INSTALL_DIR" || exit
    git pull
else
    echo -e "${BOLD}${CYAN}[*] Downloading Lotus from GitHub...${RESET}"
    rm -rf "$INSTALL_DIR"
    git clone "$REPO_URL" "$INSTALL_DIR"
fi

# Make executable
chmod +x "$INSTALL_DIR/lotus.py"

# Create launcher
echo -e "${BOLD}${CYAN}[*] Creating Lotus command...${RESET}"

cat > "$PREFIX/bin/Lotus" << EOF
#!/data/data/com.termux/files/usr/bin/bash
python3 \$HOME/Lotus/lotus.py
EOF

chmod +x "$PREFIX/bin/Lotus"

echo
echo -e "${BOLD}${GREEN}[+] Lotus has been installed successfully!${RESET}"
echo -e "${BOLD}${YELLOW}Start Lotus anytime by typing:${RESET}"
echo -e "${BOLD}${GREEN}Lotus${RESET}"
