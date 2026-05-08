import asyncio
from playwright.async_api import async_playwright

URL = "https://www.trustpilot.com/review/esvitaclinic.com"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            locale="en-US", viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
        )
        page = await context.new_page()
        await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(3)

        try:
            btn = page.locator('#onetrust-accept-btn-handler').first
            if await btn.is_visible(timeout=2000):
                await btn.click()
                await asyncio.sleep(1)
        except Exception:
            pass

        await asyncio.sleep(2)

        # Get the parent article/section that contains the full review
        # Try article elements
        articles = page.locator('article')
        count = await articles.count()
        print(f"Articles found: {count}")

        if count > 0:
            # Get second article (first might be a summary)
            html = await articles.nth(1).inner_html()
            print(f"\nArticle[1] HTML:\n{html[:3000]}")

        # Test specific data-attributes for rating
        rating_els = page.locator('[data-service-review-rating]')
        rc = await rating_els.count()
        print(f"\n[data-service-review-rating] count: {rc}")
        if rc > 0:
            val = await rating_els.nth(0).get_attribute('data-service-review-rating')
            print(f"  First rating value: {val}")

        # Test star image
        stars = page.locator('img[alt*="star"], img[alt*="Star"], img[alt*="Rated"]')
        sc = await stars.count()
        print(f"Star images found: {sc}")
        if sc > 0:
            alt = await stars.nth(0).get_attribute('alt')
            print(f"  First star alt: {alt}")

        # Test review text
        for sel in [
            '[data-service-review-text-typography]',
            'p[class*="typography_body"]',
            'p[data-cpl]',
        ]:
            c = await page.locator(sel).count()
            if c > 0:
                t = (await page.locator(sel).nth(0).inner_text()).strip()
                print(f"\n{sel} [{c}]: {t[:100]}")

        await browser.close()

asyncio.run(main())
