import asyncio
import random
import time
import os
import pandas as pd

from ollama import chat
from ollama import ChatResponse
from rpa_helper import human_option_select, human_button_click, human_type, get_human_name, get_payment_type

from playwright.async_api import async_playwright
from playwright_stealth import Stealth
import dotenv

dotenv.load_dotenv()



async def golden_PaymentPaid(page, name_surname, collection_type, amount):

    await human_type(page, "#txtaraadi", name_surname)

    await asyncio.sleep(random.uniform(0.8, 1.8))

    await page.keyboard.press("Enter")

    await asyncio.sleep(random.uniform(1.7, 3.7))

    await human_button_click(page, "a", has_text=name_surname)

    await asyncio.sleep(random.uniform(1.7, 3.7))
    
    await human_button_click(page, "a:visible", has_text="ÖDEME")

    await asyncio.sleep(random.uniform(0.8, 1.8))
    
    await human_button_click(page, "#btnyeniodeme")
    
    await asyncio.sleep(random.uniform(1.1, 3.7))
    
    await human_option_select(page, "#yenitahsilat_borctipi", collection_type)
    
    await asyncio.sleep(random.uniform(0.9, 3.1))
    
    await human_type(page, "#yenitahsilat_tutar", str(amount))
    
    await asyncio.sleep(random.uniform(0.7, 2.1))
    
    await human_button_click(page, "button", has_text="ÖDETTİR")
    
    await asyncio.sleep(random.uniform(1.6, 3.1))
    
    is_bot = await page.evaluate("navigator.webdriver")

async def golden_PaymentOwed(page, name_surname, collection_type, amount):
    
    await human_type(page, "#txtaraadi", name_surname)

    await asyncio.sleep(random.uniform(0.8, 1.8))

    await page.keyboard.press("Enter")

    await asyncio.sleep(random.uniform(1.7, 3.7))

    await human_button_click(page, "a", has_text=name_surname)

    await asyncio.sleep(random.uniform(1.7, 3.7))

    await human_button_click(page, "a:visible", has_text="ÖDEME")

    await asyncio.sleep(random.uniform(0.8, 1.8))
    
    await human_button_click(page, "#btnyeniborc")
    
    await asyncio.sleep(random.uniform(1.1, 3.7))
    
    await human_option_select(page, "#yeniborc_borctipi", collection_type)
    
    await asyncio.sleep(random.uniform(0.9, 3.1))
    
    await human_type(page, "#yeniborc_tutar", str(amount))
    
    await asyncio.sleep(random.uniform(0.7, 2.1))
    
    await human_button_click(page, "button.btn-success:visible", has_text="KAYDET")
    
    await asyncio.sleep(random.uniform(1.6, 3.1))

async def RPAexecutioner_readfile(filename, sheetname):
    dfs = pd.read_excel(filename, sheet_name=sheetname,header=14)
    people = dfs["Açıklama"]
    payments = dfs["Tutar"]
    tag = dfs["Etiket"]

    return [people, payments, tag]


async def RPAexecutioner_GoldenProcessStart(filename, sheetname):
    async with Stealth().use_async(async_playwright()) as playwright:
        chromium = playwright.chromium
        
        browser = await chromium.launch(headless=False)
        
        context = await browser.new_context()
        
        page = await context.new_page()
        
        response = await page.goto("https://kurs.goldennet.com.tr/giris.php")
        
        await human_type(page, "#kurumkodu", os.getenv("institution_code"))
        await asyncio.sleep(random.uniform(0.7, 1.9))
        
        await human_type(page, "#kullaniciadi", os.getenv("login"))
        await asyncio.sleep(random.uniform(1.1, 3.2))
        
        await human_type(page, "#kullanicisifresi", os.getenv("password"))
        await asyncio.sleep(random.uniform(0.9, 3.1))
        
        await human_button_click(page, "#btngiris")
        
        await asyncio.sleep(random.uniform(1.5, 4.1))

        await human_button_click(page, "a.btn.bg-orange", has_text="KURSİYER ARA")
        
        await asyncio.sleep(random.uniform(1.7, 3.7))

        

        payment_information = RPAexecutioner_readfile(filename, sheetname)

        for i in range(len(payment_information[0])):
            
            if payment_information[1][i].contains("-"):
                console.log(payment_information[1][i] +" Cost, not a received payment")
                continue
            if payment_information[2][i] != "Para Transferi":
                console.log("Not a payment transfer")
                continue

            name_surname = get_human_name(payment_information[0][i])
            if name_surname == "ERROR: 404":
                console.log("Error: name not found" + payment_information[0][i] + "was not attributed to any name")
                continue
            else:
                console.log("name found" + name_surname)

            payment_type = get_payment_type(page, name_surname,payment_information[0][i],payment_information[1][i])

        
        
        
        is_bot = await page.evaluate("navigator.webdriver")
        
        print(f"Am I a bot? {is_bot}")
                
        
        await browser.close()

        


    
#asyncio.run(RPAexecutioner_PaymentOwed("Onur Çelik YZ Test", "TAKSİT", 6000))



print(asyncio.run(get_payment_type("FAST2923973105-ESRANUR GÖNEN-KURS ÜCRETİ +SINAV HARCI")))

