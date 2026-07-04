# 🪷 Lotus - Advanced Termux Tool Manager

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Platform-Termux-green?logo=android&logoColor=white" alt="Termux">
  <img src="https://img.shields.io/badge/Root-Required%20No-red" alt="Rootless">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License">
</div>

<br>

**Lotus** is a modern, rootless tool manager designed from the ground up specifically for the **Termux** environment. Featuring plugin support and dynamic JSON-based tool updates, it allows you to manage cybersecurity, development, and system tools from a single, sleek, and highly customizable menu.

---

## 📑 Table of Contents
- [Features](#-features)
- [Screenshots](#-screenshots)
- [Installation](#-installation)
- [Usage](#-usage)
- [Plugin System](#-plugin-system)
- [Themes](#-themes)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

- 🚀 **Rootless Execution:** Runs flawlessly on Termux without requiring root access.
- 📦 **Extensive Tool Library:** Offers hundreds of categorized tools via the structured `tools_data_v2.json` database.
- 🔄 **Dynamic Updates:** Automatically fetches the tool database from GitHub to ensure you always have the latest tools.
- 🔌 **Plugin Support:** Expand the menu's functionality by adding your own custom Python scripts to the `plugins/` directory.
- 🎨 **Customizable Themes:** Personalize your terminal experience with built-in themes including Green, Blue, Purple, Red, and Monochrome.
- ⭐ **Favorites & Stats:** Add your most-used tools to favorites for quick access and track your usage statistics.
- 📊 **System Info:** View real-time device information including IP address, storage space, and battery status.
- ⚡ **Fast & Optimized:** Quick installation and smooth performance thanks to the hybrid Shell and Python architecture.

---

## 🖼️ Screenshots

*(Add your project screenshots here)*
<!-- ![Lotus Main Menu](screenshots/main_menu.png) -->
<!-- ![Lotus Tool Install](screenshots/tool_install.png) -->

---

## 🛠️ Installation

To install Lotus on your Termux device, follow these steps:

```bash
# Update repositories and install required packages
pkg update && pkg upgrade -y
pkg install git python -y

# Clone the Lotus repository
git clone https://github.com/WeAreMS/Lotus.git

# Navigate into the directory
cd Lotus

# Give execution permission to the install script and run it
chmod +x install.sh
bash install.sh
```

---

## 🚀 Usage

Once the installation is complete, launch Lotus by running:

```bash
python lotus.py
And you can run it by typing lotus as a shortcut.
```

**Basic Commands:**
- `update` : Manually updates the tool database (JSON).
- `theme`  : Allows you to change the interface theme.
- `stats`  : Displays usage statistics and system information.
- `exit`   : Safely exits the application.

---

## 🔌 Plugin System

Lotus features a modular architecture that allows you to integrate your own tools or scripts seamlessly.

1. Navigate to the `plugins/` directory.
2. Create a new Python file (e.g., `my_custom_tool.py`).
3. Ensure your script provides a standard output format.
4. Restart Lotus, and your plugin will automatically appear in the menu.

---

## 🎨 Themes

Lotus comes with 5 built-in themes to customize your terminal experience:
- 🟢 **Green** (Default Hacker Theme)
- 🔵 **Blue** (Ocean Theme)
- 🟣 **Purple** (Night Purple)
- 🔴 **Red** (Danger / Red)
- ⚪ **Monochrome** (Clean Black & White)

You can change themes directly from the main menu under `Theme Settings` or by editing the configuration file inside `lotus.py`.

---

## 🤝 Contributing

Contributions are highly welcome! If you want to add a new tool, fix a bug, or develop a new feature:

1. Fork the repository (`Fork`)
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request.

*(Please ensure you maintain the existing JSON format when adding new tools to `tools_data_v2.json`.)*

---

## 📜 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <sub>Built with ❤️ by <a href="https://github.com/WeAreMS">WeAreMS</a></sub>
  <br>
  <i>Lotus - The ultimate tool management experience for Termux.</i>
</div>
