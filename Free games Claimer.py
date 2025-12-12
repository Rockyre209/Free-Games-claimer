import requests
import webbrowser
import os
import sys
import shutil
from datetime import datetime, timezone
from bs4 import BeautifulSoup

# --- CONFIGURATION & FILE MANAGEMENT ---

# Define the location for the user's Documents folder
DOCS_PATH = os.path.join(os.path.expanduser('~'), 'Documents')

# Define the location for the user's Downloads folder
DOWNLOADS_PATH = os.path.join(os.path.expanduser('~'), 'Downloads')

# Define a dedicated folder for all script files
CLAIMER_DIR = os.path.join(DOCS_PATH, 'Free Games Claimer') 
os.makedirs(CLAIMER_DIR, exist_ok=True) # Ensure the directory exists

# Define the location for the configuration and log files
CLAIMED_FILE = os.path.join(CLAIMER_DIR, "claimed_games.txt")
CONFIG_FILE_PATH = os.path.join(CLAIMER_DIR, 'claimer_config.txt')
LOG_FILE_PATH = os.path.join(CLAIMER_DIR, 'claimer_log.txt')

# Default configuration settings
DEFAULT_CONFIG = {
    'logging_enabled': False
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

        if config['logging_enabled']:
            print("✨ Found saved preference: Logging is enabled.")

    except FileNotFoundError:
        print("Config file not found. Using default settings (Logging OFF).")
    except Exception as e:
        print(f"Error loading config file. Using defaults. Error: {e}")
    return config

def save_config(config_data):
    """Saves the current configuration to the config file."""
    try:
        with open(CONFIG_FILE_PATH, 'w') as f:
            f.write(f"{config_data['logging_enabled']}\n")
        print(f"✅ Configuration saved!")
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

    except FileNotFoundError:
        print(f"\n😏 The log file hasn't been created yet. You need to enable logging (L) and run a claim first!")
    except Exception as e:
        print(f"Error reading log file: {e}")

def clear_log():
    """Prompts the user for confirmation and deletes the log file."""
    try:
        if not os.path.exists(LOG_FILE_PATH):
            print(f"\n😏 The log file hasn't been created yet. Nothing to delete!")
            return

        while True:
            action = input("\n🚨 ARE YOU SURE you want to delete the claim log forever? (Y/N): ").strip().upper()
            if action == 'Y':
                os.remove(LOG_FILE_PATH)
                print(f"🔥 Claim log file deleted!")
                break
            elif action == 'N':
                print("📝 Log kept safe.")
                break
            else:
                print("Invalid input. Please type Y or N.")

    except Exception as e:
        print(f"Error deleting log file: {e}")

def create_backup():
    """Compresses the Free Games Claimer directory into a zip file in the Downloads folder."""
    try:
        source_dir_name = os.path.basename(CLAIMER_DIR)
        
        if not os.path.exists(DOWNLOADS_PATH):
            os.makedirs(DOWNLOADS_PATH)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename_base = f"FreeGamesClaimer_Backup_{timestamp}"
        
        output_base_path = os.path.join(DOWNLOADS_PATH, backup_filename_base)
        
        archive_path = shutil.make_archive(
            base_name=output_base_path,
            format='zip',
            root_dir=DOCS_PATH, 
            base_dir=source_dir_name 
        )

        print("-" * 50)
        print("🎉 **BACKUP SUCCESSFUL** 🎉")
        print(f"File: **{os.path.basename(archive_path)}**")
        print(f"Saved to: **{DOWNLOADS_PATH}**")
        print("-" * 50)

    except FileNotFoundError:
        print("\n🚨 Backup Failed: The source folder 'Free Games Claimer' could not be found in your Documents.")
    except Exception as e:
        print(f"\n🚨 An error occurred during backup: {e}")


# --- GAME DATA UTILITIES ---

def load_claimed_games():
    print("📂 Loading previously claimed games...")
    if os.path.exists(CLAIMED_FILE):
        with open(CLAIMED_FILE, "r", encoding="utf-8") as f:
            return set(line.strip().lower() for line in f if line.strip())
    return set()

def save_claimed_games(titles):
    print(f"💾 Saving {len(titles)} newly claimed games to file...")
    os.makedirs(CLAIMER_DIR, exist_ok=True)
    with open(CLAIMED_FILE, "a", encoding="utf-8") as f:
        for title in titles:
            f.write(title + "\n")

# --- GAME CHECKER FUNCTIONS (Updated Epic) ---

def parse_epic_date(date_str):
    """Parses ISO date string from Epic API and returns a timezone-aware datetime object."""
    try:
        # datetime.fromisoformat handles the 'Z' in Python 3.11+, 
        # but for broader compatibility, we handle it manually.
        if date_str.endswith('Z'):
            date_str = date_str.rstrip('Z')
        
        # Parse, then set the timezone to UTC (since Epic's API dates are in UTC/Z)
        dt = datetime.fromisoformat(date_str)
        return dt.replace(tzinfo=timezone.utc)
    except ValueError:
        # Handle cases with or without milliseconds
        if '.' in date_str:
            return datetime.strptime(date_str.split('.')[0], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)


def get_epic_free_games():
    """
    Fetches all currently active 100% free-to-claim games from the Epic Games Store API.
    Uses multi-stage checking and timezone-aware date comparison for max resilience.
    """
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
            
            # 1. Get the best possible URL slug (Prioritize human-readable slug from mappings)
            product_slug = None
            
            # 1a. **PRIORITY**: Check the 'mappings' which often contain the clean, human-readable slug.
            if game_data.get('catalogNs', {}).get('mappings'):
                for mapping in game_data['catalogNs']['mappings']:
                    # Look for the primary store page slug
                    if mapping.get('pageType') in ['productHome', 'product']:
                        temp_slug = mapping.get('pageSlug')
                        # Heuristic: Prefer the clean slug (contains hyphens or is short) over a long UUID slug.
                        if temp_slug and ('-' in temp_slug or len(temp_slug) < 15): 
                            product_slug = temp_slug
                            break # Found a good candidate, stop looking in mappings
            
            # 1b. FALLBACK: Use generic product/url slugs if no good mapping was found (this often gives the UUID)
            if not product_slug:
                if game_data.get("productSlug"):
                    product_slug = game_data["productSlug"]
                elif game_data.get("urlSlug"):
                    product_slug = game_data["urlSlug"]
            
            if not product_slug:
                continue

            # 2. **PRIMARY CHECK:** Check if the price object itself indicates 100% off.
            price_data = game_data.get('price', {}).get('totalPrice', {})
            if price_data.get('discountPercentage') == 0 and price_data.get('originalPrice') > 0:
                # If the price object shows a discount of 100% and it's not a permanently free game (original price > 0)
                is_currently_free = True
            
            # 3. **SECONDARY CHECK:** Fallback to the complex promotions object if primary check fails.
            if not is_currently_free:
                promotions = game_data.get('promotions')

                # Check both current and *immediate* upcoming offers
                for offer_type in ['promotionalOffers', 'upcomingPromotionalOffers']:
                    offer_list = promotions.get(offer_type, []) if promotions else []
                    if not offer_list:
                        continue
                        
                    for offer_group in offer_list:
                        for offer in offer_group.get('promotionalOffers', []):
                            discount = offer.get('discountSetting', {}).get('discountPercentage')
                            start_date_str = offer.get('startDate')
                            end_date_str = offer.get('endDate')
                            
                            if discount == 0 and start_date_str and end_date_str: # 100% free
                                try:
                                    start_date = parse_epic_date(start_date_str)
                                    end_date = parse_epic_date(end_date_str)
                                    
                                    # Check if current time is within the free claim window
                                    if start_date <= now_utc < end_date:
                                        is_currently_free = True
                                        break
                                except Exception:
                                    # Silently skip on date parsing error
                                    continue
                        if is_currently_free:
                            break
                    if is_currently_free:
                        break
            
            # 4. Add to list if free and not claimed
            if is_currently_free and product_slug and title.lower() not in claimed_titles:
                # Clean the slug and form the URL
                slug_base = product_slug.split('/')[0] if '/' in product_slug else product_slug
                game_url = f"https://store.epicgames.com/en-US/p/{slug_base}"
                free_games.append((title, game_url))
                
    except requests.RequestException as e:
        print(f"❌ Error checking Epic Games Store (Network/API issue): {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred while parsing Epic Games data: {e}")
        
    return free_games


def get_steam_free_games():
    """
    Checks the Steam search page for games listed as 'Free'.
    ⚠️ NOTE: Web scraping is **fragile** and may break if Steam updates its site layout.
    """
    print("🔥 Checking Steam Store (web scraping, potentially fragile)...")
    games = []
    try:
        response = requests.get(STEAM_URL, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            game_rows = soup.find_all('a', class_='search_result_row')
            for game in game_rows[:5]: # Limit to first few results
                title = game.find('span', class_='title').text.strip()
                link = game['href']
                # Check for "Free" or similar in the price container
                price_tag = game.find('div', class_='search_price')
                if price_tag and ('Free' in price_tag.text or '$0.00' in price_tag.text):
                    games.append((title, link.split('?')[0])) # Clean the URL
    except Exception as e:
        print(f"❌ Error checking Steam: {e}")
    return games

def get_gog_free_games():
    """
    Attempts to scrape the main GOG page for a giveaway banner.
    ⚠️ NOTE: GOG's site is highly dynamic. This method is highly **unreliable**.
    """
    print("🌙 Checking GOG.com (web scraping, highly unreliable)...")
    games = []
    try:
        response = requests.get(GOG_URL, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Look for giveaway sections
            giveaway_section = soup.select_one('.product-tile-container--giveaway')
            if giveaway_section:
                link_tag = giveaway_section.select_one('a')
                title_tag = giveaway_section.select_one('.product-tile__title')
                if link_tag and title_tag:
                    title = title_tag.text.strip() + " (GOG GIVEAWAY)"
                    link = "https://www.gog.com" + link_tag['href']
                    games.append((title, link))
    except Exception as e:
        print(f"❌ Error checking GOG: {e}")
    return games

def get_ubisoft_free_games():
    """
    Attempts to scrape the Ubisoft free games page.
    ⚠️ NOTE: Web scraping is **fragile** and may break if Ubisoft updates its site layout.
    """
    print("🎮 Checking Ubisoft Store (web scraping, potentially fragile)...")
    games = []
    try:
        response = requests.get(UBISOFT_URL, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # Look for product tiles where the price is free
            for card in soup.select("div.product-tile"):
                price_tag = card.select_one("div.product-tile__price span")
                if price_tag and 'free' in price_tag.text.lower():
                    title_tag = card.select_one("span.product-tile-title")
                    link_tag = card.find("a", href=True)
                    if title_tag and link_tag:
                        title = title_tag.text.strip()
                        url = "https://store.ubisoft.com" + link_tag['href']
                        games.append((title, url))
    except Exception as e:
        print(f"❌ Error checking Ubisoft: {e}")
    return games

# --- CORE LOGIC ---

def notify(config):
    """Checks and opens links for unclaimed free games."""
    print("\n🎮 Checking REAL free games only... ✨", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    claimed_titles = load_claimed_games()

    epic_games = get_epic_free_games()
    steam_games = get_steam_free_games()
    gog_games = get_gog_free_games()
    ubisoft_games = get_ubisoft_free_games()

    def filter_claimed(games):
        return [(title, url) for title, url in games if title.lower() not in claimed_titles]

    # Epic function already includes claimed check, but we run it again for consistency
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

            # Process games in batches of 5
            batch = games_to_open[:5]
            games_to_open = games_to_open[5:]

            print(f"🌐 Opening next {len(batch)} games...")
            for title, url in batch:
                print(f"🔗 Opening: {title}")
                webbrowser.open(url)
                newly_claimed.append(title.lower())
                
                # --- LOGGING CLAIMED GAME ---
                if config['logging_enabled']:
                    log_claim(title, url)
                # ----------------------------

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

def show_menu(logging_status):
    """Displays the main menu."""
    log_state = "ON 📝" if logging_status else "OFF 👻"
    
    print("\n--- Free Games Claimer Menu ---")
    print("1. Start Claiming Games 🚀")
    print(f"L. Toggle Claim Logging (Current Status: {log_state})")
    print("V. View Claim Log 📄")
    print("C. Clear Claim Log 🔥")
    print("Z. Backup Claimer Files 💾 (to Downloads as ZIP)")
    print("0. Exit 😢")
    print("-----------------------------")

# Main Execution
if __name__ == "__main__":
    
    # 1. Load configuration
    config = load_config()

    # 2. Main menu loop
    while True:
        try:
            show_menu(config['logging_enabled'])
            choice = input("\nType your choice (1, L, V, C, Z, or 0): ").strip().upper()

            if choice == '0':
                print("Okay, exiting...")
                break
            
            elif choice == '1':
                notify(config)
                
            elif choice == 'L':
                config['logging_enabled'] = not config['logging_enabled']
                save_config(config)
                log_state = "ON 📝" if config['logging_enabled'] else "OFF 👻"
                print(f"\n📢 Logging is now **{log_state}**! Configuration saved.")
                
            elif choice == 'V':
                view_log()
                
            elif choice == 'C':
                clear_log()
                
            elif choice == 'Z':
                create_backup()
                
            else:
                print("That’s not on the list. Try again.")

        except ValueError:
            print("Invalid input. Please enter a valid option.")
        except KeyboardInterrupt:
            print("\nOkay, exiting...")
            breakss
