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

## Deploying on Render (Docker Method - Recommended)

Since this bot uses Playwright, the easiest way to deploy on Render is using **Docker**. This avoids issues with system dependencies.

1.  **Push to GitHub**: Upload all files, including `Dockerfile`.
2.  **Create New Web Service**: Select your repository on Render.
3.  **Environment**: Select **Docker**.
4.  **Environment Variables**:
    *   Add `TELEGRAM_BOT_TOKEN`: Your bot token.
5.  **Deploy**: Render will build the image and start the bot automatically.

## Deploying on Render (Manual Method)

If you prefer not to use Docker:
1.  **Build Command**: `chmod +x render-build.sh && ./render-build.sh`
2.  **Start Command**: `python bot.py`
3.  **Note**: This method might fail due to root permission requirements for browser dependencies. Docker is the preferred way.

## Usage
- Open your bot in Telegram.
- Type `/start` to see the welcome message.
- Type `/attendance` to start the process.
- Follow the prompts to enter your Student ID and Password.
- Wait for the bot to fetch and display your 📊 Attendance Report.

---
**Note**: This bot is for educational purposes. Ensure you comply with your institution's policies regarding automated access to portals.
