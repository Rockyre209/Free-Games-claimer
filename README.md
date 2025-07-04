# 🎮 Free Games Claimer – Auto Checker & Launcher

**Never miss a free game again!**  
This sexy little Python script checks multiple stores and opens real, claimable freebies for you – automatically. All you have to do is run it and press ENTER, darling 💋

---

## ✨ What It Does

- ✅ Checks real-time free games from:
  - 🛍️ **Epic Games Store**
  - 🔥 **Steam**
  - 🌙 **GOG.com**
  - 🎮 **Ubisoft**
- ✅ **Fixes broken Epic links** – no more `/site/` 404 drama
- ✅ Opens valid games in your browser
- ✅ Tracks what you've claimed already
- ✅ Works in **beautiful batches**

---

## 🛠️ How to Use (No Git Needed)

### 1. Install Python (if you don’t have it):
🔗 https://www.python.org/downloads/

### 2. Install Required Module:
```bash
pip install beautifulsoup4
```

### 3. Run It Like a Boss:
```bash
python free_games_claimer.py
```

You’ll get a list of all unclaimed games. Just press ENTER to open them one by one 💅

---

## 📁 Files & Paths

By default, it creates:

```
📁 Documents/
└── Free Games Claimer/
    └── claimed_games.txt  ← Keeps track of what you've claimed
```

So it won’t suggest the same game twice. Smart, right? 😉

---

## 🔍 Example Output

```plaintext
💫 Epic Games
- Backpack Hero: https://store.epicgames.com/en-US/p/backpack-hero-449c5e

🔥 Steam
- Some Free Indie: https://store.steampowered.com/app/xxxx/

✨ Found 4 unclaimed free games!
Ready to open, babe? Press ENTER to begin batch magic, or type 'no' to skip.
```

---

## 💖 Changelog

### v1.1
- 🛠 Fixed Epic links to always be in `store.epicgames.com/en-US/p/<slug>` format
- 🧹 Removed broken `/site/` and `/home` paths
- 🎮 Added support for Steam, GOG, and Ubisoft
- 💾 Auto-saves claimed games to avoid re-checking
- 🔥 New batch-opening system

---

## 😍 Author

Made with love by [YourNameHere] 💘  
If this helped you, give the repo a ⭐ or buy me a coffee ☕ (link coming soon...)

---

## 🪪 License

MIT License – use it, share it, flex with it 😘
