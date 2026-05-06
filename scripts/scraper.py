import asyncio
import hashlib
import json
import os
import random
import time
from datetime import date

import aiohttp
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

APP_URL = os.environ.get("NEXT_PUBLIC_APP_URL", "http://localhost:3000")
SCRAPER_SECRET = os.environ.get("SCRAPER_SECRET", "")
MAPS_URL = os.environ.get(
    "GOOGLE_MAPS_URL", "https://maps.app.goo.gl/4nwAXYF4s1iUMhYMA"
)


def make_review_id(name: str, rating: int, text: str) -> str:
    raw = f"{name}{rating}{text[:50]}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


async def random_delay(min_s=1.5, max_s=3.0):
    await asyncio.sleep(random.uniform(min_s, max_s))


async def scrape_reviews() -> list[dict]:
    reviews = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            locale="tr-TR",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()

        print(f"Navigating to: {MAPS_URL}")
        await page.goto(MAPS_URL, wait_until="load", timeout=90000)
        await random_delay(2, 4)

        # Handle cookie consent popup
        consent_selectors = [
            'button[aria-label*="Reject"]',
            'button[aria-label*="Reddet"]',
            'button[aria-label*="Accept"]',
            'button[aria-label*="Kabul"]',
            'form[action*="consent"] button',
            '#L2AGLb',
            '.tHlp8d',
        ]
        for sel in consent_selectors:
            try:
                btn = page.locator(sel).first
                if await btn.is_visible(timeout=2000):
                    await btn.click()
                    await random_delay(1, 2)
                    break
            except Exception:
                pass

        # Click on "Reviews" tab
        review_tab_selectors = [
            'button[aria-label*="Yorumlar"]',
            'button[aria-label*="Reviews"]',
            '[data-tab-index="1"]',
        ]
        for sel in review_tab_selectors:
            try:
                tab = page.locator(sel).first
                if await tab.is_visible(timeout=3000):
                    await tab.click()
                    await random_delay(2, 3)
                    break
            except Exception:
                pass

        # Scroll to load all reviews
        review_container_sel = 'div[data-review-id], div[jscontroller*="review"], div.jftiEf'
        scrollable = page.locator(
            'div[aria-label*="Yorumlar"], div[aria-label*="Reviews"], div.m6QErb'
        ).first

        max_scrolls = 200
        last_count = 0
        no_change_count = 0

        for i in range(max_scrolls):
            try:
                await scrollable.evaluate("el => el.scrollTop += el.clientHeight")
            except Exception:
                await page.keyboard.press("End")

            await random_delay(1.5, 3.0)

            # Click "More reviews" / "Daha fazla yorum" buttons
            more_btns = [
                'button[aria-label*="Daha fazla yorum"]',
                'button[aria-label*="More reviews"]',
                'button.HHrUdb',
            ]
            for sel in more_btns:
                try:
                    btn = page.locator(sel).first
                    if await btn.is_visible(timeout=500):
                        await btn.click()
                        await random_delay(1, 2)
                except Exception:
                    pass

            current_count = await page.locator(
                'div[data-review-id], div[jsaction*="review"], div.jftiEf'
            ).count()

            if current_count == last_count:
                no_change_count += 1
                if no_change_count >= 5:
                    print(f"No new reviews after {i + 1} scrolls. Stopping.")
                    break
            else:
                no_change_count = 0
                last_count = current_count
                print(f"Scroll {i + 1}: {current_count} reviews loaded")

        # Expand "Daha fazla" (More) in review texts
        expand_btns = page.locator('button[aria-label*="Daha fazla"], button.w8nwRe, button[jsaction*="pane.review.expandReview"]')
        count = await expand_btns.count()
        for i in range(min(count, 500)):
            try:
                btn = expand_btns.nth(i)
                if await btn.is_visible(timeout=300):
                    await btn.click()
                    await asyncio.sleep(0.2)
            except Exception:
                pass

        # Extract reviews
        review_elements = page.locator('div[data-review-id]')
        total = await review_elements.count()
        print(f"Extracting {total} reviews...")

        for i in range(total):
            try:
                el = review_elements.nth(i)

                name_el = el.locator('[class*="d4r55"], .d4r55, [class*="NRGaub"], span.x3AX1-LfntMc-header-title-ij8cu').first
                name = (await name_el.inner_text()).strip() if await name_el.count() > 0 else "Anonim"

                star_el = el.locator('[aria-label*="yıldız"], [aria-label*="star"], span[role="img"]').first
                rating = 5
                if await star_el.count() > 0:
                    label = await star_el.get_attribute("aria-label") or ""
                    for n in ["1", "2", "3", "4", "5"]:
                        if label.startswith(n):
                            rating = int(n)
                            break

                text_el = el.locator('span.wiI7pd, [class*="review-full-text"], [jsname="bN97Pc"]').first
                text = (await text_el.inner_text()).strip() if await text_el.count() > 0 else ""

                rid = make_review_id(name, rating, text)
                reviews.append({
                    "review_id": rid,
                    "reviewer_name": name,
                    "rating": rating,
                    "review_text": text,
                })
            except Exception as e:
                print(f"Error extracting review {i}: {e}")
                continue

        await browser.close()

    return reviews


async def post_to_api(reviews: list[dict]) -> dict:
    today = date.today().isoformat()
    payload = {"reviews": reviews, "snapshot_date": today}

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{APP_URL}/api/scraper",
            json=payload,
            headers={
                "Authorization": f"Bearer {SCRAPER_SECRET}",
                "Content-Type": "application/json",
            },
            timeout=aiohttp.ClientTimeout(total=60),
        ) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise Exception(f"API error {resp.status}: {text}")
            return await resp.json()


async def main():
    print("Starting Esvita review scraper...")
    start = time.time()

    reviews = await scrape_reviews()
    print(f"Collected {len(reviews)} reviews in {time.time() - start:.1f}s")

    if not reviews:
        print("No reviews found. Exiting.")
        return

    try:
        result = await post_to_api(reviews)
        print(
            f"API result: new={result.get('new')}, "
            f"deleted={result.get('deleted')}, "
            f"total={result.get('total')}"
        )
    except Exception as e:
        print(f"API call failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
