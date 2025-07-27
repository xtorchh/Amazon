import asyncio
import logging
from datetime import datetime
from playwright.async_api import async_playwright
import aiohttp
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s")

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1398087107469250591/zZ7WPGGj-cQ7l5H8VRV48na0PqgOAKqE1exEIm3vBRVnuCk7BcuP21UIu-vEM8KRfLVQ"

async def send_discord_message(content, file_path=None):
    async with aiohttp.ClientSession() as session:
        data = {"content": content}
        if file_path and os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                webhook = aiohttp.FormData()
                webhook.add_field('file', f, filename=os.path.basename(file_path), content_type='image/png')
                webhook.add_field('payload_json', str(data))
                async with session.post(DISCORD_WEBHOOK_URL, data=webhook) as resp:
                    logging.info(f"Discord responded with {resp.status}")
        else:
            async with session.post(DISCORD_WEBHOOK_URL, json=data) as resp:
                logging.info(f"Discord responded with {resp.status}")

async def scrape_amazon(page):
    url = "https://www.amazon.co.uk/s?k=epic+deals"
    logging.info("Navigating to Amazon deals page...")
    await page.goto(url, timeout=60000)

    try:
        logging.info("Waiting for product selector")
        await page.wait_for_selector("div.s-main-slot.s-result-list", timeout=15000)
    except Exception as e:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot = f"screenshot_fail_{timestamp}.png"
        try:
            await page.screenshot(path=screenshot)
            await send_discord_message("❌ Could not find product listings on Amazon page.", file_path=screenshot)
        except Exception as ss_err:
            logging.error(f"Failed to send screenshot: {ss_err}")
            await send_discord_message("❌ Could not find product listings on Amazon page. (Screenshot failed)")
        logging.error(f"No products found: {e}")
        return []

    products = await page.query_selector_all("div.s-main-slot.s-result-list > div[data-component-type='s-search-result']")
    logging.info(f"Found {len(products)} products")

    qualifying_deals = []

    for product in products:
        try:
            title_el = await product.query_selector("h2 a span")
            price_whole_el = await product.query_selector("span.a-price-whole")
            price_fraction_el = await product.query_selector("span.a-price-fraction")
            saving_el = None  # Amazon doesn't show saving clearly on search results

            title = await title_el.inner_text() if title_el else None
            price_whole = await price_whole_el.inner_text() if price_whole_el else None
            price_fraction = await price_fraction_el.inner_text() if price_fraction_el else "00"

            if not title or not price_whole:
                continue

            price_str = f"{price_whole}.{price_fraction}".replace(",", "")
            price = float(price_str)

            # For simplicity, send all products as deals since no saving info on page
            message = f"🛒 **{title.strip()}**
💷 Price: £{price:.2f}
🔗 https://www.amazon.co.uk{await product.query_selector_eval('h2 a', 'el => el.getAttribute("href")')}"

            qualifying_deals.append(message)

        except Exception as e:
            logging.warning(f"Skipping a product due to error: {e}")
            continue

    return qualifying_deals

async def main():
    logging.info("Starting Amazon scraper...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
        page = await context.new_page()

        deals = await scrape_amazon(page)

        if deals:
            for deal in deals:
                await send_discord_message(deal)
                await asyncio.sleep(1)
        else:
            await send_discord_message("ℹ️ No qualifying deals found.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())