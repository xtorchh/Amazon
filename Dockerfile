FROM mcr.microsoft.com/playwright/python:v1.43.1-jammy

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install --with-deps

CMD ["python", "amazon_scraper.py"]
