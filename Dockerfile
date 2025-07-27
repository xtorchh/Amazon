# Use Playwright Python image based on Ubuntu 22.04 (Jammy)
FROM mcr.microsoft.com/playwright/python:v1.53.0-jammy

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers with required system dependencies
RUN playwright install --with-deps

# Default command to run your scraper script
CMD ["python", "amazon_scraper.py"]