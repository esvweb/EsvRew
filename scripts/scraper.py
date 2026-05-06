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
MAPS_URL = os.environ.get(
    "GOOGLE_MAPS_URL", "https://maps.app.goo.gl/4nwAXYF4s1iUMhYMA"
)


def make_review_id(name: str, rating: int, text: str) -> str:
    raw = f"{name}|{rating}|{text[:80]}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


async def random_delay(min_s=1.5, max_s=3.0):
    await asyncio.sleep(random.uniform(min_s, max_s))


async def dismiss_consent(page: Page):
    for sel in [
        'button[aria-label*="Reddet"]',
        'button[aria-label*="Reject"]',
        'button[aria-label*="Accept all"]',
        'button[aria-label*="Tümünü kabul"]',
        '#L2AGLb',
        'form[action*="consent"] button:last-child',
        'form[action*="consent"] button:first-child',
    ]:
        try:
            btn = page.locator(sel).first
            if await btn.is_visible(timeout=1500):
                await btn.click()
                await asyncio.sleep(1.5)
                print("Dismissed consent popup")
                return
        except Exception:
            pass


async def go_to_reviews_tab(page: Page):
    for sel in [
        'button[aria-label*="Yorumlar"]',
        'button[aria-label*="Reviews"]',
        '[role="tab"]:nth-child(2)',
        'button[data-tab-index="1"]',
    ]:
        try:
            tab = page.locator(sel).first
            if await tab.is_visible(timeout=2000):
                await tab.click()
                await asyncio.sleep(2)
                print("Clicked reviews tab")
                return
        except Exception:
            pass


async def find_scroll_container(page: Page):
    candidates = [
        'div[aria-label*="Yorumlar"][role="main"]',
        'div[aria-label*="Reviews"][role="main"]',
        'div.m6QErb.DxyBCb',
        'div.m6QErb[data-tab-index="1"]',
        'div.m6QErb',
        'div[role="feed"]',
    ]
    for sel in candidates:
        try:
            el = page.locator(sel).first
            if await el.is_visible(timeout=1000):
                count = await el.evaluate("el => el.scrollHeight")
                if count > 100:
                    return el
        except Exception:
            pass
    return None


async def scroll_all_reviews(page: Page) -> int:
    container = await find_scroll_container(page)
    last_count = 0
    no_change = 0
    max_scrolls = 300

    for i in range(max_scrolls):
        # Scroll the container or the page
        if container:
            try:
                await container.evaluate("el => { el.scrollTop += el.clientHeight * 0.8; }")
            except Exception:
                await page.keyboard.press("End")
        else:
            await page.keyboard.press("End")

        await random_delay(1.5, 2.5)

        # Count visible review cards
        count = await page.locator(
            'div.jftiEf, div[data-review-id], div[jscontroller="MZnM8e"]'
        ).count()

        if count != last_count:
            no_change = 0
            last_count = count
            print(f"Scroll {i + 1}: {count} reviews loaded")
        else:
            no_change += 1
            if no_change >= 6:
                print(f"No new reviews after scroll {i + 1}. Done.")
                break

    return last_count


async def expand_review_texts(page: Page):
    for sel in [
        'button.w8nwRe',
        'button[aria-label*="Daha fazla"]',
        'button[aria-label*="See more"]',
        'button[jsaction*="pane.review.expandReview"]',
    ]:
        btns = page.locator(sel)
        count = await btns.count()
        for i in range(min(count, 1000)):
            try:
                btn = btns.nth(i)
                if await btn.is_visible(timeout=200):
                    await btn.click()
                    await asyncio.sleep(0.15)
            except Exception:
                pass


async def extract_reviews(page: Page) -> list[dict]:
    reviews = []
    seen_ids: set[str] = set()

    # Try multiple selectors for review containers
    for container_sel in [
        'div.jftiEf',
        'div[data-review-id]',
        'div[jscontroller="MZnM8e"]',
    ]:
        elements = page.locator(container_sel)
        total = await elements.count()
        if total == 0:
            continue

        print(f"Extracting with selector '{container_sel}': {total} elements")

        for i in range(total):
            try:
                el = elements.nth(i)

                # Reviewer name
                name = "Anonim"
                for name_sel in [
                    'div.d4r55',
                    'button[data-tab-index="-1"] div.d4r55',
                    '.x3AX1-LfntMc-header-title-ij8cu',
                    'span[class*="d4r55"]',
                    'div[class*="fontHeadlineSmall"]',
                ]:
                    try:
                        n = el.locator(name_sel).first
                        if await n.count() > 0:
                            txt = (await n.inner_text()).strip()
                            if txt:
                                name = txt
                                break
                    except Exception:
                        pass

                # Star rating from aria-label
                rating = 5
                for star_sel in [
                    'span[role="img"][aria-label]',
                    'span.kvMYJc',
                    'div.DU9Pgb span[role="img"]',
                ]:
                    try:
                        s = el.locator(star_sel).first
                        if await s.count() > 0:
                            label = (await s.get_attribute("aria-label")) or ""
                            for n in range(1, 6):
                                if str(n) in label[:3]:
                                    rating = n
                                    break
                            break
                    except Exception:
                        pass

                # Review text
                text = ""
                for text_sel in [
                    'span.wiI7pd',
                    'div[data-expandable-section] span',
                    'span[jsname="bN97Pc"]',
                    'div.Jtu6Td span',
                ]:
                    try:
                        t = el.locator(text_sel).first
                        if await t.count() > 0:
                            txt = (await t.inner_text()).strip()
                            if txt:
                                text = txt
                                break
                    except Exception:
                        pass

                rid = make_review_id(name, rating, text)
                if rid in seen_ids:
                    continue
                seen_ids.add(rid)

                reviews.append({
                    "review_id": rid,
                    "reviewer_name": name,
                    "rating": rating,
                    "review_text": text,
                })

            except Exception as e:
                print(f"  Error on review {i}: {e}")
                continue

        if reviews:
            break  # found reviews with this selector, stop trying others

    return reviews


async def scrape_reviews() -> list[dict]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            locale="tr-TR",
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()

        print(f"Navigating to: {MAPS_URL}")
        await page.goto(MAPS_URL, wait_until="domcontentloaded", timeout=90000)
        await random_delay(3, 5)

        await dismiss_consent(page)
        await random_delay(1, 2)

        await go_to_reviews_tab(page)
        await random_delay(2, 3)

        print("Scrolling to load all reviews...")
        await scroll_all_reviews(page)

        print("Expanding truncated review texts...")
        await expand_review_texts(page)
        await asyncio.sleep(1)

        reviews = await extract_reviews(page)
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
    print(f"\nCollected {len(reviews)} unique reviews in {time.time() - start:.1f}s")

    if not reviews:
        print("No reviews found. Exiting.")
        return

    # Show sample
    for r in reviews[:3]:
        print(f"  [{r['rating']}★] {r['reviewer_name']}: {r['review_text'][:60]}")

    try:
        result = await post_to_api(reviews)
        print(
            f"\nAPI result: new={result.get('new')}, "
            f"deleted={result.get('deleted')}, "
            f"total={result.get('total')}"
        )
    except Exception as e:
        print(f"API call failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
