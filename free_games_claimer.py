import requests
import webbrowser
import os
import sys
import shutil
import re
import subprocess
import time
import tkinter as tk
from tkinter import filedialog
from datetime import datetime, timezone
from bs4 import BeautifulSoup

# --- CONFIGURATION & FILE MANAGEMENT ---

# Define the location for the user's Documents folder
DOCS_PATH = os.path.join(os.path.expanduser('~'), 'Documents')

# Define a dedicated folder for all script files
CLAIMER_DIR = os.path.join(DOCS_PATH, 'Free Games Claimer')
os.makedirs(CLAIMER_DIR, exist_ok=True)  # Ensure the directory exists

# Define the location for the configuration and log files
CLAIMED_FILE = os.path.join(CLAIMER_DIR, "claimed_games.txt")
CONFIG_FILE_PATH = os.path.join(CLAIMER_DIR, 'claimer_config.txt')
LOG_FILE_PATH = os.path.join(CLAIMER_DIR, 'claimer_log.txt')

# --- BROWSER CONFIGURATION ---

CURRENT_OS = sys.platform
BROWSERS = {
    1: ("Chrome", {
        'win32': "C:/Program Files/Google/Chrome/Application/chrome.exe",
        'darwin': "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        'linux': "/usr/bin/google-chrome"
    }, "chrome"),
    2: ("Firefox", {
        'win32': "C:/Program Files/Mozilla Firefox/firefox.exe",
        'darwin': "/Applications/Mozilla Firefox.app/Contents/MacOS/firefox",
        'linux': "/usr/bin/firefox"
    }, "firefox"),
    3: ("Brave", {
        'win32': "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe",
        'darwin': "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        'linux': "/usr/bin/brave-browser"
    }, "chrome")
}

# Default configuration settings
DEFAULT_CONFIG = {
    'logging_enabled': False,
    'backup_path': None,
    'browser_id': None
}

# --- STORE API / URLS ---

EPIC_API = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=US&allowCountries=US"
STEAM_URL = "https://store.steampowered.com/search/?maxprice=free&specials=1"
GOG_URL = "https://www.gog.com/en"
UBISOFT_URL = "https://store.ubisoft.com/us/free-games"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# --- CONFIG & LOGGING FUNCTIONS ---

def load_config():
    """Loads the stored configuration from the config file."""
    config = DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE_PATH, 'r') as f:
            lines = [line.strip() for line in f.readlines()]
            if len(lines) > 0:
                config['logging_enabled'] = lines[0].lower() == 'true'
            if len(lines) > 1:
                config['backup_path'] = lines[1].strip()
            if len(lines) > 2 and lines[2].isdigit():
                config['browser_id'] = int(lines[2])

        if config['logging_enabled']:
            print("✨ Found saved preference: Logging is enabled.")

    except FileNotFoundError:
        print("Config file not found. Using default settings.")
    except Exception as e:
        print(f"Error loading config file. Using defaults. Error: {e}")
    return config


def save_config(config_data):
    """Saves the current configuration to the config file."""
    try:
        with open(CONFIG_FILE_PATH, 'w') as f:
            f.write(f"{config_data['logging_enabled']}\n")
            backup_path = config_data.get('backup_path', '')
            f.write(f"{backup_path}\n")
            browser_id = config_data.get('browser_id') if config_data.get('browser_id') else ''
            f.write(f"{browser_id}\n")
        print("✅ Configuration saved!")
    except Exception as e:
        print(f"Warning: Could not save configuration to {CONFIG_FILE_PATH}. Error: {e}")


def log_claim(title, url):
    """Appends the claimed game and URL to the log file."""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] CLAIMED: {title:<50} | URL: {url}\n"
        with open(LOG_FILE_PATH, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Warning: Failed to write to log file. Error: {e}")


def view_log():
    """Reads and displays the claim log file content."""
    try:
        with open(LOG_FILE_PATH, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.strip():
            print("\n😏 The claim log file is empty. No recent claims logged.")
            return

        print("\n--- Game Claim Log 📄 ---")
        print(content)
        print("----------------------------")
        input("\nPress Enter to return...")

    except FileNotFoundError:
        print("\n😏 The log file hasn't been created yet. You need to enable logging (L) and run a claim first!")
        input("\nPress Enter to return...")
    except Exception as e:
        print(f"Error reading log file: {e}")


def clear_log():
    """Prompts the user for confirmation and deletes the log file."""
    try:
        if not os.path.exists(LOG_FILE_PATH):
            print("\n😏 The log file hasn't been created yet. Nothing to delete!")
            input("\nPress Enter to return...")
            return

        while True:
            # Case-insensitive Confirm
            action = input("\n🚨 ARE YOU SURE you want to delete the claim log forever? (Y/N): ").strip().upper()
            if action == 'Y':
                os.remove(LOG_FILE_PATH)
                print("🔥 Claim log file deleted!")
                break
            elif action == 'N':
                print("📝 Log kept safe.")
                break
            else:
                print("Invalid input. Please type Y or N.")
        input("\nPress Enter to return...")

    except Exception as e:
        print(f"Error deleting log file: {e}")

# --- BROWSER UTILITIES ---

def select_browser_menu(current_config):
    """Displays browser selection menu."""
    while True:
        print("\n--- 🌐 Select Default Browser ---")
        for key, (name, _, _) in BROWSERS.items():
            print(f"{key}. {name}")
        print("0. Use System Default")

        choice = input("Choice: ").strip()

        if choice == '0':
            return None
        if choice.isdigit() and int(choice) in BROWSERS:
            return int(choice)
        print("Invalid selection.")


def get_browser_controller(config):
    """Returns a webbrowser controller based on config."""
    browser_id = config.get('browser_id')

    if not browser_id or browser_id not in BROWSERS:
        return webbrowser.get()

    browser_name, browser_paths, _ = BROWSERS[browser_id]
    browser_path = browser_paths.get(CURRENT_OS)

    if not browser_path or not os.path.exists(browser_path):
        print(f"⚠️ Warning: Configured browser path not found: {browser_path}")
        print("⚠️ Falling back to system default.")
        return webbrowser.get()

    try:
        webbrowser.register('custom_browser', None, webbrowser.BackgroundBrowser(browser_path))
        return webbrowser.get('custom_browser')
    except Exception as e:
        print(f"Error registering browser: {e}")
        return webbrowser.get()

# --- BACKUP & RESTORE FUNCTIONS ---

def get_directory_dialog():
    """Opens a file explorer dialog to select a folder."""
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    folder_selected = filedialog.askdirectory(title="Select Backup Destination Folder")
    root.destroy()
    return folder_selected


def get_file_dialog():
    """Opens a file explorer dialog to select a ZIP file."""
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    file_selected = filedialog.askopenfilename(
        title="Select Backup ZIP to Restore",
        filetypes=[("Zip files", "*.zip")]
    )
    root.destroy()
    return file_selected


def get_last_backup_date(config):
    """Finds the most recent backup file and returns its formatted date string."""
    backup_path = config.get('backup_path')
    if not backup_path or not os.path.exists(backup_path):
        return "Never"

    full_backup_dir = os.path.join(backup_path, "Free Games Claimer Backups")
    if not os.path.exists(full_backup_dir):
        return "Never"

    try:
        files = [f for f in os.listdir(full_backup_dir) if f.startswith("FreeGamesClaimer_Backup_") and f.endswith(".zip")]
        if not files:
            return "Never"

        files.sort(reverse=True)
        latest_file = files[0]

        ts_str = latest_file.replace("FreeGamesClaimer_Backup_", "").replace(".zip", "")
        dt = datetime.strptime(ts_str, "%Y%m%d_%H%M%S")
        return dt.strftime("%Y-%m-%d %H:%M")

    except Exception:
        return "Unknown"


def perform_backup(config):
    """Backs up the entire Free Games Claimer directory."""
    current_path = config.get('backup_path')

    if not current_path or not os.path.exists(current_path):
        print("\n📂 Please select a folder to store your backups...")
        current_path = get_directory_dialog()
        if not current_path:
            print("❌ Backup cancelled. No folder selected.")
            return
        config['backup_path'] = current_path
        save_config(config)

    try:
        backup_folder_name = "Free Games Claimer Backups"
        full_backup_dir = os.path.join(current_path, backup_folder_name)

        if not os.path.exists(full_backup_dir):
            os.makedirs(full_backup_dir)

        source_dir_name = os.path.basename(CLAIMER_DIR)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename_base = f"FreeGamesClaimer_Backup_{timestamp}"

        output_base_path = os.path.join(full_backup_dir, backup_filename_base)

        archive_path = shutil.make_archive(
            base_name=output_base_path,
            format='zip',
            root_dir=DOCS_PATH,
            base_dir=source_dir_name
        )

        print("-" * 50)
        print("🎉 **BACKUP SUCCESSFUL** 🎉")
        print(f"File: **{os.path.basename(archive_path)}**")
        print(f"Saved to: **{full_backup_dir}**")
        print("-" * 50)
        input("\nPress Enter to continue...")

    except Exception as e:
        print(f"\n🚨 An error occurred during backup: {e}")
        input("\nPress Enter to continue...")


def perform_restore():
    """Restores a backup zip."""
    print("\n⚠️  WARNING: Restore will OVERWRITE current logs and claimed game lists.")
    confirm = input("Are you sure you want to proceed? (Y/N): ").strip().upper()
    if confirm != 'Y':
        print("Restore cancelled.")
        return

    print("📂 Select the ZIP file to restore...")
    zip_file = get_file_dialog()

    if not zip_file:
        print("❌ Restore cancelled. No file selected.")
        return

    try:
        shutil.unpack_archive(zip_file, DOCS_PATH)
        print("-" * 50)
        print("♻️  **RESTORE SUCCESSFUL** ♻️")
        print(f"Restored content from: {os.path.basename(zip_file)}")
        print(f"To folder: {CLAIMER_DIR}")
        print("-" * 50)
        input("\nPress Enter to continue...")

    except Exception as e:
        print(f"\n🚨 An error occurred during restore: {e}")
        input("\nPress Enter to continue...")


def backup_restore_menu(config):
    """Sub-menu for Backup/Restore operations."""
    while True:
        saved_path = config.get('backup_path', 'Not Set')
        last_backup_str = get_last_backup_date(config)

        print("\n--- 💾 Backup & Restore Menu ---")
        print(f"Current Backup Path: {saved_path}")
        print(f"Last Backup: {last_backup_str}")
        print("\n1. Create New Backup 📥")
        print("2. Restore From Backup 📤")
        print("3. Change Backup Location 📂")
        print("0. Back to Settings")

        choice = input("\nSelect option: ").strip().upper()

        if choice == '1':
            perform_backup(config)
            return
        elif choice == '2':
            perform_restore()
            return
        elif choice == '3':
            print("\n📂 Select new default backup folder...")
            new_path = get_directory_dialog()
            if new_path:
                config['backup_path'] = new_path
                save_config(config)
                print(f"✅ Backup path updated to: {new_path}")
            else:
                print("Cancelled.")
        elif choice == '0':
            return
        else:
            print("Invalid input.")

# --- GAME DATA UTILITIES ---

def load_claimed_games():
    """Loads previously claimed games."""
    print("📂 Loading previously claimed games...")
    if os.path.exists(CLAIMED_FILE):
        with open(CLAIMED_FILE, "r", encoding="utf-8") as f:
            return set(line.strip().lower() for line in f if line.strip())
    return set()


def save_claimed_games(titles):
    """Saves new games to file."""
    print(f"💾 Saving {len(titles)} newly claimed games to file...")
    os.makedirs(CLAIMER_DIR, exist_ok=True)
    with open(CLAIMED_FILE, "a", encoding="utf-8") as f:
        for title in titles:
            f.write(title + "\n")


def view_claimed_games():
    """Displays claimed games with an internal loop for changing sort order."""

    if not os.path.exists(CLAIMED_FILE):
        print("\n😏 No games claimed yet (file not found).")
        input("\nPress Enter to return...")
        return

    try:
        with open(CLAIMED_FILE, "r", encoding="utf-8") as f:
            raw_lines = [line.strip() for line in f.readlines() if line.strip()]

        if not raw_lines:
            print("\n😏 The claimed list is empty.")
            input("\nPress Enter to return...")
            return

        # Prepare unique list (preserving file order = oldest first)
        seen = set()
        clean_list = []
        for game in raw_lines:
            if '|' in game:
                game = game.split('|')[0].strip()
            if game.lower() not in seen:
                seen.add(game.lower())
                clean_list.append(game)

        # Internal Menu Loop
        current_sort = '1'  # Default A-Z

        while True:
            # 1. Create a display copy based on current sort
            display_list = list(clean_list)
            sort_name = "Alphabetical (A-Z)"

            if current_sort == '2':
                display_list.reverse()  # Newest first
                sort_name = "Recently Claimed (Newest First)"
            elif current_sort == '3':
                # Already oldest first from file
                sort_name = "Chronological (Oldest First)"
            else:
                display_list.sort(key=str.lower)  # A-Z
                sort_name = "Alphabetical (A-Z)"

            # 2. Print Header and List
            print("\n" * 2)
            print("=" * 60)
            print("📚 CLAIMED GAMES LIBRARY")
            print(f"CURRENT VIEW: {sort_name}")
            print("=" * 60)

            for idx, game in enumerate(display_list, 1):
                print(f"{idx}. {game}")

            print("-" * 60)

            # 3. Prompt for switch (MOVED HERE AS REQUESTED)
            print("VIEWS: [1] A-Z  [2] Newest First  [3] Oldest First  [0] Back")
            choice = input("Select View > ").strip()

            if choice == '0':
                break
            elif choice in ['1', '2', '3']:
                current_sort = choice
            else:
                print("Invalid choice, refreshing default view...")

    except Exception as e:
        print(f"Error reading file: {e}")

# --- GAME CHECKER FUNCTIONS ---

def parse_epic_date(date_str):
    """Parses ISO date string from Epic API and returns a timezone-aware datetime object."""
    try:
        if date_str.endswith('Z'):
            date_str = date_str.rstrip('Z')
        dt = datetime.fromisoformat(date_str)
        return dt.replace(tzinfo=timezone.utc)
    except ValueError:
        if '.' in date_str:
            return datetime.strptime(date_str.split('.')[0], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)


def get_epic_free_games():
    print("🛍️ Checking Epic Games Store (using max resilience API method)...")
    free_games = []
    claimed_titles = load_claimed_games()
    now_utc = datetime.now(timezone.utc)

    try:
        response = requests.get(EPIC_API, headers=headers)
        response.raise_for_status()
        data = response.json()
        elements = data.get('data', {}).get('Catalog', {}).get('searchStore', {}).get('elements', [])

        for game_data in elements:
            title = game_data.get('title', 'Unknown Title')
            is_currently_free = False
            product_slug = None

            # --- PRIORITY FIX: CHECK MAPPINGS FIRST ---
            # Epic often puts a random ID in 'productSlug' but the real name in 'mappings'.
            # We check this first to get the human-readable URL.
            if game_data.get('catalogNs', {}).get('mappings'):
                for mapping in game_data['catalogNs']['mappings']:
                    if mapping.get('pageType') in ['productHome', 'product']:
                        product_slug = mapping.get('pageSlug')
                        break

            # Fallback 1: Use direct 'productSlug' if mappings didn't have it
            if not product_slug and game_data.get("productSlug"):
                product_slug = game_data["productSlug"]

            # Fallback 2: Use 'urlSlug'
            if not product_slug and game_data.get("urlSlug"):
                product_slug = game_data["urlSlug"]

            if not product_slug:
                continue

            price_data = game_data.get('price', {}).get('totalPrice', {})
            if price_data.get('discountPercentage') == 0 and price_data.get('originalPrice') > 0:
                is_currently_free = True

            if not is_currently_free:
                promotions = game_data.get('promotions')
                for offer_type in ['promotionalOffers', 'upcomingPromotionalOffers']:
                    offer_list = promotions.get(offer_type, []) if promotions else []
                    if not offer_list:
                        continue
                    for offer_group in offer_list:
                        for offer in offer_group.get('promotionalOffers', []):
                            discount = offer.get('discountSetting', {}).get('discountPercentage')
                            start_date_str = offer.get('startDate')
                            end_date_str = offer.get('endDate')
                            if discount == 0 and start_date_str and end_date_str:
                                try:
                                    if parse_epic_date(start_date_str) <= now_utc < parse_epic_date(end_date_str):
                                        is_currently_free = True
                                        break
                                except Exception:
                                    continue
                        if is_currently_free:
                            break
                    if is_currently_free:
                        break

            if is_currently_free and product_slug and title.lower() not in claimed_titles:
                slug_base = product_slug
                if slug_base.endswith('/'):
                    slug_base = slug_base[:-1]

                if "/" in slug_base:
                    game_url = f"https://store.epicgames.com/en-US/{slug_base}"
                else:
                    path_type = "p"
                    if game_data.get('offerType', '').upper() == 'BUNDLE':
                        path_type = "bundles"
                    if path_type == "p":
                        for category in game_data.get('categories', []):
                            if 'bundles' in category.get('path', '').lower():
                                path_type = "bundles"
                                break
                    game_url = f"https://store.epicgames.com/en-US/{path_type}/{slug_base}"

                free_games.append((title, game_url))

    except Exception as e:
        print(f"❌ Error checking Epic Games Store: {e}")
    return free_games


def get_steam_free_games():
    print("🔥 Checking Steam Store...")
    games = []
    try:
        response = requests.get(STEAM_URL, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            for game in soup.find_all('a', class_='search_result_row')[:5]:
                price_tag = game.find('div', class_='search_price')
                if price_tag and ('Free' in price_tag.text or '$0.00' in price_tag.text):
                    title = game.find('span', class_='title').text.strip()
                    games.append((title, game['href'].split('?')[0]))
    except Exception as e:
        print(f"❌ Error checking Steam: {e}")
    return games


def get_gog_free_games():
    print("🌙 Checking GOG.com...")
    games = []
    try:
        response = requests.get(GOG_URL, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            section = soup.select_one('.product-tile-container--giveaway')
            if section:
                link, title = section.select_one('a'), section.select_one('.product-tile__title')
                if link and title:
                    games.append((title.text.strip() + " (GOG GIVEAWAY)", "https://www.gog.com" + link['href']))
    except Exception as e:
        print(f"❌ Error checking GOG: {e}")
    return games


def get_ubisoft_free_games():
    print("🎮 Checking Ubisoft Store...")
    games = []
    try:
        response = requests.get(UBISOFT_URL, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            for card in soup.select("div.product-tile"):
                price = card.select_one("div.product-tile__price span")
                if price and 'free' in price.text.lower():
                    title, link = card.select_one("span.product-tile-title"), card.find("a", href=True)
                    if title and link:
                        games.append((title.text.strip(), "https://store.ubisoft.com" + link['href']))
    except Exception as e:
        print(f"❌ Error checking Ubisoft: {e}")
    return games

# --- CORE LOGIC ---

def notify(config):
    """Checks and opens links for unclaimed free games."""
    print("\n🎮 Checking REAL free games only... ✨", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    browser = get_browser_controller(config)
    claimed_titles = load_claimed_games()

    epic_games = get_epic_free_games()
    steam_games = get_steam_free_games()
    gog_games = get_gog_free_games()
    ubisoft_games = get_ubisoft_free_games()

    def filter_claimed(games):
        return [(title, url) for title, url in games if title.lower() not in claimed_titles]

    epic_games = filter_claimed(epic_games)
    steam_games = filter_claimed(steam_games)
    gog_games = filter_claimed(gog_games)
    ubisoft_games = filter_claimed(ubisoft_games)

    def show(name, games):
        if games:
            print(f"\n💫 {name}")
            for title, url in games:
                print(f"- {title}: {url}")
        else:
            print(f"\n😔 No new freebies on {name} right now.")

    show("Epic Games", epic_games)
    show("Steam", steam_games)
    show("GOG.com", gog_games)
    show("Ubisoft", ubisoft_games)

    all_games = epic_games + steam_games + gog_games + ubisoft_games

    if all_games:
        print(f"\n✨ Found {len(all_games)} unclaimed free games! Ready to open? Press ENTER to begin batch magic, or type 'no' to skip.")
        newly_claimed = []
        games_to_open = list(all_games)

        while True:
            choice = input("> ").strip().lower()
            if choice == "no":
                print("💤 Okayy, skipped this time...")
                break

            if not games_to_open:
                print("\nAll games already opened!")
                input("Press ENTER to return to menu.")
                break

            batch = games_to_open[:5]
            games_to_open = games_to_open[5:]

            print(f"🌐 Opening next {len(batch)} games...")
            for title, url in batch:
                print(f"🔗 Opening: {title}")
                try:
                    browser.open_new_tab(url)
                except Exception as e:
                    print(f"Error opening browser: {e}")
                    webbrowser.open(url)

                newly_claimed.append(title.lower())
                if config['logging_enabled']:
                    log_claim(title, url)

            if games_to_open:
                print(f"\n⏭️ {len(games_to_open)} more remaining. Press ENTER for next batch.")
            else:
                print("\n🎉 All done opening! Wasn't that fun?")
                input("Press ENTER to wrap it up.")
                break

        save_claimed_games(newly_claimed)
    else:
        print("\n😢 No new games today... we'll check again soon 💖")
        input("\nPress ENTER to return to menu.")

# --- MENU FUNCTIONS ---

def show_settings_menu(config, last_backup_date):
    log_state = "ON 📝" if config['logging_enabled'] else "OFF 👻"

    b_id = config.get('browser_id')
    if b_id and b_id in BROWSERS:
        browser_name = BROWSERS[b_id][0]
    else:
        browser_name = "System Default"

    print("\n--- ⚙️ Settings Menu ---")
    print(f"T. Browser Selection (Current: {browser_name}) 🌐")
    print(f"L. Toggle Claim Logging (Current Status: {log_state})")
    print("V. View Claim Log 📄")
    print("C. Clear Claim Log 🔥")
    print(f"Z. Backup / Restore Data 💾 (Last: {last_backup_date})")
    print("0. Back to Main Menu 🔙")
    print("-------------------------")


def show_main_menu():
    print("\n--- Free Games Claimer Menu ---")
    print("1. Start Claiming Games 🚀")
    print("2. View Claimed Games Library 📚")
    print("S. Settings & Tools ⚙️")
    print("0. Exit 😢")
    print("-----------------------------")


def settings_loop(config):
    while True:
        last_backup = get_last_backup_date(config)
        show_settings_menu(config, last_backup)
        choice = input("\nType option: ").strip().upper()

        if choice == '0':
            break
        elif choice == 'T':
            new_id = select_browser_menu(config)
            config['browser_id'] = new_id
            save_config(config)
        elif choice == 'L':
            config['logging_enabled'] = not config['logging_enabled']
            save_config(config)
            print("✅ Logging toggled.")
        elif choice == 'V':
            view_log()
        elif choice == 'C':
            clear_log()
        elif choice == 'Z':
            backup_restore_menu(config)
        else:
            print("Invalid option.")

# Main Execution
if __name__ == "__main__":
    config = load_config()

    while True:
        try:
            show_main_menu()
            choice = input("\nType your choice: ").strip().upper()

            if choice == '0':
                print("Okay, exiting...")
                break
            elif choice == '1':
                notify(config)
            elif choice == '2':
                view_claimed_games()
            elif choice == 'S':
                settings_loop(config)
            else:
                print("That’s not on the list. Try again.")

        except ValueError:
            print("Invalid input. Please enter a valid option.")
        except KeyboardInterrupt:
            print("\nOkay, exiting...")
            break
