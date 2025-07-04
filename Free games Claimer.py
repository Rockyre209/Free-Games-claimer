import requests
import webbrowser
import os
from datetime import datetime
from bs4 import BeautifulSoup

# Save folder
DOCS_DIR = os.path.join(os.path.expanduser("~"), "Documents", "Free Games Claimer")
CLAIMED_FILE = os.path.join(DOCS_DIR, "claimed_games.txt")

# URLs and headers
EPIC_API = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=US&allowCountries=US"
STEAM_URL = "https://store.steampowered.com/search/?maxprice=free&specials=1"
GOG_URL = "https://www.gog.com/#giveaway"
UBISOFT_URL = "https://store.ubisoft.com/us/free-games"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def load_claimed_games():
    print("📂 Loading previously claimed games...")
    if os.path.exists(CLAIMED_FILE):
        with open(CLAIMED_FILE, "r", encoding="utf-8") as f:
            return set(line.strip().lower() for line in f if line.strip())
    return set()

def save_claimed_games(titles):
    print(f"💾 Saving {len(titles)} newly claimed games to file...")
    os.makedirs(DOCS_DIR, exist_ok=True)
    with open(CLAIMED_FILE, "a", encoding="utf-8") as f:
        for title in titles:
            f.write(title + "\n")

def get_epic_free_games():
    print("🛍️ Checking Epic Games Store...")
    games = []
    try:
        response = requests.get(EPIC_API, headers=headers)
        if response.status_code == 200:
            data = response.json()
            elements = data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", [])
            for game in elements:
                title = game.get("title", "Untitled")
                promotions = game.get("promotions")
                if not promotions or not promotions.get("promotionalOffers"):
                    continue

                slug = None

                if game.get("productSlug"):
                    slug = game["productSlug"]
                elif game.get("catalogNs", {}).get("mappings"):
                    slug = game["catalogNs"]["mappings"][0].get("pageSlug")
                elif game.get("urlSlug"):
                    slug = game["urlSlug"]

                if slug:
                    slug = slug.strip("/").split("/")[0]
                    link = f"https://store.epicgames.com/en-US/p/{slug}"
                    games.append((title, link))

    except Exception as e:
        print(f"❌ Error checking Epic: {e}")
    return games

def get_steam_free_games():
    print("🔥 Checking Steam Store...")
    games = []
    try:
        response = requests.get(STEAM_URL, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            game_rows = soup.find_all('a', class_='search_result_row')
            for game in game_rows[:5]:
                title = game.find('span', class_='title').text.strip()
                link = game['href']
                games.append((title, link))
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
            banner = soup.find('a', class_='giveaway-banner')
            if banner:
                title = banner.find('div', class_='giveaway-banner__title').text.strip()
                link = "https://www.gog.com" + banner['href']
                games.append((title, link))
            section = soup.find('section', {'data-ga-event-category': 'free games'})
            if section:
                tiles = section.find_all('a', class_='product-tile')
                for tile in tiles[:3]:
                    title = tile.get('title') or tile.find('span', class_='product-tile__title').text.strip()
                    link = "https://www.gog.com" + tile['href']
                    games.append((title.strip(), link))
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
                title_tag = card.select_one("span.product-tile-title")
                link_tag = card.find("a", href=True)
                if title_tag and link_tag:
                    title = title_tag.text.strip()
                    url = "https://store.ubisoft.com" + link_tag['href']
                    games.append((title, url))
    except Exception as e:
        print(f"❌ Error checking Ubisoft: {e}")
    return games

def notify():
    print("\n🎮 Checking REAL free games only... ✨", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

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
        print(f"\n✨ Found {len(all_games)} unclaimed free games! Ready to open, babe? Press ENTER to begin batch magic, or type 'no' to skip.")
        newly_claimed = []
        while True:
            choice = input("> ").strip().lower()
            if choice == "no":
                print("💤 Okayy, skipped this time darling...")
                break
            if not all_games:
                print("\nAll games already opened!")
                input("Press ENTER to close.")
                break

            batch = all_games[:5]
            all_games = all_games[5:]

            print(f"🌐 Opening next {len(batch)} games...")
            for title, url in batch:
                print(f"🔗 Opening: {title}")
                webbrowser.open(url)
                newly_claimed.append(title.lower())

            if all_games:
                print(f"\n⏭️ {len(all_games)} more remaining. Press ENTER for next batch, love.")
            else:
                print("\n🎉 All done opening! Wasn't that fun?")
                input("Press ENTER to wrap it up.")
                break

        save_claimed_games(newly_claimed)
    else:
        print("\n😢 No new games today, baby... we'll check again soon 💖")

# Main
if __name__ == "__main__":
    try:
        notify()
    except Exception as e:
        print(f"\n⚠️ Oops! Something went wrong: {e}")
    input("\nPress ENTER to close this window, darling... 💋")
