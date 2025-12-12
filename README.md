# 🕹️ Free Games Claimer — Automatic Multi-Store Free Game Scanner

Collecting free games from Epic, Steam, GOG, and Ubisoft sounds fun… until you realise how annoying it actually is. Every store hides freebies differently, promotions appear randomly, you forget which ones you already claimed, and before you know it — a giveaway expires. This tool exists because constantly checking four different stores manually is boring, repetitive, and easy to forget.

Free Games Claimer fully automates that entire process.

## 🎯 What This Tool Does (In Simple Words)
- Checks Epic Games Store (via API — stable and accurate)
- Scrapes Steam, GOG, and Ubisoft for 100% free, limited-time giveaways
- Filters out permanently free games and duplicates
- Tracks what you already claimed so it won’t show again
- Automatically opens claim pages in batches for convenience
- Can log every claim with timestamps
- Can create ZIP backups of all logs/configs in your Downloads folder
- Saves all data into your Documents folder for persistence

This turns the daily “open 4 websites and search manually” routine into a 10-second automated scan.

## 🚩 The Problem It Solves
Before this script:
- You manually open Epic → check promotions  
- Then open Steam → filter free specials  
- Then check GOG giveaways  
- Then check Ubisoft free offers  
- You forget what you claimed  
- You repeat this every day  
- You often miss giveaways  

After this script:
- Run once → It scans all stores  
- Shows only real freebies  
- Opens only games you haven’t already claimed  
- Logs them (optional)  
- Backs up data when needed  
- No manual searching, no missed giveaways

A completely automated free-game detector that simply works.

## 🚀 How to Use
Install dependencies:

```
pip install -r requirements.txt
```

Run the script:

```
python free_games_claimer.py
```

You will get a simple menu that allows you to:
- Start scanning & claiming games
- Turn logging ON/OFF
- View logs
- Clear logs
- Create backups
- Exit

No extra configuration required — it creates all needed files automatically.

## 📁 Files in This Project
free_games_claimer.py — Main program  
requirements.txt — Python dependencies  
LICENSE — MIT License  
README.md — This file  
claimer_config.txt — Auto-generated logging preference  
claimed_games.txt — Auto-generated claimed game history  
claimer_log.txt — Auto-generated logs (only when logging enabled)

Runtime files are stored in:
Documents/Free Games Claimer/

## 💡 Why This README Matters
This file explains clearly:
- The original problem users face  
- Why this project exists  
- What exact solution it provides  
- How to run it  
- What files it uses  

The goal is to make the project instantly understandable to anyone visiting your GitHub.

## 📄 License
MIT License. Free to use and modify.

## 🎉 Final Note
This script removes the frustration of checking for free games daily.  
Run it once a day — it handles everything else automatically.  
Never miss another giveaway again.
