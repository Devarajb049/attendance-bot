# MITS IMS Attendance Telegram Bot

A Telegram bot that scrapes student attendance from the [MITS IMS Portal](http://mitsims.in/) and provides a neat report.

## Features
- Interactive login (Bot asks for Student ID and Password).
- Scrapes subject-wise attendance (Attended/Total/Percentage).
- Calculates overall attendance percentage.
- Secure (deletes password message after receiving).

## Local Setup

1. **Clone or Download** this directory.
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```
3. **Set your Bot Token**:
   - Create a bot via [@BotFather](https://t.me/BotFather) and get the API Token.
   - Set it as an environment variable:
     - **Windows (PowerShell)**: `$env:TELEGRAM_BOT_TOKEN="your_token_here"`
     - **Linux/Mac**: `export TELEGRAM_BOT_TOKEN="your_token_here"`
4. **Run the Bot**:
   ```bash
   python bot.py
   ```

## Deploying on Render

1. **Create a Github Repository** with these files.
2. **Create a New Web Service** on [Render](https://render.com/).
3. **Configure Service**:
   - **Environment**: Python
   - **Build Command**: `./render-build.sh` (Make sure to give it execute permissions: `chmod +x render-build.sh` before pushing to git).
   - **Start Command**: `python bot.py`
4. **Environment Variables**:
   - Add `TELEGRAM_BOT_TOKEN` with your bot's token.
   - Add `PYTHON_VERSION` (e.g., `3.10.0`).

## Usage
- Open your bot in Telegram.
- Type `/start` to see the welcome message.
- Type `/attendance` to start the process.
- Follow the prompts to enter your Student ID and Password.
- Wait for the bot to fetch and display your 📊 Attendance Report.

---
**Note**: This bot is for educational purposes. Ensure you comply with your institution's policies regarding automated access to portals.
