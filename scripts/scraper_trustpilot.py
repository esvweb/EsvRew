import asyncio
import hashlib
import os
import random
import time
from datetime import date

import aiohttp
from dotenv import load_dotenv
from playwright.async_api import async_playwright, Page

load_dotenv()

APP_URL = os.environ.get("NEXT_PUBLIC_APP_URL", "http://localhost:3000")
SCRAPER_SECRET = os.environ.get("SCRAPER_SECRET", "")
TP_URL = os.environ.get("TRUSTPILOT_URL", "https://www.trustpilot.com/review/esvitaclinic.com")


def make_review_id(tp_id: str, name: str, rating: int) -> str:
    """Use Trustpilot's own review ID if available, else hash name+rating."""
    if tp_id:
        return hashlib.sha256(f"tp|{tp_id}".encode()).hexdigest()
    return hashlib.sha256(f"tp|{name}|{rating}".encode()).hexdigest()


async def random_delay(min_s=1.0, max_s=2.5):
    await asyncio.sleep(random.uniform(min_s, max_s))


async def dismiss_consent(page: Page):
    for sel in [
        '#onetrust-accept-btn-handler',
        'button[id*="accept"]',
        'button[data-testid="close-btn"]',
    ]:
        try:
            btn = page.locator(sel).first
            if await btn.is_visible(timeout=2000):
                await btn.click()
                await asyncio.sleep(1)
                print("Dismissed cookie banner")
                return
        except Exception:
            pass


async def extract_reviews_from_page(page: Page) -> list[dict]:
    reviews = []

    # Wait for review cards
    try:
        await page.wait_for_selector('[data-service-review-id], article.review', timeout=10000)
    except Exception:
        return reviews

    cards = page.locator('[data-service-review-id]')
    count = await cards.count()
    if count == 0:
        cards = page.locator('article.review, div[class*="reviewCard"]')
        count = await cards.count()

    for i in range(count):
        try:
            card = cards.nth(i)

            # Trustpilot review ID from attribute
            tp_id = (await card.get_attribute('data-service-review-id')) or ''

            # Reviewer name
            name = 'Anonim'
            for sel in [
                'span[data-consumer-name-typography]',
                'a[name*="consumer"] span',
                '.typography_heading-xxs__QKBS8',
                'span[class*="consumerName"]',
                'a[class*="consumer"] span',
            ]:
                try:
                    n = card.locator(sel).first
                    if await n.count() > 0:
                        t = (await n.inner_text()).strip()
                        if t:
                            name = t
                            break
                except Exception:
                    pass

            # Rating from data attribute or stars
            rating = 5
            for sel in [
                '[data-service-review-rating]',
                'div[class*="star-rating"]',
                'div[class*="starRating"]',
            ]:
                try:
                    s = card.locator(sel).first
                    if await s.count() > 0:
                        # Try data attribute first
                        val = await s.get_attribute('data-service-review-rating')
                        if val and val.isdigit():
                            rating = int(val)
                            break
                        # Try aria-label
                        label = (await s.get_attribute('aria-label')) or ''
                        for n in range(1, 6):
                            if str(n) in label[:4]:
                                rating = n
                                break
                        break
                except Exception:
                    pass

            # Also try img alt text for rating
            if rating == 5:
                try:
                    img = card.locator('img[alt*="star"], img[alt*="Star"]').first
                    if await img.count() > 0:
                        alt = (await img.get_attribute('alt')) or ''
                        for n in range(1, 6):
                            if str(n) in alt[:4]:
                                rating = n
                                break
                except Exception:
                    pass

            # Review text
            text = ''
            for sel in [
                'p[data-service-review-text-typography]',
                'p[class*="typography_body"]',
                'div[class*="reviewText"] p',
                'section p',
                'p.review-content__text',
            ]:
                try:
                    t = card.locator(sel).first
                    if await t.count() > 0:
                        txt = (await t.inner_text()).strip()
                        if txt:
                            text = txt
                            break
                except Exception:
                    pass

            rid = make_review_id(tp_id, name, rating)
            reviews.append({
                'review_id': rid,
                'reviewer_name': name,
                'rating': rating,
                'review_text': text,
            })

        except Exception as e:
            print(f"  Error on card {i}: {e}")
            continue

    return reviews


async def get_total_pages(page: Page) -> int:
    """Try to find the total number of pages."""
    try:
        # Trustpilot pagination: last page button or page count text
        last = page.locator('a[name="pagination-button-last"], nav[aria-label*="pagination"] a:last-child')
        if await last.count() > 0:
            href = await last.get_attribute('href') or ''
            if 'page=' in href:
                return int(href.split('page=')[-1].split('&')[0])
    except Exception:
        pass
    return 999  # fallback: scrape until empty


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
        await dismiss_consent(page)
        await random_delay(1, 2)

        max_pages = await get_total_pages(page)
        print(f"Max pages estimate: {max_pages}")

        page_num = 1
        consecutive_empty = 0

        while page_num <= max_pages:
            url = f"{TP_URL}?page={page_num}" if page_num > 1 else TP_URL
            if page_num > 1:
                await page.goto(url, wait_until='domcontentloaded', timeout=60000)
                await random_delay(1.5, 3)

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
                print(f"Page {page_num}: no new reviews ({consecutive_empty} consecutive empty)")
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
            headers={
                'Authorization': f'Bearer {SCRAPER_SECRET}',
                'Content-Type': 'application/json',
            },
            timeout=aiohttp.ClientTimeout(total=120),
        ) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise Exception(f"API error {resp.status}: {text}")
            return await resp.json()


async def main():
    print("Starting Trustpilot review scraper...")
    start = time.time()

    reviews = await scrape_reviews()
    elapsed = time.time() - start
    print(f"\nCollected {len(reviews)} unique reviews in {elapsed:.1f}s")

    if not reviews:
        print("No reviews found. Exiting.")
        return

    print("Sample:")
    for r in reviews[:3]:
        preview = r['review_text'][:60] if r['review_text'] else '(no text)'
        print(f"  [{r['rating']}★] {r['reviewer_name']}: {preview}")

    try:
        result = await post_to_api(reviews)
        print(
            f"\nAPI result: new={result.get('new')}, "
            f"deleted={result.get('deleted')}, "
            f"total={result.get('total')}, "
            f"platform={result.get('platform')}"
        )
    except Exception as e:
        print(f"API call failed: {e}")
        raise


if __name__ == '__main__':
    asyncio.run(main())
