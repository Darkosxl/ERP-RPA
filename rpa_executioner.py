import asyncio
import time
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def RPAexecutioner_Login():
    async with Stealth().use_async(async_playwright()) as playwright:
        chromium = playwright.chromium
        browser = await chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        response = await page.goto("https://kurs.goldennet.com.tr/giris.php")
        is_bot = await page.evaluate("navigator.webdriver")
        print(f"Am I a bot? {is_bot}")
        headers = response.headers
        print("Server:", headers.get("server"))
        print("X-Powered-By:", headers.get("x-powered-by"))
        await page.screenshot(path="screenshot.png")
        await browser.close()
    
asyncio.run(RPAexecutioner())