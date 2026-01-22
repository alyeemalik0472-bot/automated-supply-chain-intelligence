import os
import requests
import sys

# 1. Get Secrets
TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

print(f"DEBUG: Checking Keys...")
if not TOKEN:
    print("❌ FAIL: Token is missing!")
    sys.exit(1)
if not CHAT_ID:
    print("❌ FAIL: Chat ID is missing!")
    sys.exit(1)

print(f"DEBUG: Token found. Chat ID is: {CHAT_ID}")

# 2. Force a Message
print("DEBUG: Sending message...")
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
params = {'chat_id': CHAT_ID, 'text': "🔔 TEST: Verification Successful!"}

response = requests.post(url, params=params)

print(f"DEBUG: Telegram replied with Code {response.status_code}")
print(f"DEBUG: Telegram replied with Text: {response.text}")

# 3. CRASH if not successful (This turns the checkmark RED)
if response.status_code != 200:
    print("❌ FAILURE: Message was rejected.")
    sys.exit(1)
else:
    print("🎉 SUCCESS: Message accepted.")
