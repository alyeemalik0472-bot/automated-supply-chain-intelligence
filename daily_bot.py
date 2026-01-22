import os
import wbgapi as wb
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import random
from datetime import datetime

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# --- SOURCE 1: WORLD BANK (ECONOMY) ---
def get_economy_chart():
    print("Fetching Economy Data...")
    df = wb.data.DataFrame('NY.GDP.MKTP.KD.ZG', mrv=1, labels=True)
    df = df.sort_values(by=df.columns[1], ascending=False).head(10)
    return df, "🚀 Top Growing Economies", "Source: World Bank"

# --- SOURCE 2: OUR WORLD IN DATA (TECH/ENV) ---
def get_tech_chart():
    print("Fetching Tech Data...")
    url = "https://raw.githubusercontent.com/owid/owid-datasets/master/datasets/Share%20of%20the%20population%20using%20the%20Internet/Share%20of%20the%20population%20using%20the%20Internet.csv"
    df = pd.read_csv(url)
    latest_year = df['Year'].max()
    df = df[df['Year'] == latest_year]
    df = df.sort_values(by='Share of the population using the Internet', ascending=False).head(10)
    df = df.set_index('Entity')[['Share of the population using the Internet']]
    return df, f"🌐 Most Connected Countries ({latest_year})", "Source: Our World in Data"

# --- SOURCE 3: SUPPLY CHAIN & RETAIL (YOUR JOB NICHE) ---
def get_supply_chain_chart():
    print("Fetching Supply Chain Data...")
    metrics = {
        'LP.LPI.OVRL.XQ': {'title': "📦 Top Logistics Hubs (LPI Score)", 'xlabel': "Efficiency Score (1-5)"},
        'IS.SHP.GOOD.TU': {'title': "🚢 Busiest Ports (Million TEU)", 'xlabel': "TEU"},
        'NE.CON.PRVT.PC.KD': {'title': "🛍️ Top Consumer Markets", 'xlabel': "Spending Per Capita (USD)"}
    }
    code = random.choice(list(metrics.keys()))
    info = metrics[code]
    df = wb.data.DataFrame(code, mrv=1, labels=True)
    df = df.sort_values(by=df.columns[1], ascending=False).head(10)
    if code == 'IS.SHP.GOOD.TU': df.iloc[:, 0] = df.iloc[:, 0] / 1000000 
    return df, info['title'], "Source: World Bank LPI/WDI"

# --- THE DESIGN ENGINE ---
def create_chart(df, title, source_text):
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(9, 16))
    sns.barplot(x=df.iloc[:, 0], y=df.index, palette='cool', ax=ax)
    ax.set_title(f"{title}\n", fontsize=24, color='white', weight='bold')
    plt.text(0, len(df)+1, source_text, color='#888888', fontsize=12)
    sns.despine(left=True, bottom=True)
    filename = "daily_post.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='black')
    return filename

# --- TELEGRAM SENDER ---
def send_to_telegram(filename, caption):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Error: Telegram keys not found.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    with open(filename, 'rb') as f:
        requests.post(url, files={'photo': f}, data={'chat_id': CHAT_ID, 'caption': caption})

# --- MAIN CONTROLLER ---
if __name__ == "__main__":
    try:
        choice = random.choice(['economy', 'tech', 'supply_chain'])
        if choice == 'economy': data, title, source = get_economy_chart()
        elif choice == 'tech': data, title, source = get_tech_chart()
        else: data, title, source = get_supply_chain_chart()
        
        image_file = create_chart(data, title, source)
        send_to_telegram(image_file, f"Here is your {choice} content! 📊 #SupplyChain")
        print("Done!")
    except Exception as e:
        print(f"Failed: {e}")
