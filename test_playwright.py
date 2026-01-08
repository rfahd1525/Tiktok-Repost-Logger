"""
Simple Playwright test to diagnose browser issues.
"""
import asyncio
from playwright.async_api import async_playwright

async def test_playwright():
    """Test basic Playwright functionality."""
    print("Starting Playwright test...")

    try:
        print("1. Starting playwright...")
        playwright = await async_playwright().start()
        print("    Playwright started")

        print("2. Launching browser (Firefox)...")
        browser = await playwright.firefox.launch(headless=False)
        print("    Browser launched")

        print("3. Creating context...")
        context = await browser.new_context()
        print("    Context created")

        print("4. Creating page...")
        page = await context.new_page()
        print("    Page created")

        print("5. Navigating to example.com...")
        await page.goto('https://example.com')
        print("    Navigation successful")

        print("6. Getting page title...")
        title = await page.title()
        print(f"    Page title: {title}")

        print("\n7. Waiting 5 seconds...")
        await asyncio.sleep(5)

        print("8. Closing browser...")
        await page.close()
        await context.close()
        await browser.close()
        await playwright.stop()
        print("    Browser closed")

        print("\n All tests passed! Playwright is working correctly.")
        return True

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    result = asyncio.run(test_playwright())
    exit(0 if result else 1)
