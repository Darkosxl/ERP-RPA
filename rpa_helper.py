import asyncio
import random
import time
import os
import pandas as pd
import easyocr
from ollama import chat
from ollama import ChatResponse

from playwright.async_api import async_playwright
from playwright_stealth import Stealth
import dotenv

async def human_option_select(page, dropdown_selector, option_text):
    dropDownList = page.locator(dropdown_selector)
    await dropDownList.select_option(option_text)
    
async def human_button_click(page, selector=None, has_text=None ,exact_text=None, check_exists=False):
    if exact_text:
        element = page.get_by_text(exact_text, exact=False)
    elif has_text:
        element = page.locator(selector, has_text=has_text).first
    elif selector:
        element = page.locator(selector).first
    else:
        console.log("No selector provided")
        return
    
    if check_exists:
        try:
            # Wait up to 3000ms (3 seconds) for the element to appear
            await element.wait_for(state="visible", timeout=3000)
        except:
            # If it times out, print message and STOP function here
            print(f"The name '{exact_text or selector}' is not there.")
            return
            
    await element.hover()
    
    await asyncio.sleep(random.uniform(0.3, 0.7))
    
    await element.click()

async def human_type(page, selector, text):
    element = page.locator(selector).first

    await element.hover()
    await asyncio.sleep(random.uniform(0.2,0.5))

    await element.click()

    # Clear the field by selecting all and deleting (human-like behavior)
    await page.keyboard.press("Control+a")
    await asyncio.sleep(random.uniform(0.1, 0.2))

    await element.type(text, delay=random.randint(50,150))

async def get_human_name(description):
    response: ChatResponse = chat(model='gemma3', messages=[
  {
    'role': 'user',
    'content': 'output the persons name and surname in all upper case with turkish characters exactly as written' + description + ' if there is no name output ERROR: 404',
  },
])
    
    return response['message']['content']


async def get_payment_type(page, name_surname, description, payment_amount):

    await human_type(page, "#txtaraadi", name_surname)

    await asyncio.sleep(random.uniform(0.8, 1.8))

    await page.keyboard.press("Enter")

    await asyncio.sleep(random.uniform(1.7, 3.7))

    await human_button_click(page, "a", has_text=name_surname)

    await asyncio.sleep(random.uniform(1.7, 3.7))

    await human_button_click(page, "a:visible", has_text="ÖDEME")

    #TODO take a very specific cropped screenshot of the billing area, we will give to an OCR Algorithm
    await page.screenshot(path="screenshot.png")

    await asyncio.sleep(random.uniform(0.8, 1.8))

    await human_button_click(page, "a.btn.bg-orange", has_text="KURSİYER ARA")

    #1600 uygulama sinav harci
    #1200 yazili sinav
    #1000 saglik belge ucreti
    #2000 ozel ders fiyatlandirma, genelde 2 ders aliniyor,
    #basarisiz aday egitimi 4000
    #taksit 
    


    return response['message']['content']


reader = easyocr.Reader(['tr', 'en']) # 'tr' for Turkish support
result = reader.readtext('screenshot.png', detail=0)
print(result)