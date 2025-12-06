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

async def image_ocr(screenshot):
    reader = easyocr.Reader(['tr', 'en'])

    # 1. Read and Sort by Y (vertical position) first to group lines
    results = sorted(reader.readtext(screenshot), key=lambda r: r[0][0][1])

    rows = []
    for bbox, text, _ in results:
        # Get coordinates (Top-Left)
        top_left = bbox[0]
        x, y = top_left[0], top_left[1]
        
        # 2. Group by Row (Y proximity)
        # We store (x, text) tuples now, so we can sort them left-to-right later
        if not rows or abs(y - rows[-1][0]) > 10:
            rows.append([y, [(x, text)]])
        else:
            rows[-1][1].append((x, text))

    return rows
async def get_payment_type(page, name_surname, description, payment_amount):

    await human_type(page, "#txtaraadi", name_surname)

    await asyncio.sleep(random.uniform(0.8, 1.8))

    await page.keyboard.press("Enter")

    await asyncio.sleep(random.uniform(1.7, 3.7))

    await human_button_click(page, "a", has_text=name_surname)

    await asyncio.sleep(random.uniform(1.7, 3.7))

    await human_button_click(page, "a:visible", has_text="ÖDEME")

    #TODO take a very specific cropped screenshot of the billing area, we will give to an OCR Algorithm
    await page.screenshot(path="screenshotv2.png")

    await asyncio.sleep(random.uniform(0.8, 1.8))

    await human_button_click(page, "a.btn.bg-orange", has_text="KURSİYER ARA")

    payments_info = image_ocr("screenshotv3.png")

    payment_types = []
    to_be_paid = []
    payment_owed = []
    payments_paid = []

    for row in payments_info:
        if len(row) < 2:
            continue
        if "ÖDEDİ" in row:
            payments_paid.append(row[1])
        else: 
            to_be_paid.append(row[-1])
            payment_owed.append(row[1])

    #SET KURALLAR:
    if payment_amount == 1200:
        if "YAZILI SINAV HARCI" in payment_owed:
            payment_types.append(["YAZILI SINAV HARCI", "BORC VAR"])
            return payment_types
        else: 
            payment_types.append(["YAZILI SINAV HARCI", "BORC YOK"])
            return payment_types
    if payment_amount == 1600:
        if "UYGULAMA SINAV HARCI" in payment_owed:
            payment_types.append(["UYGULAMA SINAV HARCI", "BORC VAR"])
            return payment_types
        else: 
            payment_types.append(["UYGULAMA SINAV HARCI", "BORC YOK"])
            return payment_types
    if payment_amount == 900:
        if "YAZILI SINAV HARCI" in payment_owed:
            payment_types.append(["YAZILI SINAV HARCI", "BORC VAR"])
            return payment_types
        else: 
            payment_types.append(["YAZILI SINAV HARCI", "BORC YOK"])
            return payment_types
    if payment_amount == 1350:
        if "UYGULAMA SINAV HARCI" in payment_owed:
            payment_types.append(["UYGULAMA SINAV HARCI", "BORC VAR"])
            return payment_types
        else: 
            payment_types.append(["UYGULAMA SINAV HARCI", "BORC YOK"])
            return payment_types
    
    if payment_amount == 4000 and "BAŞARISIZ ADAY EĞİTİMİ" in payment_owed:
        payment_types.append(["BAŞARISIZ ADAY EĞİTİMİ", "BORC VAR"])
        return payment_types

    if payment_amount == 4000 and "ÖZEL DERS" in payment_owed:
        payment_types.append(["ÖZEL DERS", "BORC VAR"])
        return payment_types

    payment_copy = payment_amount

    if payment_amount == 2000 and "BELGE ÜCRETİ" in payment_owed:
        payment_types.append(["BELGE ÜCRETİ", "BORC VAR"])
        payment_types.append(["TAKSİT", "BORC VAR"])
        return payment_types

    if payment_copy > 1600:
        if (payment_copy - 1600)%500 == 0 and payment_copy - 1600 != 4000:
            if "UYG. SNV. HARCI" in payment_owed and "YZL. SNV. HARCI" in payments_paid:
                payment_types.append(["UYGULAMA SINAV HARCI", "BORC VAR"])
                payment_types.append(["TAKSİT", "BORC VAR"])
            elif "YZL. SNV. HARCI" in payment_owed:
                payment_types.append(["YAZILI SINAV HARCI", "BORC YOK"])
                payment_types.append(["TAKSİT", "BORC VAR"])
        elif (payment_copy - 1600)%500 == 0 and payment_copy - 1600 == 4000:
            if "UYG. SNV. HARCI" in payment_owed and "YZL. SNV. HARCI" in payments_paid:
                payment_types.append(["UYGULAMA SINAV HARCI", "BORC VAR"])
                payment_types.append(["DORTBIN", "FLAG: 4000"])
            elif "YZL. SNV. HARCI" in payment_owed:
                payment_types.append(["UYGULAMA SINAV HARCI", "BORC YOK"])
                payment_types.append(["DORTBIN", "FLAG: 4000"])
        if (payment_copy - 1200)%500 == 0 and payment_copy - 1200 != 4000:
            if "YZL. SNV. HARCI" in payment_owed:
                payment_types.append(["YAZILI SINAV HARCI", "BORC VAR"])
                payment_types.append(["TAKSİT", "BORC VAR"])
            else:
                payment_types.append(["YAZILI SINAV HARCI", "BORC YOK"])
                payment_types.append(["TAKSİT", "BORC VAR"])
        elif (payment_copy - 1200)%500 == 0 and payment_copy - 1200 == 4000:
            if "YZL. SNV. HARCI" in payment_owed:
                payment_types.append(["YAZILI SINAV HARCI", "BORC VAR"])
                payment_types.append(["DORTBIN", "FLAG: 4000"])
            else:
                payment_types.append(["YAZILI SINAV HARCI", "BORC YOK"])
                payment_types.append(["DORTBIN", "FLAG: 4000"])

    return payment_types
