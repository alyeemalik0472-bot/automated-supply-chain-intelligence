import os
import smtplib
import wbgapi as wb
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import io
import yfinance as yf  # <--- NEW LIBRARY
from datetime import datetime
from email.message import EmailMessage

# --- CONFIGURATION ---
EMAIL_USER = os.environ.get('EMAIL_USER')
EMAIL_PASS = os.environ.get('EMAIL_PASS')

# --- THE CHART DESIGNER ---
def generate_chart(df, title, source, filename):
    try:
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(10, 14))
        
        # Standardize: Top 12 values
        df = df.iloc[:12]
        
        # Color Logic: Green for positive, Red for negative (Stocks only)
        if "Change" in title:
            colors = ['#00ff00' if x >= 0 else '#ff0000' for x in df.iloc[:, 0]]
            sns.barplot(x=df.iloc[:, 0], y=df.index, palette=colors, ax=ax)
        else:
            sns.barplot(x=df.iloc[:, 0], y=df.index, palette='viridis', ax=ax)
        
        # Typography
        ax.set_title(f"{title}\n", fontsize=22, color='white', weight='bold', pad=20)
        plt.text(0, len(df)+1, f"Source: {source} | {datetime.now().strftime('%Y-%m-%d')}", color='#888888', fontsize=10)
        
        # Clean up
        ax.set_xlabel("")
        ax.set_ylabel("")
        sns.despine(left=True, bottom=True)
        ax.tick_params(axis='y', labelsize=12)
        
        plt.savefig(filename, dpi=100, bbox_inches='tight', facecolor='black')
        plt.close()
        print(f"✅ Created: {filename}")
        return filename
    except Exception as e:
        print(f"⚠️ Skip ({title}): {e}")
        return None

# --- SOURCE 1: STOCK MARKET (NEW!) ---
def fetch_stocks():
    print("--- Fetching Market Data ---")
    charts = []
    # Tickers: Shipping (ZIM, GSL), Logistics (FDX, UPS), Fuel (CL=F), Tech (AMZN)
    tickers = ['ZIM', 'GSL', 'FDX', 'UPS', 'AMZN', 'CL=F', 'DAC', 'XPO']
    names = {
        'ZIM': 'ZIM Shipping', 'GSL': 'Global Ship Lease', 'FDX': 'FedEx',
        'UPS': 'UPS Logistics', 'AMZN': 'Amazon', 'CL=F': 'Crude Oil',
        'DAC': 'Danaos Corp', 'XPO': 'XPO Logistics'
    }
    
    try:
        # Download last 5 days of data
        data = yf.download(tickers, period="5d")['Close']
        
        # Calculate % Change from yesterday
        latest = data.iloc[-1]
        prev = data.iloc[-2]
        pct_change = ((latest - prev) / prev) * 100
        
        # Rename tickers to real names
        pct_change.index = [names.get(x, x) for x in pct_change.index]
        
        # Sort by biggest movers
        df = pct_change.sort_values(ascending=False).to_frame(name='Value')
        
        filename = "market_movers.png"
        if generate_chart(df, "Daily Market Movers (% Change)", "Yahoo Finance", filename):
            charts.append(filename)
            
    except Exception as e:
        print(f"Stock Error: {e}")
        
    return charts

# --- SOURCE 2: WORLD BANK ---
def fetch_world_bank():
    print("--- Fetching World Bank ---")
    indicators = {
        'NY.GDP.MKTP.KD.ZG': 'Top GDP Growth (%)',
        'FP.CPI.TOTL.ZG': 'Highest Inflation Rates (%)',
        'NE.TRD.GNFS.ZS': 'Trade Dependence (% GDP)',
        'LP.LPI.OVRL.XQ': 'Top Logistics Hubs (LPI)', 
        'IS.SHP.GOOD.TU': 'Port Traffic (Million TEU)',
        'SL.UEM.TOTL.ZS': 'Unemployment Rate (%)'
    }
    charts = []
    for code, title in indicators.items():
        try:
            df = wb.data.DataFrame(code, mrv=1, labels=True)
            ascending = True if "Unemployment" in title else False
            df = df.sort_values(by=df.columns[1], ascending=ascending)
            if 'TEU' in title: df.iloc[:, 0] = df.iloc[:, 0] / 1000000
            
            filename = f"wb_{code}.png"
            if generate_chart(df, title, "World Bank", filename):
                charts.append(filename)
        except: pass
    return charts

# --- SOURCE 3: WIKIPEDIA (Energy) ---
def fetch_wiki_energy():
    print("--- Fetching Energy ---")
    charts = []
    try:
        url = "https://en.wikipedia.org/wiki/List_of_countries_by_renewable_electricity_production"
        dfs = pd.read_html(url)
        df = dfs[1].iloc[:, [0, 2]]
        df.columns = ['Country', 'Value']
        df['Value'] = pd.to_numeric(df['Value'].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce')
        df = df.dropna().sort_values('Value', ascending=False).set_index('Country')
        
        filename = "wiki_energy.png"
        if generate_chart(df, "Top Green Energy Producers", "Wikipedia/IEA", filename):
            charts.append(filename)
    except: pass
    return charts

# --- SOURCE 4: SIPRI (Defense) ---
def fetch_sipri():
    print("--- Fetching Defense ---")
    charts = []
    try:
        url = "https://www.sipri.org/sites/default/files/SIPRI-Milex-data-1949-2024.xlsx"
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        with io.BytesIO(r.content) as f:
            df = pd.read_excel(f, sheet_name="Current USD", skiprows=5)
        last_col = df.columns[-1]
        df = df[['Country', last_col]].dropna().sort_values(last_col, ascending=False).set_index('Country')
        
        filename = "sipri_defense.png"
        if generate_chart(df, f"Top Military Budgets ({last_col})", "SIPRI", filename):
            charts.append(filename)
    except: pass
    return charts

# --- EMAILER ---
def send_email(attachments):
    if not attachments: return
    print(f"📧 Sending {len(attachments)} charts...")
    msg = EmailMessage()
    msg['Subject'] = f"📊 Daily Intel: {len(attachments)} Charts Ready"
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_USER
    msg.set_content("Daily Market Intelligence Briefing.\n\nGenerated by Python.")

    for file in attachments:
        with open(file, 'rb') as f:
            msg.add_attachment(f.read(), maintype='image', subtype='png', filename=file)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)
    print("🎉 Email Sent!")

# --- MAIN ---
if __name__ == "__main__":
    files = []
    files.extend(fetch_stocks())      # <--- The New Stock Function
    files.extend(fetch_world_bank())
    files.extend(fetch_wiki_energy())
    files.extend(fetch_sipri())
    send_email(files)
