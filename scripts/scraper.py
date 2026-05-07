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
MAPS_URL = os.environ.get("GOOGLE_MAPS_URL", "https://maps.app.goo.gl/4nwAXYF4s1iUMhYMA")


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
        'button[data-tab-index="1"]',
        '[role="tab"]:nth-child(2)',
    ]:
        try:
            tab = page.locator(sel).first
            if await tab.is_visible(timeout=2000):
                await tab.click()
                await asyncio.sleep(2.5)
                print("Clicked reviews tab")
                return
        except Exception:
            pass


async def find_scroll_container(page: Page):
    for sel in [
        'div.m6QErb.DxyBCb',
        'div.m6QErb[data-tab-index="1"]',
        'div[aria-label*="Yorumlar"][role="main"]',
        'div[aria-label*="Reviews"][role="main"]',
        'div.m6QErb',
        'div[role="feed"]',
    ]:
        try:
            el = page.locator(sel).first
            if await el.is_visible(timeout=800):
                h = await el.evaluate("el => el.scrollHeight")
                if h and h > 200:
                    return el
        except Exception:
            pass
    return None


async def extract_visible_reviews(page: Page) -> list[dict]:
    """Extract all currently visible review cards from the DOM."""
    reviews = []

    elements = page.locator('div.jftiEf')
    total = await elements.count()
    if total == 0:
        elements = page.locator('div[data-review-id]')
        total = await elements.count()
    if total == 0:
        return reviews

    for i in range(total):
        try:
            el = elements.nth(i)

            # Reviewer name
            name = "Anonim"
            for sel in ['div.d4r55', 'span.d4r55', 'div[class*="fontHeadlineSmall"]']:
                try:
                    n = el.locator(sel).first
                    if await n.count() > 0:
                        t = (await n.inner_text()).strip()
                        if t:
                            name = t
                            break
                except Exception:
                    pass

            # Star rating
            rating = 5
            for sel in ['span[role="img"][aria-label]', 'span.kvMYJc']:
                try:
                    s = el.locator(sel).first
                    if await s.count() > 0:
                        label = (await s.get_attribute("aria-label")) or ""
                        for n in range(1, 6):
                            if str(n) in label[:4]:
                                rating = n
                                break
                        break
                except Exception:
                    pass

            # Click "See original" if review was auto-translated
            for orig_sel in [
                'button[aria-label*="See original"]',
                'button[aria-label*="Orijinali gör"]',
                'button.kyuRq',
            ]:
                try:
                    orig_btn = el.locator(orig_sel).first
                    if await orig_btn.count() > 0 and await orig_btn.is_visible(timeout=200):
                        await orig_btn.click()
                        await asyncio.sleep(0.2)
                        break
                except Exception:
                    pass

            # Review text (empty string is fine — star-only reviews are valid)
            text = ""
            for sel in ['span.wiI7pd', 'span[jsname="bN97Pc"]', 'div.Jtu6Td span']:
                try:
                    t = el.locator(sel).first
                    if await t.count() > 0:
                        txt = (await t.inner_text()).strip()
                        if txt:
                            text = txt
                            break
                except Exception:
                    pass

            rid = make_review_id(name, rating, text)
            reviews.append({
                "review_id": rid,
                "reviewer_name": name,
                "rating": rating,
                "review_text": text,
            })

        except Exception as e:
            print(f"  Extraction error on card {i}: {e}")
            continue

    return reviews


async def expand_visible_texts(page: Page):
    """Click 'Daha fazla' buttons on currently visible reviews."""
    for sel in ['button.w8nwRe', 'button[aria-label*="Daha fazla"]', 'button[aria-label*="See more"]']:
        btns = page.locator(sel)
        count = await btns.count()
        for i in range(count):
            try:
                btn = btns.nth(i)
                if await btn.is_visible(timeout=150):
                    await btn.click()
                    await asyncio.sleep(0.1)
            except Exception:
                pass


async def scrape_reviews() -> list[dict]:
    all_reviews: dict[str, dict] = {}  # review_id → data (dedup across scrolls)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            locale="en-US",  # neutral locale — avoids auto-translation of reviews
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

        container = await find_scroll_container(page)
        if container:
            info = await container.evaluate(
                "el => ({sh: el.scrollHeight, ch: el.clientHeight, st: el.scrollTop})"
            )
            print(f"Scroll container: scrollHeight={info['sh']} clientHeight={info['ch']}")
        else:
            print("No scroll container found, using keyboard scroll")

        no_new_count = 0
        scroll_num = 0
        max_scrolls = 600
        SCROLL_PX = 800  # fixed pixel step — avoids tiny clientHeight issues

        while scroll_num < max_scrolls:
            scroll_num += 1

            # Extract currently visible reviews
            batch = await extract_visible_reviews(page)
            new_this_batch = 0
            for r in batch:
                if r["review_id"] not in all_reviews:
                    all_reviews[r["review_id"]] = r
                    new_this_batch += 1

            total_so_far = len(all_reviews)

            if new_this_batch > 0:
                no_new_count = 0
                print(f"Scroll {scroll_num}: +{new_this_batch} new → {total_so_far} total")
            else:
                no_new_count += 1
                if no_new_count == 4:
                    # Pause — Google Maps may still be loading the next AJAX batch
                    print(f"  Waiting for next batch to load... ({total_so_far} so far)")
                    await asyncio.sleep(4)
                if no_new_count >= 12:
                    print(f"No new reviews for 12 scrolls. Done at {total_so_far}.")
                    break

            # Scroll using fixed pixel amount on container AND page
            scrolled = False
            if container:
                try:
                    prev = await container.evaluate("el => el.scrollTop")
                    await container.evaluate(f"el => el.scrollTop += {SCROLL_PX}")
                    after = await container.evaluate("el => el.scrollTop")
                    if after > prev:
                        scrolled = True
                except Exception:
                    pass

            if not scrolled:
                # Fallback: scroll the page itself
                await page.evaluate(f"window.scrollBy(0, {SCROLL_PX})")

            await random_delay(0.8, 1.5)

        await browser.close()

    return list(all_reviews.values())


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
            timeout=aiohttp.ClientTimeout(total=120),
        ) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise Exception(f"API error {resp.status}: {text}")
            return await resp.json()


async def main():
    print("Starting Esvita review scraper...")
    start = time.time()

    reviews = await scrape_reviews()
    elapsed = time.time() - start
    print(f"\nCollected {len(reviews)} unique reviews in {elapsed:.1f}s")

    if not reviews:
        print("No reviews found. Exiting.")
        return

    print("Sample:")
    for r in reviews[:3]:
        text_preview = r["review_text"][:60] if r["review_text"] else "(yıldız yorumu)"
        print(f"  [{r['rating']}★] {r['reviewer_name']}: {text_preview}")

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
