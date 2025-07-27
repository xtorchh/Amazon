import asyncio
import logging
from playwright.async_api import async_playwright
import aiohttp
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s")

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
MAX_PRICE = 500.00
SEARCH_TERM = "laptop deals"

async def send_discord_message(content):
    async with aiohttp.ClientSession() as session:
        async with session.post(WEBHOOK_URL, json={"content": content}) as resp:
            logging.info(f"Discord responded with {resp.status}")
            await asyncio.sleep(1)

async def scrape_amazon():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/115.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()

        search_url = f"https://www.amazon.co.uk/s?k={SEARCH_TERM.replace(' ', '+')}"
        logging.info(f"Searching Amazon: {search_url}")
        await page.goto(search_url, timeout=60000)
        await page.wait_for_selector("div.s-main-slot")

        items = await page.query_selector_all("div.s-main-slot div[data-component-type='s-search-result']")
        logging.info(f"Found {len(items)} results")

        for item in items:
            try:
                title_el = await item.query_selector("h2 a span")
                price_whole = await item.query_selector("span.a-price-whole")
                price_fraction = await item.query_selector("span.a-price-fraction")
                link_el = await item.query_selector("h2 a")

                if not title_el or not price_whole or not link_el:
                    continue

                title = await title_el.inner_text()
                price_str = await price_whole.inner_text() + "." + (await price_fraction.inner_text())
                price = float(price_str.replace(",", ""))
                link = "https://www.amazon.co.uk" + await link_el.get_attribute("href")

                if price <= MAX_PRICE:
                    message = f"🛒 **{title.strip()}**\n💷 £{price:.2f}\n🔗 {link}"
                    await send_discord_message(message)

            except Exception as e:
                logging.warning(f"Error parsing item: {e}")
                continue

        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_amazon())
