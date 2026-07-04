#!/usr/bin/env python3
"""
Lotus - Termux Rootless Advanced Tool Menu
Version: 5.0
Developed by: Nyrox
"""

import os
import sys
import json
import time
import shutil
import subprocess
import threading
import itertools
from pathlib import Path
from datetime import datetime

VERSION = "5.0"

# ---------------------------------------------------------------------------
# File paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
TOOLS_FILE = BASE_DIR / 'tools_data_v2.json'
FAVORITES_FILE = BASE_DIR / '.lotus_favorites.json'
LOG_FILE = BASE_DIR / '.lotus_log.txt'
STATS_FILE = BASE_DIR / '.lotus_stats.json'
CONFIG_FILE = BASE_DIR / '.lotus_config.json'
TOOLS_DIR = BASE_DIR / 'installed'
PLUGINS_DIR = BASE_DIR / 'plugins'

# ---------------------------------------------------------------------------
# Themes
# ---------------------------------------------------------------------------
THEMES = {
    "green": {
        "primary": '\033[92m', "accent": '\033[96m', "warn": '\033[93m',
        "danger": '\033[91m', "muted": '\033[97m', "special": '\033[95m',
        "label": "Green (Default)"
    },
    "blue": {
        "primary": '\033[94m', "accent": '\033[96m', "warn": '\033[93m',
        "danger": '\033[91m', "muted": '\033[97m', "special": '\033[95m',
        "label": "Blue"
    },
    "purple": {
        "primary": '\033[95m', "accent": '\033[96m', "warn": '\033[93m',
        "danger": '\033[91m', "muted": '\033[97m', "special": '\033[92m',
        "label": "Purple"
    },
    "red": {
        "primary": '\033[91m', "accent": '\033[93m', "warn": '\033[93m',
        "danger": '\033[95m', "muted": '\033[97m', "special": '\033[96m',
        "label": "Red"
    },
    "mono": {
        "primary": '\033[97m', "accent": '\033[97m', "warn": '\033[97m',
        "danger": '\033[97m', "muted": '\033[90m', "special": '\033[97m',
        "label": "Monochrome"
    },
}
RESET = '\033[0m'
BOLD = '\033[1m'
DIM = '\033[2m'

# Global theme references (assigned with set_theme() after config is loaded)
PRIMARY = ACCENT = WARN = DANGER = MUTED = SPECIAL = ""


def set_theme(name):
    global PRIMARY, ACCENT, WARN, DANGER, MUTED, SPECIAL
    theme = THEMES.get(name, THEMES["green"])
    PRIMARY = theme["primary"]
    ACCENT = theme["accent"]
    WARN = theme["warn"]
    DANGER = theme["danger"]
    MUTED = theme["muted"]
    SPECIAL = theme["special"]


# ---------------------------------------------------------------------------
# Basic Helpers
# ---------------------------------------------------------------------------
def clear_screen():
    # ANSI \033[3J might not clear scrollback in some terminals (especially
    # some Android terminal emulators). The actual 'clear' command provides
    # guaranteed clearing including scrollback on all platforms.
    if os.name == 'nt':
        os.system('cls')
    else:
        sys.stdout.write('\033[H\033[2J\033[3J')
        sys.stdout.flush()
        os.system('clear')


def log(message):
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    except OSError:
        pass


def safe_input(prompt=""):
    try:
        return input(prompt)
    except (KeyboardInterrupt, EOFError):
        raise


def pause(message="Press Enter to continue..."):
    safe_input(f"\n{ACCENT}{message}{RESET}")


def read_menu_choice(prompt="Enter your choice: "):
    return safe_input(f"{BOLD}{MUTED}{prompt}{RESET}").strip()


def is_command_available(name):
    return shutil.which(name) is not None


# ---------------------------------------------------------------------------
# JSON Read/Write
# ---------------------------------------------------------------------------
def load_json_file(path, default):
    if not path.exists():
        return default
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"{DANGER}[!] '{path.name}' could not be read: {e}{RESET}")
        log(f"JSON read error: {path} -> {e}")
        return default


def save_json_file(path, data):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except OSError as e:
        print(f"{DANGER}[!] '{path.name}' could not be saved: {e}{RESET}")
        log(f"JSON write error: {path} -> {e}")
        return False


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DEFAULT_CONFIG = {
    "theme": "green",
    "language": "en",
}

STRINGS = {
    "tr": {
        "banner_sub": "Termux Rootsuz Gelişmiş Araç Menüsü",
        "dev": "Geliştiren: Nyrox",
        "categories": "Kategoriler",
        "general": "Genel",
        "search": "Araç Ara",
        "favorites": "Favoriler",
        "sysinfo": "Sistem Bilgileri",
        "update_all": "Tüm Araçları Güncelle",
        "settings": "Ayarlar",
        "stats": "İstatistikler",
        "exit": "Çıkış",
        "invalid": "Geçersiz seçim. Lütfen tekrar deneyin.",
        "goodbye": "Lotus'tan çıkılıyor... Hoşça kalın!",
    },
    "en": {
        "banner_sub": "Termux Rootless Advanced Tool Menu",
        "dev": "Developed by: Nyrox",
        "categories": "Categories",
        "general": "General",
        "search": "Search Tool",
        "favorites": "Favorites",
        "sysinfo": "System Info",
        "update_all": "Update All Tools",
        "settings": "Settings",
        "stats": "Statistics",
        "exit": "Exit",
        "invalid": "Invalid choice. Please try again.",
        "goodbye": "Exiting Lotus... Goodbye!",
    },
}

CONFIG = {}
T = {}


def load_config():
    global CONFIG, T
    data = load_json_file(CONFIG_FILE, default=None)
    CONFIG = {**DEFAULT_CONFIG, **data} if isinstance(data, dict) else dict(DEFAULT_CONFIG)
    if CONFIG.get("theme") not in THEMES:
        CONFIG["theme"] = "green"
    if CONFIG.get("language") not in STRINGS:
        CONFIG["language"] = "en"
    set_theme(CONFIG["theme"])
    T = STRINGS[CONFIG["language"]]


def save_config():
    save_json_file(CONFIG_FILE, CONFIG)


# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------
def display_banner():
    clear_screen()
    print(rf"""
{BOLD}{PRIMARY}
  _      ____  _______ _    _  _____
 | |    / __ \|__   __| |  | |/ ____|
 | |   | |  | |  | |  | |  | | (___
 | |   | |  | |  | |  | |  | |\___ \
 | |___| |__| |  | |  | |__| |____) |
 |______\____/   |_|   \____/|_____/

    {WARN}{T['banner_sub']}{RESET}
    {ACCENT}Version: {VERSION}{RESET}
    {PRIMARY}{T['dev']}{RESET}
    """)


# ---------------------------------------------------------------------------
# Command Execution + Spinner (simple async feel)
# ---------------------------------------------------------------------------
def _spin(stop_event, message):
    frames = itertools.cycle("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏")
    while not stop_event.is_set():
        sys.stdout.write(f"\r{ACCENT}{next(frames)} {message}{RESET}   ")
        sys.stdout.flush()
        time.sleep(0.08)
    sys.stdout.write("\r" + " " * (len(message) + 10) + "\r")
    sys.stdout.flush()


def run_command(cmd, cwd=None, spinner_msg=None):
    """Executes the command; if spinner_msg is given, shows a spinner in a separate thread
    (the command itself still runs synchronously with subprocess.run, but the UI doesn't look frozen)."""
    log(f"CMD: {cmd} (cwd={cwd})")
    stop_event = threading.Event()
    spinner_thread = None
    if spinner_msg:
        spinner_thread = threading.Thread(target=_spin, args=(stop_event, spinner_msg), daemon=True)
        spinner_thread.start()
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd)
        return result.returncode == 0
    except Exception as e:
        log(f"ERROR: {cmd} -> {e}")
        print(f"{DANGER}[!] Error occurred while running command: {e}{RESET}")
        return False
    finally:
        if spinner_thread:
            stop_event.set()
            spinner_thread.join()


# ---------------------------------------------------------------------------
# Schema Tolerant Data Loading
# ---------------------------------------------------------------------------
def normalize_tool(raw):
    """Reduces different possible key names to a single standard schema.
    Thus, slightly different formats other than tools_data_v2.json also work."""
    if not isinstance(raw, dict):
        return None

    name = raw.get('name') or raw.get('title') or raw.get('tool')
    if not name:
        return None

    repo = raw.get('repo') or raw.get('url') or raw.get('git') or None

    install = raw.get('install') or raw.get('install_cmds') or raw.get('setup') or []
    if isinstance(install, str):
        install = [install]
    if not isinstance(install, list):
        install = []
    install = [str(c) for c in install if isinstance(c, (str, int, float))]

    run_cmd = raw.get('run') or raw.get('run_cmd') or raw.get('exec') or raw.get('command')
    if isinstance(run_cmd, list):
        run_cmd = " && ".join(str(c) for c in run_cmd)

    desc = raw.get('description') or raw.get('desc') or ""

    return {
        "name": str(name),
        "repo": str(repo) if repo else None,
        "install": install,
        "run": str(run_cmd) if run_cmd else None,
        "description": str(desc),
    }


def load_tools():
    data = load_json_file(TOOLS_FILE, default=None)
    if data is None:
        print(f"{DANGER}[!] Data file not found or corrupted: {TOOLS_FILE.name}{RESET}")
        print(f"{WARN}[*] Please make sure '{TOOLS_FILE.name}' file is in the Lotus directory.{RESET}")
        sys.exit(1)

    cleaned = {}
    skipped = 0

    def process_list(category, tools):
        nonlocal skipped
        valid = []
        for item in tools:
            norm = normalize_tool(item)
            if norm:
                valid.append(norm)
            else:
                skipped += 1
        if valid:
            cleaned[category] = valid

    if isinstance(data, dict):
        # Expected format: {"Category": [ {...}, {...} ]}
        for category, tools in data.items():
            if isinstance(tools, list):
                process_list(category, tools)
            elif isinstance(tools, dict):
                # Alternative format: {"Category": {"tools": [...]}}
                inner = tools.get('tools') if isinstance(tools.get('tools'), list) else None
                if inner is not None:
                    process_list(category, inner)
                else:
                    skipped += 1
            else:
                skipped += 1
    elif isinstance(data, list):
        # Alternative format: flat list, category info might be inside the tool
        by_cat = {}
        for item in data:
            norm = normalize_tool(item)
            if norm:
                cat = item.get('category', 'General') if isinstance(item, dict) else 'General'
                by_cat.setdefault(cat, []).append(norm)
            else:
                skipped += 1
        cleaned = by_cat
    else:
        print(f"{DANGER}[!] Data file format not recognized.{RESET}")
        sys.exit(1)

    if skipped:
        print(f"{WARN}[*] {skipped} invalid/skipped tool records.{RESET}")
        log(f"{skipped} invalid tool records skipped.")

    if not cleaned:
        print(f"{DANGER}[!] No usable tools found.{RESET}")
        sys.exit(1)

    return cleaned


# ---------------------------------------------------------------------------
# Tool Status / Installation / Running
# ---------------------------------------------------------------------------
def get_repo_dir(tool):
    repo = tool.get('repo')
    if not repo:
        return None
    name = repo.rstrip('/').split('/')[-1].replace('.git', '')
    return TOOLS_DIR / name


def is_tool_installed(tool):
    repo_dir = get_repo_dir(tool)
    if repo_dir is not None:
        return (repo_dir / '.git').exists()
    return is_command_available(tool['name'].lower())


def install_tool(tool):
    print(f"\n{WARN}[*] Starting installation for {tool['name']}...{RESET}")
    log(f"Installation started: {tool['name']}")

    install_cmds = tool.get('install') or []
    has_apt_cmd = any('apt install' in cmd for cmd in install_cmds)

    if not has_apt_cmd:
        run_command('apt update && apt upgrade -y', spinner_msg="Updating system")
        run_command('apt install python git -y', spinner_msg="Installing base packages")

    repo = tool.get('repo')
    repo_dir = get_repo_dir(tool)

    if repo:
        TOOLS_DIR.mkdir(parents=True, exist_ok=True)
        if not repo_dir.exists():
            ok = run_command(f"git clone {repo} {repo_dir}", spinner_msg=f"Cloning {tool['name']}")
            if not ok:
                print(f"{DANGER}[!] Could not clone {tool['name']}. Installation cancelled.{RESET}")
                log(f"Clone error: {tool['name']}")
                pause()
                return False
        else:
            print(f"{WARN}[*] {tool['name']} already cloned, updating...{RESET}")
            run_command("git pull", cwd=str(repo_dir), spinner_msg="Updating")

    success = True
    for cmd in install_cmds:
        cwd = str(repo_dir) if repo_dir else None
        if cmd.startswith('cd '):
            continue
        if not run_command(cmd, cwd=cwd, spinner_msg=f"Running: {cmd[:40]}"):
            success = False
            print(f"{DANGER}[!] Command failed: {cmd}{RESET}")

    if success:
        print(f"{PRIMARY}[+] {tool['name']} installation completed!{RESET}")
        log(f"Installation completed: {tool['name']}")
        record_stat(tool['name'], "install")
    else:
        print(f"{WARN}[!] {tool['name']} installation completed with some errors, check above.{RESET}")
        log(f"Installation partially failed: {tool['name']}")

    time.sleep(1.2)
    return success


def run_tool(tool):
    run_cmd = tool.get('run')
    if not run_cmd:
        print(f"{DANGER}[!] Run command not defined for {tool['name']}.{RESET}")
        pause()
        return

    print(f"\n{WARN}[*] Running {tool['name']}...{RESET}")
    log(f"Running: {tool['name']}")
    repo_dir = get_repo_dir(tool)
    cwd = str(repo_dir) if repo_dir else None

    ok = run_command(run_cmd, cwd=cwd)
    if ok:
        record_stat(tool['name'], "run")
    else:
        print(f"{DANGER}[!] Encountered a problem while running {tool['name']}.{RESET}")
    pause()


def repair_tool(tool):
    print(f"\n{DANGER}[!] Repairing {tool['name']} (reinstalling)...{RESET}")
    log(f"Repair started: {tool['name']}")
    repo_dir = get_repo_dir(tool)
    if repo_dir and repo_dir.exists():
        shutil.rmtree(repo_dir, ignore_errors=True)
    install_tool(tool)


def uninstall_tool(tool):
    repo_dir = get_repo_dir(tool)
    if not repo_dir or not repo_dir.exists():
        print(f"{WARN}[*] {tool['name']} is not installed (or is a command-based tool).{RESET}")
        time.sleep(1.2)
        return
    confirm = read_menu_choice(f"Remove {tool['name']}? (y/N): ").lower()
    if confirm == 'y':
        shutil.rmtree(repo_dir, ignore_errors=True)
        print(f"{PRIMARY}[+] {tool['name']} removed.{RESET}")
        log(f"Removed: {tool['name']}")
    time.sleep(1)


def ensure_installed_then_run(tool):
    if not is_tool_installed(tool):
        if not install_tool(tool):
            return
    run_tool(tool)


# ---------------------------------------------------------------------------
# Statistics / Usage History
# ---------------------------------------------------------------------------
def load_stats():
    data = load_json_file(STATS_FILE, default={})
    return data if isinstance(data, dict) else {}


def record_stat(tool_name, action):
    """action: 'run' or 'install'."""
    stats = load_stats()
    entry = stats.setdefault(tool_name, {"run_count": 0, "install_count": 0, "last_used": None})
    if action == "run":
        entry["run_count"] += 1
        entry["last_used"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    elif action == "install":
        entry["install_count"] += 1
    save_json_file(STATS_FILE, stats)


def display_stats():
    display_banner()
    stats = load_stats()
    print(f"\n{BOLD}{MUTED}{T['stats']}:{RESET}")
    print(f"{ACCENT}------------------------------------{RESET}")
    if not stats:
        print(f"{WARN}No tools have been run yet.{RESET}")
    else:
        # Sort by most used
        ordered = sorted(stats.items(), key=lambda kv: kv[1].get('run_count', 0), reverse=True)
        for name, info in ordered[:15]:
            print(f"{PRIMARY}{name}{RESET}: "
                  f"{MUTED}{info.get('run_count', 0)} runs, "
                  f"{info.get('install_count', 0)} installs, "
                  f"last: {info.get('last_used') or '-'}{RESET}")
    print(f"{ACCENT}------------------------------------{RESET}")
    pause()


# ---------------------------------------------------------------------------
# Favorites
# ---------------------------------------------------------------------------
def load_favorites():
    data = load_json_file(FAVORITES_FILE, default=[])
    return set(data) if isinstance(data, list) else set()


def save_favorites(favorites):
    save_json_file(FAVORITES_FILE, sorted(favorites))


def toggle_favorite(tool_name, favorites):
    if tool_name in favorites:
        favorites.discard(tool_name)
        print(f"{WARN}[*] '{tool_name}' removed from favorites.{RESET}")
    else:
        favorites.add(tool_name)
        print(f"{PRIMARY}[+] '{tool_name}' added to favorites.{RESET}")
    save_favorites(favorites)
    time.sleep(1)


# ---------------------------------------------------------------------------
# Plugin System
# ---------------------------------------------------------------------------
def discover_plugins():
    """Loads every .py file in the plugins/ directory as a module.
    Each plugin can optionally define these functions:
      - PLUGIN_NAME (str)
      - register(context) -> dict  # {'1': ('Menu Label', callable), ...}
    context: {'run_command': ..., 'print_color': (PRIMARY, ...), 'tools_data': ...}
    """
    plugins = []
    if not PLUGINS_DIR.exists():
        return plugins

    sys.path.insert(0, str(PLUGINS_DIR))
    for file in sorted(PLUGINS_DIR.glob("*.py")):
        mod_name = file.stem
        try:
            spec = __import__(mod_name)
            name = getattr(spec, "PLUGIN_NAME", mod_name)
            register = getattr(spec, "register", None)
            plugins.append({"name": name, "module": spec, "register": register})
            log(f"Plugin loaded: {name}")
        except Exception as e:
            print(f"{WARN}[*] Plugin '{mod_name}' could not be loaded: {e}{RESET}")
            log(f"Plugin loading error: {mod_name} -> {e}")
    return plugins


def plugins_menu(plugins, tools_data):
    if not plugins:
        display_banner()
        print(f"{WARN}No plugins found. You can add .py files to the '{PLUGINS_DIR.name}/' directory.{RESET}")
        pause()
        return

    while True:
        display_banner()
        print(f"\n{BOLD}{MUTED}Installed Plugins:{RESET}")
        for i, p in enumerate(plugins, 1):
            print(f"{PRIMARY}{i}. {p['name']}{RESET}")
        print(f"{DANGER}99. Go Back{RESET}")
        choice = read_menu_choice()
        if choice == '99':
            return
        if not choice.isdigit() or not (1 <= int(choice) <= len(plugins)):
            print(f"{DANGER}Invalid choice.{RESET}")
            time.sleep(1)
            continue

        plugin = plugins[int(choice) - 1]
        if not plugin["register"]:
            print(f"{WARN}This plugin does not provide a runnable interface.{RESET}")
            time.sleep(1.2)
            continue

        context = {
            "run_command": run_command,
            "colors": {"primary": PRIMARY, "accent": ACCENT, "warn": WARN,
                       "danger": DANGER, "muted": MUTED, "reset": RESET},
            "tools_data": tools_data,
            "log": log,
        }
        try:
            actions = plugin["register"](context) or {}
        except Exception as e:
            print(f"{DANGER}[!] Error while running plugin: {e}{RESET}")
            pause()
            continue

        while True:
            display_banner()
            print(f"\n{BOLD}{MUTED}{plugin['name']}{RESET}\n")
            for key, (label, _) in actions.items():
                print(f"{PRIMARY}{key}. {label}{RESET}")
            print(f"{DANGER}99. Go Back{RESET}")
            sub_choice = read_menu_choice()
            if sub_choice == '99':
                break
            if sub_choice in actions:
                try:
                    actions[sub_choice][1]()
                except Exception as e:
                    print(f"{DANGER}[!] Error: {e}{RESET}")
                pause()
            else:
                print(f"{DANGER}Invalid choice.{RESET}")
                time.sleep(1)


# ---------------------------------------------------------------------------
# Settings Menu
# ---------------------------------------------------------------------------
def settings_menu():
    while True:
        display_banner()
        print(f"\n{BOLD}{MUTED}{T['settings']}:{RESET}")
        print(f"{PRIMARY}1. Change Theme (current: {THEMES[CONFIG['theme']]['label']}){RESET}")
        lang_label = "Turkish" if CONFIG['language'] == 'tr' else "English"
        print(f"{PRIMARY}2. Change Language (current: {lang_label}){RESET}")
        print(f"{PRIMARY}3. Clear Logs{RESET}")
        print(f"{PRIMARY}4. Reset Statistics{RESET}")
        print(f"{DANGER}99. Go Back{RESET}")

        choice = read_menu_choice()
        if choice == '99':
            return
        elif choice == '1':
            choose_theme()
        elif choice == '2':
            CONFIG['language'] = 'en' if CONFIG['language'] == 'tr' else 'tr'
            save_config()
            load_config()  # Refresh T dictionary
        elif choice == '3':
            LOG_FILE.write_text("", encoding='utf-8') if LOG_FILE.exists() else None
            print(f"{PRIMARY}[+] Logs cleared.{RESET}")
            time.sleep(1)
        elif choice == '4':
            save_json_file(STATS_FILE, {})
            print(f"{PRIMARY}[+] Statistics reset.{RESET}")
            time.sleep(1)
        else:
            print(f"{DANGER}Invalid choice.{RESET}")
            time.sleep(1)


def choose_theme():
    display_banner()
    print(f"\n{BOLD}{MUTED}Select Theme:{RESET}")
    keys = list(THEMES.keys())
    for i, key in enumerate(keys, 1):
        marker = " (active)" if key == CONFIG['theme'] else ""
        print(f"{THEMES[key]['primary']}{i}. {THEMES[key]['label']}{marker}{RESET}")
    print(f"{DANGER}99. Go Back{RESET}")

    choice = read_menu_choice()
    if choice == '99':
        return
    if choice.isdigit() and 1 <= int(choice) <= len(keys):
        CONFIG['theme'] = keys[int(choice) - 1]
        save_config()
        set_theme(CONFIG['theme'])
        print(f"{PRIMARY}[+] Theme updated.{RESET}")
        time.sleep(1)
    else:
        print(f"{DANGER}Invalid choice.{RESET}")
        time.sleep(1)


# ---------------------------------------------------------------------------
# Tool Menus
# ---------------------------------------------------------------------------
def status_tag(tool):
    return f"{PRIMARY}[Installed]{RESET}" if is_tool_installed(tool) else f"{WARN}[Not Installed]{RESET}"


def tool_action_menu(tool, favorites):
    while True:
        display_banner()
        print(f"{BOLD}{MUTED}{tool['name']}{RESET}  {status_tag(tool)}")
        if tool.get('description'):
            print(f"{DIM}{tool['description']}{RESET}")
        if tool.get('repo'):
            print(f"{ACCENT}Repo: {MUTED}{tool['repo']}{RESET}")
        fav_mark = "★" if tool['name'] in favorites else "☆"
        print(f"{SPECIAL}Favorite: {fav_mark}{RESET}\n")

        print(f"{PRIMARY}1. Run{RESET}")
        print(f"{PRIMARY}2. Install / Update{RESET}")
        print(f"{PRIMARY}3. Repair (reinstall){RESET}")
        print(f"{PRIMARY}4. Add/Remove Favorite{RESET}")
        print(f"{DANGER}5. Uninstall{RESET}")
        print(f"{DANGER}99. Go Back{RESET}")

        choice = read_menu_choice()
        if choice == '99':
            return
        elif choice == '1':
            ensure_installed_then_run(tool)
        elif choice == '2':
            install_tool(tool)
        elif choice == '3':
            repair_tool(tool)
        elif choice == '4':
            toggle_favorite(tool['name'], favorites)
        elif choice == '5':
            uninstall_tool(tool)
        else:
            print(f"{DANGER}Invalid choice.{RESET}")
            time.sleep(1)


def list_tools_menu(title, tools, favorites):
    normalized = [item if isinstance(item, tuple) else (None, item) for item in tools]

    while True:
        display_banner()
        print(f"\n{BOLD}{MUTED}{title}:{RESET}")
        if not normalized:
            print(f"{WARN}(List empty){RESET}")
        for i, (category, tool) in enumerate(normalized, 1):
            suffix = f" {ACCENT}({category}){RESET}" if category else ""
            fav_mark = f"{SPECIAL}★{RESET} " if tool['name'] in favorites else ""
            print(f"{PRIMARY}{i}. {fav_mark}{tool['name']}{RESET} {status_tag(tool)}{suffix}")
        print(f"{DANGER}99. Go Back{RESET}")

        choice = read_menu_choice()
        if choice == '99':
            return
        if not choice.isdigit():
            print(f"{DANGER}Please enter a number.{RESET}")
            time.sleep(1)
            continue

        idx = int(choice) - 1
        if 0 <= idx < len(normalized):
            _, tool = normalized[idx]
            tool_action_menu(tool, favorites)
        else:
            print(f"{DANGER}Invalid choice.{RESET}")
            time.sleep(1)


def search_tools(tools_data, favorites):
    while True:
        display_banner()
        term = read_menu_choice("Enter tool name to search (99 to exit): ").lower()
        if term == '99':
            return
        if not term:
            continue

        found = [
            (category, tool)
            for category, tools in tools_data.items()
            for tool in tools
            if term in tool['name'].lower() or term in tool.get('description', '').lower()
        ]

        if found:
            list_tools_menu(f"Results for '{term}'", found, favorites)
        else:
            print(f"{WARN}No tools found.{RESET}")
            time.sleep(1.5)


def favorites_menu(tools_data, favorites):
    fav_tools = [
        (category, tool)
        for category, tools in tools_data.items()
        for tool in tools
        if tool['name'] in favorites
    ]
    if not fav_tools:
        display_banner()
        print(f"{WARN}You haven't added any favorites yet.{RESET}")
        pause()
        return
    list_tools_menu("Favorite Tools", fav_tools, favorites)


def display_system_info():
    display_banner()
    print(f"\n{BOLD}{MUTED}System Info:{RESET}")
    print(f"{ACCENT}------------------------------------{RESET}")

    ip_address = ""
    out = subprocess.run(
        "ifconfig 2>/dev/null | grep -A1 'wlan0\\|eth0' | grep 'inet '",
        shell=True, capture_output=True, text=True
    ).stdout
    if out:
        parts = out.split()
        if len(parts) >= 2:
            ip_address = parts[1]
    print(f"{PRIMARY}IP Address: {MUTED}{ip_address or 'Not Found'}{RESET}")

    storage = subprocess.run(
        "df -h /data 2>/dev/null | tail -1 | awk '{print $2, $3, $4}'",
        shell=True, capture_output=True, text=True
    ).stdout.strip()
    print(f"{PRIMARY}Storage (Total/Used/Free): {MUTED}{storage or 'Not Found'}{RESET}")

    battery = ""
    if is_command_available('termux-battery-status'):
        out = subprocess.run(
            "termux-battery-status 2>/dev/null | grep percentage",
            shell=True, capture_output=True, text=True
        ).stdout
        battery = ''.join(ch for ch in out if ch.isdigit())

    print(f"{PRIMARY}Battery: {MUTED}"
          f"{(battery + '%') if battery else 'Information inaccessible (Termux:API might not be installed)'}{RESET}")

    installed_count = sum(
        1 for tools in TOOLS_DATA_CACHE.values() for t in tools if is_tool_installed(t)
    ) if TOOLS_DATA_CACHE else 0
    total_count = sum(len(tools) for tools in TOOLS_DATA_CACHE.values()) if TOOLS_DATA_CACHE else 0
    print(f"{PRIMARY}Tools: {MUTED}{installed_count}/{total_count} installed{RESET}")

    print(f"{ACCENT}------------------------------------{RESET}")
    pause()


def update_all_tools(tools_data):
    display_banner()
    print(f"\n{WARN}[*] Updating all installed tools...{RESET}")
    updated = 0
    for category, tools in tools_data.items():
        for tool in tools:
            repo_dir = get_repo_dir(tool)
            if repo_dir and repo_dir.exists():
                print(f"{ACCENT}[*] Updating {tool['name']}...{RESET}")
                if run_command("git pull", cwd=str(repo_dir), spinner_msg=f"{tool['name']}"):
                    updated += 1
    print(f"{PRIMARY}[+] Update completed. {updated} tools updated.{RESET}")
    pause()


def display_main_menu(categories, favorites_count, plugin_count):
    display_banner()
    print(f"\n{BOLD}{MUTED}{T['categories']}:{RESET}")
    for i, cat_name in enumerate(categories, 1):
        print(f"{PRIMARY}{i}. {cat_name}{RESET}")
    print(f"\n{BOLD}{MUTED}{T['general']}:{RESET}")
    print(f"{PRIMARY}S. {T['search']}{RESET}")
    print(f"{PRIMARY}F. {T['favorites']} ({favorites_count}){RESET}")
    print(f"{PRIMARY}I. {T['sysinfo']}{RESET}")
    print(f"{PRIMARY}U. {T['update_all']}{RESET}")
    print(f"{PRIMARY}T. {T['stats']}{RESET}")
    if plugin_count:
        print(f"{PRIMARY}P. Plugins ({plugin_count}){RESET}")
    print(f"{PRIMARY}A. {T['settings']}{RESET}")
    print(f"{DANGER}0. {T['exit']}{RESET}")
    print(f"\n{BOLD}{WARN}------------------------------------{RESET}")


# ---------------------------------------------------------------------------
# Main Loop
# ---------------------------------------------------------------------------
TOOLS_DATA_CACHE = None


def main():
    global TOOLS_DATA_CACHE
    load_config()
    tools_data = load_tools()
    TOOLS_DATA_CACHE = tools_data
    categories = list(tools_data.keys())
    favorites = load_favorites()
    plugins = discover_plugins()

    while True:
        display_main_menu(categories, len(favorites), len(plugins))
        choice = read_menu_choice().upper()

        if choice == '0':
            clear_screen()
            print(f"{BOLD}{DANGER}{T['goodbye']}{RESET}")
            return
        elif choice == 'S':
            search_tools(tools_data, favorites)
        elif choice == 'F':
            favorites_menu(tools_data, favorites)
        elif choice == 'I':
            display_system_info()
        elif choice == 'U':
            update_all_tools(tools_data)
        elif choice == 'T':
            display_stats()
        elif choice == 'P' and plugins:
            plugins_menu(plugins, tools_data)
        elif choice == 'A':
            settings_menu()
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(categories):
                cat_name = categories[idx]
                cat_tools = [(cat_name, t) for t in tools_data[cat_name]]
                list_tools_menu(cat_name, cat_tools, favorites)
            else:
                print(f"{DANGER}{T['invalid']}{RESET}")
                time.sleep(1.5)
        else:
            print(f"{DANGER}{T['invalid']}{RESET}")
            time.sleep(1.5)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        clear_screen()
        print(f"\n{BOLD}\033[91m[!] Process cancelled. Exiting Lotus... Goodbye!{RESET}")
        sys.exit(0)
    except Exception as e:
        clear_screen()
        print(f"{BOLD}\033[91m[!] An unexpected error occurred: {e}{RESET}")
        log(f"Unexpected error: {e}")
        sys.exit(1)
