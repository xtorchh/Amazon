# Dockerfile for Playwright scraper using python:3.10-slim
FROM python:3.10-slim

# Install dependencies for Playwright and Chromium
RUN apt-get update && apt-get install -y     curl     wget     gnupg     ca-certificates     fonts-liberation     libasound2     libatk-bridge2.0-0     libatk1.0-0     libcups2     libdbus-1-3     libdrm2     libgbm1     libgtk-3-0     libnspr4     libnss3     libx11-xcb1     libxcomposite1     libxdamage1     libxrandr2     libxss1     libxtst6     xdg-utils     --no-install-recommends &&     rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN python -m playwright install --with-deps

# Copy scraper script
COPY scraper_bot.py .

# Run scraper
CMD ["python", "scraper_bot.py"]