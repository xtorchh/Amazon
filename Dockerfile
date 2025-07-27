# Use a stable Playwright Python base image
FROM mcr.microsoft.com/playwright/python:v1.43.1-focal

# Set working directory
WORKDIR /app

# Copy project files into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install --with-deps

# Expose port (optional if you use webserver; safe to include)
EXPOSE 8000

# Run the script
CMD ["python", "scraper_bot.py"]