import asyncio
import hashlib
import os
import random
import re
import time
from datetime import date

import aiohttp
from dotenv import load_dotenv
from playwright.async_api import async_playwright, Page

load_dotenv()

APP_URL = os.environ.get("NEXT_PUBLIC_APP_URL", "http://localhost:3000")
SCRAPER_SECRET = os.environ.get("SCRAPER_SECRET", "")
TP_URL = os.environ.get("TRUSTPILOT_URL", "https://www.trustpilot.com/review/esvitaclinic.com")


def make_review_id(name: str, rating: int) -> str:
    return hashlib.sha256(f"tp|{name}|{rating}".encode()).hexdigest()


async def random_delay(min_s=1.0, max_s=2.5):
    await asyncio.sleep(random.uniform(min_s, max_s))


async def dismiss_cookie(page: Page):
    try:
        btn = page.locator('#onetrust-accept-btn-handler').first
        if await btn.is_visible(timeout=3000):
            await btn.click()
            await asyncio.sleep(1)
            print("Cookie banner dismissed")
    except Exception:
        pass


async def expand_reviews(page: Page):
    """Click all 'See more' buttons to get full review text."""
    for sel in [
        'button[data-service-review-content-toggle]',
        'span.styles_seeMore__J_tOL',
        'button:has-text("See more")',
    ]:
        btns = page.locator(sel)
        count = await btns.count()
        for i in range(count):
            try:
                btn = btns.nth(i)
                if await btn.is_visible(timeout=200):
                    await btn.click()
                    await asyncio.sleep(0.15)
            except Exception:
                pass


async def extract_reviews_from_page(page: Page) -> list[dict]:
    reviews = []

    await expand_reviews(page)
    await asyncio.sleep(0.5)

    articles = page.locator('article')
    count = await articles.count()
    if count == 0:
        return reviews

    for i in range(count):
        try:
            art = articles.nth(i)

            # Name
            name = 'Anonim'
            name_el = art.locator('[data-consumer-name-typography="true"]').first
            if await name_el.count() > 0:
                t = (await name_el.inner_text()).strip()
                if t:
                    name = t

            # Rating from star image alt text: "Rated 5 out of 5 stars"
            rating = 5
            star_img = art.locator('img[alt*="Rated"], img[alt*="star"], img[alt*="Star"]').first
            if await star_img.count() > 0:
                alt = (await star_img.get_attribute('alt')) or ''
                m = re.search(r'(\d)', alt)
                if m:
                    rating = int(m.group(1))

            # Review text
            text = ''
            text_el = art.locator('[data-relevant-review-text-typography="true"]').first
            if await text_el.count() > 0:
                raw = (await text_el.inner_text()).strip()
                # Remove "See more" suffix if present
                raw = re.sub(r'\s*See more\s*$', '', raw).strip()
                # Skip lorem ipsum placeholder (flagged reviews)
                if raw and 'lorem ipsum' not in raw.lower():
                    text = raw

            # Skip if name is still default and no useful data
            if name == 'Anonim' and not text:
                continue

            rid = make_review_id(name, rating)
            reviews.append({
                'review_id': rid,
                'reviewer_name': name,
                'rating': rating,
                'review_text': text,
            })

        except Exception as e:
            print(f"  Error on article {i}: {e}")
            continue

    return reviews


async def scrape_reviews() -> list[dict]:
    all_reviews: dict[str, dict] = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            locale='en-US',
            viewport={'width': 1280, 'height': 900},
            user_agent=(
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/124.0.0.0 Safari/537.36'
            ),
        )
        page = await context.new_page()

        print(f"Navigating to: {TP_URL}")
        await page.goto(TP_URL, wait_until='domcontentloaded', timeout=60000)
        await random_delay(2, 4)
        await dismiss_cookie(page)
        await random_delay(1, 2)

        page_num = 1
        consecutive_empty = 0
        max_pages = 200

        while page_num <= max_pages:
            if page_num > 1:
                url = f"{TP_URL}?page={page_num}"
                await page.goto(url, wait_until='domcontentloaded', timeout=60000)
                await random_delay(1.5, 2.5)

            batch = await extract_reviews_from_page(page)
            new_count = 0
            for r in batch:
                if r['review_id'] not in all_reviews:
                    all_reviews[r['review_id']] = r
                    new_count += 1

            if new_count > 0:
                consecutive_empty = 0
                print(f"Page {page_num}: +{new_count} new → {len(all_reviews)} total")
            else:
                consecutive_empty += 1
                print(f"Page {page_num}: no new ({consecutive_empty} consecutive)")
                if consecutive_empty >= 3:
                    print("3 consecutive empty pages. Done.")
                    break

            page_num += 1
            await random_delay(1, 2)

        await browser.close()

    return list(all_reviews.values())


async def post_to_api(reviews: list[dict]) -> dict:
    today = date.today().isoformat()
    payload = {'reviews': reviews, 'snapshot_date': today, 'platform': 'trustpilot'}

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{APP_URL}/api/scraper",
            json=payload,
            headers={'Authorization': f'Bearer {SCRAPER_SECRET}', 'Content-Type': 'application/json'},
            timeout=aiohttp.ClientTimeout(total=120),
        ) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise Exception(f"API error {resp.status}: {text}")
            return await resp.json()


async def main():
    print("Starting Trustpilot scraper...")
    start = time.time()
    reviews = await scrape_reviews()
    elapsed = time.time() - start
    print(f"\nCollected {len(reviews)} unique reviews in {elapsed:.1f}s")

    if not reviews:
        print("No reviews found.")
        return

    print("Sample:")
    for r in reviews[:3]:
        preview = r['review_text'][:60] if r['review_text'] else '(no text)'
        print(f"  [{r['rating']}★] {r['reviewer_name']}: {preview}")

    result = await post_to_api(reviews)
    print(f"\nAPI: new={result.get('new')}, deleted={result.get('deleted')}, total={result.get('total')}")


if __name__ == '__main__':
    asyncio.run(main())
