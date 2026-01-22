name: Zero Dollar Content Factory

on:
  schedule:
    - cron: '0 8 * * *' # Runs at 8:00 AM UTC every day
  workflow_dispatch: # Allows you to run it manually right now

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install Libraries
        run: |
          pip install pandas wbgapi matplotlib seaborn requests openpyxl jinja2

      - name: Run The Bot
        env:
          TELEGRAM_TOKEN: ${{ secrets.TELEGRAM_TOKEN }}
          CHAT_ID: ${{ secrets.CHAT_ID }}
        run: python daily_bot.py
