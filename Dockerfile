# Use the official Playwright image which comes with browsers and dependencies pre-installed
FROM mcr.microsoft.com/playwright/python:v1.45.0-jammy

# Set work directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variable for Playwright (headless mode)
ENV PYTHONUNBUFFERED=1

# Command to run the bot
CMD ["python", "bot.py"]
