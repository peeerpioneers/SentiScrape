#✅ SentiScrape 📘  
Sentiment sensor 

📘 README.md
markdown
# SentiScrape

**Scrape Yahoo Finance community comments. Analyze investor sentiment. Visualize engagement.**

SentiScrape lets you tap into the emotional pulse of retail investors by scraping the Yahoo Finance *Community* section for any stock ticker. It extracts comment text, timestamps, thumbs up/down, and runs sentiment analysis using VADER — perfect for short, social-style text. Then it visualizes engagement trends and sentiment shifts over time.

---

## 🚀 Features

- 🔍 Scrape Yahoo Finance comment threads using Playwright
- 💬 Analyze sentiment using VADER (compound polarity scoring)
- 📊 Track engagement: comment volume, thumbs up/down per day
- 📈 Visualize sentiment and engagement trends
- 🖥️ CLI interface for scraping and analysis in one command
- 🧩 Modular design for easy extension or integration

---

## 📦 Installation

```bash
git clone https://github.com/peeerpioneers/SentiScrape.git
cd SentiScrape
pip install -r requirements.txt
playwright install
